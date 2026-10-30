"""SPEC_FINALIZE F3: study totals (calls, cost, validity per phase)."""
from __future__ import annotations

import json
import re
from collections import defaultdict

import pandas as pd

from audit.config import ROOT


def phase_of(run_id: str) -> str:
    if "materials" in run_id:
        return "materials"
    if "pretest" in run_id:
        return "pretest"
    if "pilot-" in run_id or run_id.endswith("-pilot-deepseek_v41_flash"):
        return "pilot"
    if run_id.endswith(("-e1_scoring-deepseek_v41_flash", "-e2_paired-deepseek_v41_flash",
                        "-e3_ranking-deepseek_v41_flash", "-e4_jd_context-deepseek_v41_flash")):
        return "main_run (phase 1)"
    if "phase2" in run_id:
        return "main_run (phase 2, other models)"
    if "repair2" in run_id and run_id < "20261018":
        return "main_run repairs"
    if "phase3_pilot" in run_id:
        return "phase 3 pilot"
    if "phase3_manip" in run_id or "manip" in run_id:
        return "phase 3 manipulation check"
    if "phase3_lawyer" in run_id:
        return "phase 3 lawyer rerun"
    if "phase3_main" in run_id:
        return "phase 3 main"
    if "phase3" in run_id:
        return "phase 3 other"
    if "phase4_main" in run_id:
        return "phase 4 experiment"
    if "rationale_coding" in run_id:
        return "phase 4 rationale coding"
    if "repair2" in run_id:
        return "phase 3/4 repairs"
    return "other"


def main() -> None:
    rows = []
    for f in ROOT.glob("runs/*/logs.jsonl"):
        for l in open(f):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            rows.append(r)
    df = pd.DataFrame([{
        "run_id": r.get("run_id"), "call_id": r.get("call_id"), "cost": float(r.get("cost_usd") or 0),
        "ok": bool(r.get("parse_ok")), "refusal": bool(r.get("refusal_flag")),
        "repair": r.get("repair_of") is not None,
    } for r in rows])
    df["phase"] = df.run_id.map(phase_of)
    df = df.drop_duplicates(subset=["run_id", "call_id", "ok", "refusal", "repair"])

    # unique planned calls per phase: a call belongs to the phase of its FIRST attempt
    first = df.sort_values("run_id").drop_duplicates("call_id")
    phase_of_call = first.set_index("call_id")["phase"]
    validity: dict[str, dict] = {}
    for call, ph in phase_of_call.items():
        v = validity.setdefault(ph, {"calls": 0, "valid_original": 0, "refusal": 0, "valid_incl_repair": 0})
        v["calls"] += 1
        sub = df[df.call_id == call]
        if sub[(~sub.repair) & sub.ok].shape[0] or sub[(~sub.repair) & sub.refusal].shape[0]:
            v["valid_original"] += 1
        if sub[(~sub.repair) & sub.refusal].shape[0]:
            v["refusal"] += 1  # refusals on ORIGINAL prompts only (repair-pass
            # refusal rows are artifacts of re-asking already-valid calls)
        if sub[sub.ok].shape[0] or sub[sub.refusal].shape[0]:
            v["valid_incl_repair"] += 1

    cost = df.groupby("phase")["cost"].sum().round(2).to_dict()
    log_rows = df.groupby("phase").size().to_dict()

    out = {"phases": {}, "grand_total": {
        "calls": int(len(phase_of_call)),
        "log_rows": int(len(df)),
        "cost_usd": round(float(df.cost.sum()), 2),
        "valid_original": sum(v["valid_original"] for v in validity.values()),
    }}
    lines = ["# F3: study totals", "",
             "| phase | unique calls | valid (original) | refusals | valid % | log rows | cost |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for ph in sorted(validity, key=lambda p: -(cost.get(p, 0))):
        v = validity[ph]
        pct = round(100 * v["valid_original"] / v["calls"], 2) if v["calls"] else 0
        out["phases"][ph] = {**v, "cost_usd": cost.get(ph, 0.0), "log_rows": log_rows.get(ph, 0)}
        lines.append(f"| {ph} | {v['calls']:,} | {v['valid_original']:,} | {v['refusal']:,} "
                     f"| {pct:.2f}% | {log_rows.get(ph, 0):,} | ${cost.get(ph, 0):.2f} |")
    g = out["grand_total"]
    lines += ["", f"**Grand total: {g['calls']:,} unique calls, {g['log_rows']:,} log rows, "
              f"${g['cost_usd']:.2f}, {g['valid_original']:,} valid-original responses "
              f"({100 * g['valid_original'] / g['calls']:.2f}%).**", ""]
    d = ROOT / "docs" / "final"
    d.mkdir(exist_ok=True)
    (d / "study_totals.json").write_text(json.dumps(out, indent=1))
    (d / "study_totals.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
