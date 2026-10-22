"""Round-5 analyses (REVIEW_NOTES.md Round 5).

5-3a tie-breaker check: is the E2 penalty concentrated in near-tie résumé pairs?
5-3b noise model: does the E1 score gap predict the E2 choice share under a
       probit on within-cell fit noise? (forced-choice amplification test)
5-4 primary estimand: decomposition on O20 L1/L2 pooled (56 -> 40 pairs) with CI;
       the interruption's own effect vs parity with CI.
Writes docs/phase3/round5_stats.json.
"""
import json

import numpy as np
import pandas as pd
from scipy import stats as sps

from audit.analysis.build_tables import build_tables
from audit.analysis.round3 import _pm, _unordered_pair, holm
from audit.config import MATERIALS_DIR, ROOT
from audit.analysis.phase3_stats import _tables_for

MODELS = ["deepseek_v41_flash", "claude_haiku_55", "gpt6_luna", "qwen38_flash"]
SHORT = dict(zip(MODELS, ["deepseek", "haiku", "luna", "qwen"]))
OUT: dict = {}


def _pretest_quality() -> pd.Series:
    """Mean anonymous-pretest fit per resume_id (materials quality measure)."""
    rows = json.load(open(MATERIALS_DIR / "pretest" / "scores.json"))
    if isinstance(rows, dict):
        rows = list(rows.values())
    df = pd.DataFrame(rows)
    return df.groupby("resume_id")["overall_fit"].mean()


# ---------------- 5-3a: penalty by pair quality gap ----------------
def tiebreaker() -> dict:
    qual = _pretest_quality()
    res = {}
    for m in MODELS:
        e2 = build_tables(None, model_key=m)["e2"]
        e2 = e2[~e2.run_id.str.contains("phase3")].copy()
        e2["pair"] = _unordered_pair(e2)
        entry = {}
        for con in ["parent", "parent_gap"]:
            sub = e2[(e2.contrast == con)].copy()
            sub["pc"] = pd.to_numeric(sub["parent_chosen"], errors="coerce")
            pm = sub.groupby(["pair", "gender"])["pc"].mean().reset_index()
            # quality gap of the underlying résumé pair (occupation|a-b)
            def qgap(pair):
                occ, ab = pair.split("|")
                a, b = ab.split("-")
                return abs(qual.get(f"{occ}_{a}", np.nan) - qual.get(f"{occ}_{b}", np.nan))
            pm["qgap"] = pm["pair"].map(qgap)
            pm = pm.dropna(subset=["qgap"])
            med = pm["qgap"].median()
            near = pm[pm.qgap <= med]
            far = pm[pm.qgap > med]
            entry[con] = {
                "median_qgap_fit": round(float(med), 2),
                "near_tie": {"penalty_pp": round(50 - float(near["pc"].mean()) * 100, 1), "n": len(near)},
                "clear_gap": {"penalty_pp": round(50 - float(far["pc"].mean()) * 100, 1), "n": len(far)},
                "t_near_vs_far": round(float(sps.ttest_ind(near["pc"], far["pc"], equal_var=False).statistic), 1),
            }
        res[SHORT[m]] = entry
    return res


# ---------------- 5-3b: noise model ----------------
def noise_model() -> dict:
    """Predicted P(parent chosen) if E2 choices were driven by E1 fit gaps plus
    within-cell noise: P = Phi(delta_fit / sigma_within). delta_fit = E1 fit gap
    (cue minus none, same gender+occupation, per model). sigma_within = SD of
    fit within E1 cells (call-level)."""
    res = {}
    for m in MODELS:
        tabs = build_tables(None, model_key=m)
        e1 = tabs["e1"]
        e1 = e1[~e1.run_id.str.contains("phase3")].copy()
        e2 = tabs["e2"]
        e2 = e2[~e2.run_id.str.contains("phase3")]
        sigma = float(e1.groupby(["family_code", "gender", "occupation_id"])["overall_fit"].std().mean())
        entry = {"sigma_within_fit": round(sigma, 2)}
        for con in ["parent", "parent_gap"]:
            gap = e1[(e1.family_code == con) & (e1.gender == "female")]["overall_fit"].mean() - \
                  e1[(e1.family_code == "none") & (e1.gender == "female")]["overall_fit"].mean()
            predicted = float(sps.norm.cdf(gap / sigma))
            actual = float(e2[(e2.contrast == con) & (e2.gender == "female")]["parent_chosen"].astype(float).mean())
            entry[con] = {"e1_fit_gap": round(float(gap), 3), "predicted_P_parent": round(predicted, 3),
                          "actual_P_parent": round(actual, 3)}
        res[SHORT[m]] = entry
    return res


# ---------------- 5-4: primary decomposition estimand + interruption effect ----------------
def primary_decomposition() -> dict:
    """O20 at L1+L2 pooled (40 unordered pairs), pair-matched t + 95% CI;
    plus each component's cell means and the interruption's own effect
    (0.5 - P(gap_travel chosen)) with t vs parity."""
    from audit.analysis.phase3_stats import _tables_for as _tf

    res = {}
    for m in MODELS:
        e2 = _tf(m)["e2"]
        o20 = ~e2.occupation_id.isin(
            {o.id for o in __import__("audit.config", fromlist=["load_occupations_built"]).load_occupations_built().occupations if o.cohort == "o8"}
        )
        mask = o20 & e2.cue_level.isin(["name_field", "initial_field"])
        entry: dict = {}
        for comp, (c1, c2) in {"parenthood": ("parent", "personal"),
                               "label": ("gap_parental_only", "gap_travel"),
                               "bundle": ("parent_gap", "gap_parental_only")}.items():
            a, b = _pm(e2[mask & e2.cue_level.isin(["name_field"])], "name_field", c1), None
            # pooled L1+L2: average the two levels' pair means first
            a1 = _pm(e2, "name_field", c1) if False else None
            # simpler: restrict df then average levels per pair
            def pooled(con):
                rows = []
                for lvl in ["name_field", "initial_field"]:
                    s = e2[mask & (e2.cue_level == lvl) & (e2.contrast == con)].copy()
                    s["pc"] = pd.to_numeric(s["parent_chosen"], errors="coerce")
                    s["pair"] = _unordered_pair(s)
                    rows.append(s.groupby("pair")["pc"].mean())
                return pd.concat(rows, axis=1).mean(axis=1)
            pa, pb = pooled(c1), pooled(c2)
            common = pa.index.intersection(pb.index)
            d = (pa[common] - pb[common]).values
            t, p = sps.ttest_1samp(d, 0)
            entry[comp] = {"diff": round(float(d.mean()), 3),
                           "ci95": [round(float(d.mean() - 1.96 * d.std(ddof=1) / np.sqrt(len(d))), 3),
                                    round(float(d.mean() + 1.96 * d.std(ddof=1) / np.sqrt(len(d)), ), 3)],
                           "t": round(float(t), 1), "p": round(float(p), 4), "n_pairs": int(len(common))}
        # interruption's own effect: gap_travel (and gap_parental_only) vs parity
        for con in ["gap_travel", "gap_parental_only", "personal", "parent", "parent_gap"]:
            pm = pooled(con)
            t, p = sps.ttest_1samp(pm.values, 0.5)
            entry[f"cell_{con}"] = {"P": round(float(pm.mean()), 3),
                                    "t_vs_half": round(float(t), 1), "p": round(float(p), 4)}
        res[SHORT[m]] = entry
    return res


if __name__ == "__main__":
    OUT["tiebreaker"] = tiebreaker()
    OUT["noise_model"] = noise_model()
    OUT["primary_decomposition"] = primary_decomposition()
    p = ROOT / "docs" / "phase3" / "round5_stats.json"
    p.write_text(json.dumps(OUT, indent=1))
    print(f"wrote {p}")
    print(json.dumps(OUT["noise_model"], indent=1))
    print(json.dumps(OUT["primary_decomposition"]["deepseek"], indent=1))
    print(json.dumps(OUT["tiebreaker"]["deepseek_v41_flash" if "deepseek_v41_flash" in OUT["tiebreaker"] else "deepseek"], indent=1))
