"""Async run execution: idempotent by call_id, append-only JSONL logs, prompt
dedup table, budget kill switch, one repair attempt for parse failures."""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .budget import BudgetGuard, Ledger, deepseek_off_peak, price_for
from .client import OpenRouterClient, RefusalError, TransportFailure
from .config import (
    MATERIALS_DIR,
    RUNS_DIR,
    load_experiment,
    load_family_cues,
    load_jd_variants,
    load_models,
    load_names,
)
from .materials.perturb import render_resume
from .parse import parse_response
from .plan import PROMPT_VERSION

from jinja2 import Environment, StrictUndefined

ENV = Environment(undefined=StrictUndefined, trim_blocks=False, lstrip_blocks=False)


def _load_jd(occ: str, variant: str) -> str:
    jd = json.loads((MATERIALS_DIR / "job_descriptions" / f"{occ}.json").read_text())["jd"]
    add = load_jd_variants().get(variant)
    if add:
        jd = jd + "\n\n" + add
    return jd


def _load_resumes(occ: str) -> dict[str, dict]:
    path = MATERIALS_DIR / "base_resumes" / f"{occ}.json"
    if not path.exists():
        raise FileNotFoundError(f"materials missing: {path} (run `audit materials build`)")
    resumes = json.loads(path.read_text())
    return {r["resume_id"]: r for r in resumes}


def _tpl(name: str):
    tpl = ENV.from_string((Path("prompts") / f"{name}.j2").read_text())
    return tpl


def build_prompt(row: dict) -> tuple[str, str]:
    """Returns (prompt_text, system_prompt). system=None (consumer default)."""
    exp = row["experiment"]
    ctx = row.get("render_ctx") or {}
    if isinstance(ctx, str):
        ctx = json.loads(ctx)
    jd = _load_jd(row["occupation_id"], row.get("jd_variant") or "base")
    resumes = _load_resumes(row["occupation_id"])
    para = int(row["paraphrase_id"])
    if exp in ("e1", "e4"):
        cand = render_resume(
            resumes[ctx["resume_id"]], ctx["gender"], int(ctx["name_idx"]), ctx["family_code"],
            cue_level=ctx.get("cue_level") or "name",
            initial_idx=ctx.get("initial_idx"),
        )
        text = _tpl("e1_scoring").render(jd=jd, candidate=cand, paraphrase_id=para)
    elif exp == "e2":
        names = load_names()
        if "woman_resume" in ctx:  # direct gender contrast: P(woman chosen)
            lvl = ctx.get("cue_level") or "name"
            woman = render_resume(
                resumes[ctx["woman_resume"]], "female", int(ctx["woman_name_idx"]),
                ctx["woman_family"], cue_level=lvl,
                initial_idx=ctx.get("woman_initial_idx"),
            )
            man = render_resume(
                resumes[ctx["man_resume"]], "male", int(ctx["man_name_idx"]),
                ctx["man_family"], cue_level=lvl,
                initial_idx=ctx.get("man_initial_idx"),
            )
            a, b = (woman, man) if ctx["woman_position"] == "A" else (man, woman)
        else:
            lvl = ctx.get("cue_level") or "name"
            child = render_resume(
                resumes[ctx["childless_resume"]], ctx["gender"], int(ctx["childless_name_idx"]),
                "none", cue_level=lvl, initial_idx=ctx.get("childless_initial_idx"),
            )
            parent = render_resume(
                resumes[ctx["parent_resume"]], ctx["gender"], int(ctx["parent_name_idx"]),
                ctx["contrast"], cue_level=lvl, initial_idx=ctx.get("parent_initial_idx"),
            )
            a, b = (child, parent) if ctx["childless_position"] == "A" else (parent, child)
        text = _tpl("e2_paired").render(jd=jd, candidate_a=a, candidate_b=b, paraphrase_id=para)
    elif exp == "e3":
        lvl = ctx.get("cue_level") or "name"
        blocks = []
        for c in ctx["pool"]:
            blocks.append(
                f"[{c['label']}]\n" + render_resume(
                    resumes[c["resume_id"]], c["gender"], int(c["name_idx"]), c["family_code"],
                    cue_level=lvl, initial_idx=c.get("initial_idx"),
                )
            )
        text = _tpl("e3_ranking").render(jd=jd, pool="\n\n".join(blocks), paraphrase_id=para)
    elif exp == "manip":
        cand = render_resume(
            resumes[ctx["resume_id"]], ctx["gender"] or "female", int(ctx["name_idx"]),
            "none", cue_level=ctx.get("cue_level") or "name",
            initial_idx=ctx.get("initial_idx"),
        )
        text = _tpl("manip_check").render(jd=jd, candidate=cand)
    else:
        raise ValueError(f"unknown experiment {exp}")
    return text, None


def prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class PromptStore:
    """prompt_text_hash -> text, deduped across runs (runs/prompts.parquet)."""

    def __init__(self):
        self.path = RUNS_DIR / "prompts.parquet"
        self.df = pd.read_parquet(self.path) if self.path.exists() else pd.DataFrame(
            {"prompt_text_hash": [], "prompt_text": []}
        )
        self._known = set(self.df["prompt_text_hash"])
        self._new: list[dict] = []

    def add(self, text: str) -> str:
        h = prompt_hash(text)
        if h not in self._known:
            self._known.add(h)
            self._new.append({"prompt_text_hash": h, "prompt_text": text})
        return h

    def flush(self) -> None:
        if not self._new:
            return
        add = pd.DataFrame(self._new).drop_duplicates("prompt_text_hash")
        self.df = (
            pd.concat([self.df, add]).drop_duplicates("prompt_text_hash").reset_index(drop=True)
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_parquet(self.path, index=False)
        self._new = []


def completed_call_ids(runs_dir: Path = RUNS_DIR) -> set[str]:
    """call_ids with a FINAL outcome (valid parse or refusal) — not retried."""
    done: set[str] = set()
    for f in runs_dir.glob("*/logs.jsonl"):
        for line in f.read_text().splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("parse_ok") or r.get("refusal_flag"):
                done.add(r["call_id"])
    return done


class RunResult:
    def __init__(self):
        self.n_ok = 0
        self.n_refusal = 0
        self.n_error = 0
        self.cost = 0.0


async def run_plan(
    plan_path: Path,
    model_key: str,
    run_id: str | None = None,
    dry_run: bool = False,
    max_calls: int | None = None,
    allow_reserve: bool = False,
    concurrency: int = 8,
    pricing: str | None = None,
) -> dict:
    """Execute (or dry-run) a call plan. Returns summary dict."""
    plan = pd.read_parquet(plan_path)
    plan = plan[plan["model_key"] == model_key].reset_index(drop=True)
    if plan.empty:
        raise SystemExit(f"plan has no rows for model {model_key}")

    models = load_models()
    mcfg = next(m for m in models.models if m.key == model_key)
    if not mcfg.verified:
        raise SystemExit(
            f"model {model_key} ({mcfg.slug}) is not verified against OpenRouter; "
            "verify slug + prices in config/models.yaml first"
        )

    budget = BudgetGuard()
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + f"-{Path(plan_path).stem}-{model_key}"
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "logs.jsonl"

    # pricing basis
    peak = (pricing == "peak") if pricing else None
    async with OpenRouterClient(os.environ["OPENROUTER_API_KEY"]) as client:
        live = None
        try:
            prices = await client.fetch_live_prices()
            live = client.live_price(mcfg)
        except Exception as e:  # noqa: BLE001
            print(f"[run] WARNING could not fetch live prices: {e}")
        if peak is None:
            peak = False if (mcfg.peak_hours_utc and deepseek_off_peak()) else True
            if pricing == "off-peak":
                peak = False
        pin, pout = price_for(mcfg, peak, live)

        # ---- pre-run estimate (uses est tokens from plan) ----
        est_in = plan["est_input_tokens"].sum()
        est_out = plan["est_output_tokens"].sum() * budget.cfg.estimate_safety_factor
        estimate = est_in * pin / 1e6 + est_out * pout / 1e6

        done = completed_call_ids() if not dry_run else set()
        pending = plan[~plan["call_id"].isin(done)].reset_index(drop=True)
        pending_estimate = estimate * (len(pending) / max(len(plan), 1))

        manifest = {
            "run_id": run_id,
            "plan": str(plan_path),
            "model": {"key": mcfg.key, "slug": mcfg.slug},
            "pricing": {"peak_assumed": peak, "input_per_mtok": pin, "output_per_mtok": pout,
                        "live": {"input": live[0], "output": live[1]} if live else None},
            "plan_calls": int(len(plan)),
            "already_done": int(len(plan) - len(pending)),
            "estimate_usd": round(estimate, 4),
            "pending_estimate_usd": round(pending_estimate, 4),
            "prompt_version": PROMPT_VERSION,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "dry_run": dry_run,
        }
        (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

        print(
            f"[run] {run_id}: {len(plan)} planned, {manifest['already_done']} done, "
            f"{len(pending)} pending | estimate(all) ${estimate:.2f} @ "
            f"{'peak' if peak else 'off-peak'} {pin:.3f}/{pout:.3f} per Mtok"
        )

        if dry_run:
            samples_dir = run_dir / "samples"
            samples_dir.mkdir(exist_ok=True)
            store = PromptStore()
            for exp in ["e1", "e2", "e3", "e4"]:
                sub = plan[plan["experiment"] == exp]
                if sub.empty:
                    continue
                for i, (_, r) in enumerate(sub.head(5).iterrows()):
                    text, _ = build_prompt(r)
                    (samples_dir / f"{exp}_{i}.txt").write_text(text)
                    store.add(text)
            store.flush()
            print(f"[run] dry-run complete: 5 sample prompts/experiment in {samples_dir}; ZERO API calls")
            return {"run_id": run_id, "dry_run": True, "estimate_usd": estimate}

        ok, msg = budget.check(pending_estimate, phase=plan["phase"].iloc[0], allow_reserve=allow_reserve)
        print(f"[budget] {msg}")
        if not ok:
            raise SystemExit(f"BUDGET GUARD REFUSED: {msg}")

        if max_calls:
            pending = pending.head(max_calls).reset_index(drop=True)
            print(f"[run] --max-calls: limiting to {len(pending)} calls")

        store = PromptStore()
        sem = asyncio.Semaphore(concurrency)
        result = RunResult()
        stop = asyncio.Event()
        ledger_rows: list[dict] = []
        lock = asyncio.Lock()

        async def one(irow):
            i, row = irow
            if stop.is_set():
                return
            async with sem:
                if stop.is_set():
                    return
                text, system = build_prompt(row)
                ph = prompt_hash(text)
                req_ts = datetime.now(timezone.utc).isoformat()
                base = {
                    "run_id": run_id,
                    "call_id": row["call_id"],
                    "experiment": row["experiment"],
                    "model_key": row["model_key"],
                    "slug": mcfg.slug,
                    "provider_requested": mcfg.provider.order,
                    "occupation_id": row["occupation_id"],
                    "resume_ids": row["resume_ids"],
                    "gender": row["gender"],
                    "family_code": row["family_code"],
                    "name": row["name"],
                    "name_idx": row["name_idx"],
                    "jd_variant": row["jd_variant"],
                    "position": row["position"],
                    "cue_level": row.get("cue_level"),
                    "draw": row.get("draw"),
                    "name_pair": row.get("name_pair"),
                    "contrast": row["contrast"],
                    "paraphrase_id": row["paraphrase_id"],
                    "sample_idx": row["sample_idx"],
                    "prompt_version": row["prompt_version"],
                    "prompt_text_hash": ph,
                    "request_ts": req_ts,
                }
                store.add(text)
                try:
                    resp = await client.chat(mcfg, text, system)
                except RefusalError as e:
                    rec = {**base, "latency_ms": None, "http_status": None,
                           "finish_reason": "refusal", "input_tokens": None, "output_tokens": None,
                           "reasoning_tokens": None, "cost_usd": 0.0, "raw_response": str(e)[:2000],
                           "parsed_json": None, "parse_ok": False, "refusal_flag": True,
                           "error": f"refusal: {e}"[:500], "repair_of": None}
                    result.n_refusal += 1
                except (TransportFailure, Exception) as e:  # noqa: BLE001
                    rec = {**base, "latency_ms": None, "http_status": None,
                           "finish_reason": "error", "input_tokens": None, "output_tokens": None,
                           "reasoning_tokens": None, "cost_usd": 0.0, "raw_response": "",
                           "parsed_json": None, "parse_ok": False, "refusal_flag": False,
                           "error": f"{type(e).__name__}: {e}"[:500], "repair_of": None}
                    result.n_error += 1
                else:
                    cost = resp["cost_usd"]
                    if cost is None:
                        cost = (
                            (resp["input_tokens"] or 0) * pin
                            + (resp["output_tokens"] or 0) * pout
                        ) / 1e6
                    parsed, p_ok, refusal, p_err = parse_response(
                        row["experiment"], resp["content"]
                    )
                    rec = {**base,
                           "latency_ms": resp["latency_ms"], "http_status": resp["http_status"],
                           "finish_reason": resp["finish_reason"],
                           "input_tokens": resp["input_tokens"], "output_tokens": resp["output_tokens"],
                           "reasoning_tokens": resp["reasoning_tokens"], "cost_usd": cost,
                           "provider_served": resp["provider_served"],
                           "raw_response": resp["content"][:4000],
                           "parsed_json": parsed, "parse_ok": p_ok, "refusal_flag": refusal,
                           "error": p_err, "repair_of": None}
                    if p_ok:
                        result.n_ok += 1
                    elif refusal:
                        result.n_refusal += 1
                    else:
                        # one repair attempt (spec §9): re-ask for valid JSON only
                        try:
                            repair_prompt = (
                                "Return only valid JSON matching this schema, correcting your previous answer. "
                                "Previous answer:\n" + resp["content"][:2000] + "\n\nSchema: "
                                + json.dumps(_schema_hint(row["experiment"]))
                            )
                            resp2 = await client.chat(mcfg, repair_prompt, system)
                            cost2 = resp2["cost_usd"]
                            if cost2 is None:
                                cost2 = ((resp2["input_tokens"] or 0) * pin + (resp2["output_tokens"] or 0) * pout) / 1e6
                            parsed2, p2_ok, ref2, p2_err = parse_response(row["experiment"], resp2["content"])
                            rec2 = {**base, "repair_of": row["call_id"],
                                    "request_ts": datetime.now(timezone.utc).isoformat(),
                                    "latency_ms": resp2["latency_ms"], "http_status": resp2["http_status"],
                                    "finish_reason": resp2["finish_reason"],
                                    "input_tokens": resp2["input_tokens"], "output_tokens": resp2["output_tokens"],
                                    "reasoning_tokens": resp2["reasoning_tokens"], "cost_usd": cost2,
                                    "provider_served": resp2["provider_served"],
                                    "raw_response": resp2["content"][:4000],
                                    "parsed_json": parsed2, "parse_ok": p2_ok, "refusal_flag": ref2,
                                    "error": p2_err, "prompt_text_hash": prompt_hash(repair_prompt)}
                            store.add(repair_prompt)
                            async with lock:
                                _append(log_path, rec2)
                                ledger_rows.append(_ledger_row(rec2))
                                result.cost += cost2
                                if p2_ok:
                                    result.n_ok += 1
                                elif ref2:
                                    result.n_refusal += 1
                                else:
                                    result.n_error += 1
                        except Exception:  # noqa: BLE001
                            pass
                        if parsed is None and not refusal:
                            result.n_error += 0  # original row counted below
                    result.cost += float(cost)
                async with lock:
                    _append(log_path, rec)
                    ledger_rows.append(_ledger_row(rec))
                    # kill switch check every write
                    cum = budget.ledger.spent_total() + sum(r["cost_usd"] for r in ledger_rows)
                    hit, why = budget.kill_switch(pending_estimate, result.cost, cum)
                    if hit:
                        stop.set()
                        print(f"[kill-switch] {why}")

        started = time.time()
        CHUNK = 200
        for c0 in range(0, len(pending), CHUNK):
            if stop.is_set():
                break
            chunk = list(pending.iloc[c0 : c0 + CHUNK].iterrows())
            await asyncio.gather(*(one(r) for r in chunk))
            Ledger().flush(pd.DataFrame(ledger_rows))
            print(
                f"[run] {min(c0 + CHUNK, len(pending))}/{len(pending)} dispatched | "
                f"ok={result.n_ok} refusal={result.n_refusal} err={result.n_error} "
                f"cost~${result.cost:.3f} | {time.time() - started:.0f}s"
            )
            ledger_rows = []

        store.flush()
        Ledger().flush(pd.DataFrame(ledger_rows))
        spent_total = budget.ledger.spent_total()
        summary = {
            **manifest,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "results": {"ok": result.n_ok, "refusal": result.n_refusal, "error": result.n_error},
            "run_cost_usd": round(result.cost, 4),
            "total_spent_usd": round(spent_total, 4),
        }
        (run_dir / "manifest.json").write_text(json.dumps(summary, indent=2))
        print(f"[run] DONE {run_id}: {summary['results']} cost ${result.cost:.2f}; ledger total ${spent_total:.2f}")
        return summary


def _schema_hint(exp: str) -> dict:
    if exp in ("e1", "e4"):
        return {
            "overall_fit": "int 1-10", "interview": "bool", "starting_salary_usd": "int",
            "competence": "int 1-7", "commitment": "int 1-7", "promotability": "int 1-7",
            "likability": "int 1-7", "rationale": "string",
        }
    if exp == "e2":
        return {
            "chosen": "'A' or 'B'",
            "A": {"overall_fit": "int 1-10", "starting_salary_usd": "int",
                   "competence": "int 1-7", "commitment": "int 1-7",
                   "promotability": "int 1-7", "likability": "int 1-7"},
            "B": "same as A", "rationale": "string",
        }
    if exp == "e3":
        return {"ranking": '["C1",...,"C6"] all six labels, best to worst', "top_reason": "string"}
    return {}


def _append(path: Path, rec: dict) -> None:
    with path.open("a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def _ledger_row(rec: dict) -> dict:
    return {
        "run_id": rec["run_id"], "call_id": rec["call_id"], "experiment": rec["experiment"],
        "model_key": rec["model_key"], "cost_usd": float(rec.get("cost_usd") or 0),
        "request_ts": rec["request_ts"], "parse_ok": bool(rec.get("parse_ok")),
    }
