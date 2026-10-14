"""Quality pretest (spec §4.3): score each base résumé anonymously against its
occupation JD on the pinned model; flag résumés > 1 SD from occupation mean.
Does NOT auto-replace — the researcher decides."""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from ..budget import BudgetGuard, deepseek_off_peak, price_for
from ..client import OpenRouterClient
from ..config import MATERIALS_DIR, RUNS_DIR, load_models
from ..materials.perturb import render_anonymous
from ..parse import parse_response
from ..runner import _append, _tpl, _load_jd, _load_resumes

SAMPLES = 5


async def _run(model_key: str, samples: int = SAMPLES, pricing: str | None = None) -> dict:
    models = load_models()
    mcfg = next(m for m in models.models if m.key == model_key)
    budget = BudgetGuard()
    peak = (pricing == "peak") if pricing else not deepseek_off_peak()
    pin, pout = price_for(mcfg, peak)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + f"-pretest-{model_key}"
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "logs.jsonl"

    jobs = []
    for f in sorted((MATERIALS_DIR / "base_resumes").glob("*.json")):
        occ = f.stem
        resumes = [r for r in json.loads(f.read_text()) if r.get("role", "base") == "base"]
        jd = _load_jd(occ, "base")
        for r in resumes:
            text = _tpl("e1_scoring").render(
                jd=jd, candidate=render_anonymous(r), paraphrase_id=0
            )
            for s in range(samples):
                cid = hashlib.sha256(f"pretest|{r['resume_id']}|{s}".encode()).hexdigest()[:24]
                jobs.append({"call_id": cid, "resume_id": r["resume_id"], "occupation_id": occ,
                             "sample_idx": s, "prompt": text})
    estimate = len(jobs) * (1300 * pin + 300 * pout) / 1e6
    ok, msg = budget.check(estimate, phase="pilot", allow_reserve=False)
    print(f"[pretest] {len(jobs)} calls | [budget] {msg}")
    if not ok:
        raise SystemExit(f"BUDGET GUARD REFUSED: {msg}")

    rows = []
    sem = asyncio.Semaphore(8)
    cost = 0.0
    async with OpenRouterClient(os.environ["OPENROUTER_API_KEY"]) as client:
        try:
            await client.fetch_live_prices()
            live = client.live_price(mcfg)
            if live:
                pin, pout = price_for(mcfg, peak, live)
        except Exception as e:  # noqa: BLE001
            print(f"[pretest] live price fetch failed: {e}")

        async def one(job):
            nonlocal cost
            async with sem:
                try:
                    resp = await client.chat(mcfg, job["prompt"])
                except Exception as e:  # noqa: BLE001
                    _append(log_path, {"run_id": run_id, "call_id": job["call_id"],
                                       "experiment": "pretest", "model_key": model_key,
                                       "occupation_id": job["occupation_id"],
                                       "resume_ids": job["resume_id"], "sample_idx": job["sample_idx"],
                                       "request_ts": datetime.now(timezone.utc).isoformat(),
                                       "cost_usd": 0.0, "parse_ok": False, "error": str(e)[:300],
                                       "raw_response": ""})
                    return
                c = resp["cost_usd"] or ((resp["input_tokens"] or 0) * pin + (resp["output_tokens"] or 0) * pout) / 1e6
                cost += float(c)
                parsed, p_ok, refusal, err = parse_response("e1", resp["content"])
                _append(log_path, {
                    "run_id": run_id, "call_id": job["call_id"], "experiment": "pretest",
                    "model_key": model_key, "slug": mcfg.slug,
                    "occupation_id": job["occupation_id"], "resume_ids": job["resume_id"],
                    "sample_idx": job["sample_idx"],
                    "request_ts": datetime.now(timezone.utc).isoformat(),
                    "latency_ms": resp["latency_ms"], "cost_usd": c,
                    "input_tokens": resp["input_tokens"], "output_tokens": resp["output_tokens"],
                    "parse_ok": p_ok, "refusal_flag": refusal, "error": err,
                    "parsed_json": parsed, "raw_response": resp["content"][:4000],
                })
                if p_ok:
                    rows.append({"occupation_id": job["occupation_id"],
                                 "resume_id": job["resume_id"],
                                 "overall_fit": parsed["overall_fit"],
                                 "interview": parsed["interview"]})

        await asyncio.gather(*(one(j) for j in jobs))

    import pandas as pd

    df = pd.DataFrame(rows)
    report_lines = [
        "# Résumé quality pretest", "",
        f"Run: `{run_id}` · model `{model_key}` · {samples} samples · {len(df)} valid scores · cost ${cost:.2f}", "",
    ]
    if df.empty:
        report_lines.append("NO VALID SCORES — investigate parsing before proceeding.")
    else:
        stats = df.groupby(["occupation_id", "resume_id"])["overall_fit"].mean().reset_index()
        occ_mean = stats.groupby("occupation_id")["overall_fit"].transform("mean")
        occ_sd = stats.groupby("occupation_id")["overall_fit"].transform(lambda s: s.std(ddof=0))
        stats["occ_mean"] = occ_mean
        stats["occ_sd"] = occ_sd
        stats["z"] = (stats["overall_fit"] - occ_mean) / occ_sd.replace(0, float("nan"))
        flagged = stats[stats["z"].abs() > 1]
        report_lines += [
            "| occupation | résumé | mean fit | occ mean | occ SD | z | flagged |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for _, r in stats.iterrows():
            flag = "⚠️" if abs(r["z"] or 0) > 1 else ""
            report_lines.append(
                f"| {r['occupation_id']} | {r['resume_id']} | {r['overall_fit']:.2f} | "
                f"{r['occ_mean']:.2f} | {r['occ_sd']:.2f} | {r['z']:+.2f} | {flag} |"
            )
        report_lines += ["", f"Flagged (>1 SD from occupation mean): {len(flagged)} résumé(s). "
                             "No auto-replacement; researcher decides (spec §4.3)."]
    out = MATERIALS_DIR / "pretest"
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_text("\n".join(report_lines))
    (out / "scores.json").write_text(df.to_json(orient="records", indent=2))
    print(f"[pretest] report -> {out / 'report.md'} | cost ${cost:.2f}")
    return {"run_id": run_id, "cost_usd": round(cost, 4), "valid": len(df)}


def run_pretest(model_key: str, samples: int = SAMPLES, pricing: str | None = None) -> dict:
    return asyncio.run(_run(model_key, samples=samples, pricing=pricing))
