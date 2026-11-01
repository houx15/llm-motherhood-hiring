"""R16-2: per-occupation leave-gap penalty estimates for Supplementary Fig. S2.

For each model x occupation (28): P(parent_gap chosen) for mothers and fathers
with pair-clustered CIs. Main run for O20; phase-3 L0 (`name`) for O8 (only
occupations where phase-3 L0 cells exist). Output docs/final/occupations.json.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from scipy import stats as sps

from audit.analysis.etl import load_clean
from audit.analysis.select import main_run_ids, phase3_ids
from audit.analysis.build_tables import _moderators
from audit.config import ROOT

MODELS = ["deepseek_v41_flash", "gpt6_luna", "qwen38_flash", "claude_haiku_55"]


def occupation_estimates() -> list[dict]:
    e2 = load_clean("e2")
    e2 = e2[~e2.from_repair.astype(bool)]
    e2["pc"] = pd.to_numeric(e2["parent_chosen"], errors="coerce")
    main = e2[e2.call_id.isin(main_run_ids())]
    p3 = e2[e2.call_id.isin(phase3_ids()) & (e2.cue_level == "name")]
    mod = _moderators().drop_duplicates("occupation_id").set_index("occupation_id")
    rows = []
    occs = sorted(set(main.occupation_id) | set(p3.occupation_id))
    for m in MODELS:
        for occ in occs:
            rec = {"model": m.split("_")[0], "occupation_id": occ}
            src_main = main[(main.model_key == m) & (main.occupation_id == occ)
                            & (main.contrast == "parent_gap")]
            src_p3 = p3[(p3.model_key == m) & (p3.occupation_id == occ)
                        & (p3.contrast == "parent_gap")]
            for g, key in [("female", "mother"), ("male", "father")]:
                sub = pd.concat([src_main[src_main.gender == g], src_p3[src_p3.gender == g]])
                pm = sub.groupby("resume_ids")["pc"].mean().dropna()
                if len(pm) >= 2:
                    se = pm.std(ddof=1) / np.sqrt(len(pm))
                    t = sps.t.ppf(0.975, len(pm) - 1)
                    rec[f"{key}_p"] = round(float(pm.mean()), 3)
                    rec[f"{key}_ci"] = [round(float(pm.mean() - t * se), 3),
                                        round(float(pm.mean() + t * se), 3)]
                    rec[f"{key}_n_pairs"] = int(len(pm))
                else:
                    rec[f"{key}_p"] = None
            for col in ["female_share", "median_wage", "care", "time_demands"]:
                if col in mod.columns and occ in mod.index:
                    v = mod.loc[occ, col]
                    rec[col] = round(float(v), 3) if pd.notna(v) else None
                else:
                    rec[col] = None
            rec["cohort"] = "o8" if occ in {"childcare_worker", "electrician", "emt_paramedic",
                                            "health_services_manager", "housekeeper",
                                            "police_officer", "security_guard", "veterinarian"} else "o20"
            rows.append(rec)
    return rows


if __name__ == "__main__":
    rows = occupation_estimates()
    out = ROOT / "docs/final/occupations.json"
    out.write_text(json.dumps(rows, indent=1))
    n_ok = sum(1 for r in rows if r.get("mother_p") is not None)
    print(f"wrote {out}: {len(rows)} rows ({n_ok} with mother estimates)")


