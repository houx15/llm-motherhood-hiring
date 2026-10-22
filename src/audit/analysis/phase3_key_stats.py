"""Key phase-3 statistics for the integrated report -> docs/phase3/phase3_key_stats.json.

Everything the rewritten report cites from phase 3, generated (no hand-typed numbers):
O8-only cue-level invariance table, E3-v3 ranking ratios, occupation-regression
coefficients, per-model E2 salary gaps (main run, from stats.json), decomposition,
direct-gender, abstention, drift, manipulation check.
"""
import json

import pandas as pd
import statsmodels.api as sm

from audit.analysis.phase3_stats import (
    LEVELS,
    LEVEL_NAMES,
    _tables_for,
    abstention,
    drift,
    manip_summary,
    placebo_decomposition,
)
from audit.config import load_occupations_built

MODELS = ["deepseek_v41_flash", "claude_haiku_55", "gpt6_luna", "qwen38_flash"]
SHORT = dict(zip(MODELS, ["deepseek", "haiku", "luna", "qwen"]))
O8 = {o.id for o in load_occupations_built().occupations if o.cohort == "o8"}
CONTRASTS = ["parent", "parent_committed", "parent_gap", "personal", "gap_travel", "gap_parental_only"]

OUT: dict = {}

# ---- 1. O8-only cue-level invariance (same occupations at every level) ----
cue_o8 = {}
for m in MODELS:
    e2 = _tables_for(m)["e2"]
    sub = e2[e2.occupation_id.isin(O8)]
    tbl = {}
    for con in CONTRASTS:
        row = {}
        for lvl in LEVELS:
            s = sub[(sub.cue_level == lvl) & (sub.contrast == con)]["parent_chosen"].dropna().astype(float)
            row[lvl] = round(float(s.mean()), 3) if len(s) else None
        tbl[con] = row
    cue_o8[SHORT[m]] = tbl
OUT["cue_level_o8_only"] = cue_o8

# ---- 2. E3-v3 ranking: top-3 ratio parent vs childless, by cue level ----
e3v3 = {}
for m in MODELS:
    e3 = _tables_for(m).get("e3")
    if e3 is None or e3.empty:
        continue
    tbl = {}
    for lvl in LEVELS:
        sub = e3[(e3.cue_level == lvl) & (e3.composition.isin(["a", "b"]))]
        if sub.empty:
            continue
        par = float(sub[sub.parent == 1]["top3"].mean())
        non = float(sub[sub.parent == 0]["top3"].mean())
        tbl[lvl] = {"parent_top3": round(par, 3), "childless_top3": round(non, 3),
                    "ratio": round(par / non, 3), "n_pools": int(len(sub) // 6)}
    e3v3[SHORT[m]] = tbl
OUT["e3v3_ratio_by_level"] = e3v3

# ---- 3. Occupation regressions (leave-gap mother penalty ~ z-scores, n=28) ----
from audit.analysis.phase3_stats import occupation_appendix

occ_reg = {}
for m in MODELS:
    d = occupation_appendix(m)
    if d.empty:
        continue
    zs = ["z_female_share", "z_median_wage", "z_physical", "z_care", "z_analytic", "z_manage"]
    d = d.dropna(subset=["p_parent_gap_F"] + zs)
    X = sm.add_constant(d[zs])
    fit = sm.OLS(d["p_parent_gap_F"], X).fit()
    occ_reg[SHORT[m]] = {
        "n": int(fit.nobs),
        "z_female_share": {"coef": round(float(fit.params["z_female_share"]), 3),
                           "p": round(float(fit.pvalues["z_female_share"]), 4)},
        "z_care": {"coef": round(float(fit.params["z_care"]), 3),
                   "p": round(float(fit.pvalues["z_care"]), 4)},
    }
OUT["occupation_regression_parent_gap_F"] = occ_reg

# ---- 4. decomposition / direct gender / abstention / drift / manip ----
OUT["decomposition_L0_mothers"] = {
    SHORT[m]: {
        "parenthood_net_of_disclosure": float(
            placebo_decomposition(m).query("level == 'L0 name' and group == 'mothers'")
            ["parenthood (parent-personal)"].iloc[0]),
        "caregiving_label_net_of_interruption": float(
            placebo_decomposition(m).query("level == 'L0 name' and group == 'mothers'")
            ["caregiving (gap_par-gap_travel)"].iloc[0]),
        "family_bundle_on_top_of_gap": float(
            placebo_decomposition(m).query("level == 'L0 name' and group == 'mothers'")
            ["bundle (parent_gap-gap_par)"].iloc[0]),
    } for m in MODELS
}
OUT["abstention_pregnant_by_level"] = {
    SHORT[m]: {k: (None if pd.isna(v) else round(float(v), 3))
               for k, v in abstention(m).loc["pregnant"].items()}
    for m in MODELS
}
OUT["drift_mean_delta"] = {SHORT[m]: round(float(drift(m)["delta"].mean()), 3) for m in MODELS}
OUT["manip"] = json.loads(manip_summary().to_json(orient="records"))

# ---- 5. main-run per-model E2 salary gaps + pooled stats for citation ----
S = json.load(open("docs/report/stats.json"))
OUT["main_e2_salary_mother"] = {
    SHORT[m]: {"parent_usd": S["models"][m]["e2_parent_salary_f"]["diff"],
               "parent_pct": S["models"][m]["e2_parent_salary_f"]["pct"],
               "gap_usd": S["models"][m]["e2_parent_gap_salary_f"]["diff"],
               "gap_pct": S["models"][m]["e2_parent_gap_salary_f"]["pct"]}
    for m in MODELS
}

if __name__ == "__main__":
    from audit.config import ROOT

    p = ROOT / "docs" / "phase3" / "phase3_key_stats.json"
    p.write_text(json.dumps(OUT, indent=1))
    print(f"wrote {p}")
    print(json.dumps(OUT["e3v3_ratio_by_level"], indent=1))
    print(json.dumps(OUT["occupation_regression_parent_gap_F"], indent=1))
