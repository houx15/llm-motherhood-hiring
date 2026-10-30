"""Offline targeted repair pass (spec §9 spirit; deviation documented in QUESTIONS.md).

Re-asks invalid, non-refusal calls with an explicit field-level correction:
"you returned likability=8; ratings are integers 1-7". Every repair is logged with
a repair_of link and counted in the ledger. The primary analysis still uses strict
validity; a winsorized robustness re-parse lives in analysis.
"""
from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .budget import BudgetGuard, Ledger, price_for
from .client import OpenRouterClient
from .config import RUNS_DIR, load_models
from .parse import extract_json, parse_response
from .runner import _append, _ledger_row


def find_invalid(run_glob: str, model_key: str) -> list[dict]:
    """Invalid, non-refusal, not-yet-repaired calls for a model across runs.

    run_glob is a glob for logs.jsonl FILES, e.g. '*phase2*/logs.jsonl'.
    """
    invalid: dict[str, dict] = {}
    repaired: set[str] = set()
    valid: set[str] = set()
    for f in sorted(RUNS_DIR.glob(run_glob)):
        if not f.is_file():
            continue
        for line in f.read_text().splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("model_key") != model_key:
                continue
            if r.get("repair_of"):
                if r.get("parse_ok"):
                    repaired.add(r["repair_of"])
            elif r.get("parse_ok") or r.get("refusal_flag"):
                valid.add(r["call_id"])  # succeeded somewhere: never repair
            elif (
                r.get("experiment") in ("e1", "e2", "e3", "e4")
                and not r.get("parse_ok")
                and not r.get("refusal_flag")
            ):
                invalid[r["call_id"]] = r
    return [r for cid, r in invalid.items() if cid not in repaired and cid not in valid]


REPAIR_TMPL = """Your previous answer was invalid JSON for a hiring evaluation.

Your previous answer:
{prev}

Problems: {problems}

Rules you MUST follow in the corrected answer:
- Every rating (competence, commitment, promotability, likability) is an INTEGER from 1 to 7 INCLUSIVE. 8, 9, 0, or text like "strong" are INVALID.
- overall_fit is an INTEGER from 1 to 10. interview is true or false. starting_salary_usd is an integer number of US dollars.
{extra}
Return ONLY the corrected JSON object, same keys as before, nothing else."""


def _problems(row: dict) -> str:
    err = str(row.get("error") or "")
    out = []
    if "out of range" in err:
        out.append("at least one rating was out of the allowed 1-7 range (e.g., 8 or 9)")
    if "could not convert" in err or "not a boolean" in err:
        out.append("a non-numeric or wrong-type value was used where a number/boolean is required")
    if "Field required" in err or "missing" in err:
        out.append("required fields were missing")
    if "permutation" in err:
        out.append("the ranking must list all six labels C1..C6 exactly once")
    return "; ".join(out) or "the JSON did not match the required schema"


async def _run(run_glob: str, model_key: str, max_calls: int | None) -> dict:
    models = load_models()
    mcfg = next(m for m in models.models if m.key == model_key)
    todo = find_invalid(run_glob, model_key)
    if max_calls:
        todo = todo[:max_calls]
    if not todo:
        return {"repaired": 0, "note": "nothing to repair"}
    budget = BudgetGuard()
    pin, pout = mcfg.prices(peak=False)
    estimate = len(todo) * (1200 * pin + 350 * 1.15 * pout) / 1e6
    ok, msg = budget.check(estimate, allow_reserve=False)
    print(f"[repair] {len(todo)} calls to repair | [budget] {msg}")
    if not ok:
        raise SystemExit(f"BUDGET GUARD REFUSED: {msg}")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + f"-repair2-{model_key}"
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "logs.jsonl"
    sem = asyncio.Semaphore(8)
    n_ok = n_fail = 0
    cost = 0.0
    async with OpenRouterClient(os.environ["OPENROUTER_API_KEY"]) as client:
        try:
            await client.fetch_live_prices()
            live = client.live_price(mcfg)
            if live:
                pin, pout = price_for(mcfg, False, live)
        except Exception as e:  # noqa: BLE001
            print(f"[repair] live prices unavailable: {e}")

        async def one(row):
            nonlocal n_ok, n_fail, cost
            async with sem:
                extra = ""
                if row["experiment"] == "e2":
                    extra = '- The JSON has keys: chosen ("A" or "B"), A {...}, B {...}, rationale.'
                elif row["experiment"] == "e3":
                    extra = '- The JSON has keys: ranking (all six labels "C1".."C6", best first), top_reason.'
                prompt = REPAIR_TMPL.format(
                    prev=(row.get("raw_response") or "")[:2500],
                    problems=_problems(row),
                    extra=extra,
                )
                try:
                    resp = await client.chat(mcfg, prompt, max_tokens=600)
                except Exception as e:  # noqa: BLE001
                    _append(log_path, {**row, "run_id": run_id, "repair_of": row["call_id"],
                                       "request_ts": datetime.now(timezone.utc).isoformat(),
                                       "cost_usd": 0.0, "parse_ok": False, "refusal_flag": False,
                                       "error": f"transport: {e}"[:300], "raw_response": ""})
                    n_fail += 1
                    return
                c = resp["cost_usd"] or ((resp["input_tokens"] or 0) * pin + (resp["output_tokens"] or 0) * pout) / 1e6
                cost += float(c)
                parsed, p_ok, ref, err = parse_response(row["experiment"], resp["content"])
                _append(log_path, {**row, "run_id": run_id, "repair_of": row["call_id"],
                                   "request_ts": datetime.now(timezone.utc).isoformat(),
                                   "latency_ms": resp["latency_ms"], "cost_usd": c,
                                   "finish_reason": resp["finish_reason"],
                                   "input_tokens": resp["input_tokens"], "output_tokens": resp["output_tokens"],
                                   "parse_ok": p_ok, "refusal_flag": ref, "error": err,
                                   "parsed_json": parsed, "raw_response": resp["content"][:4000]})
                if p_ok:
                    n_ok += 1
                else:
                    n_fail += 1

        await asyncio.gather(*(one(r) for r in todo))
    try:
        Ledger().flush(pd.DataFrame([_ledger_row(json.loads(l)) for l in log_path.read_text().splitlines()]))
    except Exception as e:  # noqa: BLE001 — raw JSONL is canonical
        print(f"[repair] WARNING ledger flush failed: {e}")
    summary = {"run_id": run_id, "attempted": len(todo), "repaired": n_ok, "still_bad": n_fail,
               "cost_usd": round(cost, 4)}
    (run_dir / "manifest.json").write_text(json.dumps(summary, indent=2))
    print(f"[repair] done: {summary}")
    return summary


def run_repair(run_glob: str, model_key: str, max_calls: int | None = None) -> dict:
    return asyncio.run(_run(run_glob, model_key, max_calls))
