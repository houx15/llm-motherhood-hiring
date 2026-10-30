"""Phase-4 confirmatory analysis (SPEC_PHASE4 §6): H-B1, H-B2, H-B3, H-C1.

Arms: sp_none / sp_fair / sp_gap (system prompts, Part B).
H-C1: neutral gap labels gap_closure / gap_cert vs gap_travel in sp_none (Part C).

All E2 pair-mean analyses cluster on UNORDERED résumé pairs; equivalence via
TOST at ±5pp (90% CI); Holm within families. sysarm comes from the plan
parquet (logs predate the field).
Writes docs/phase4/phase4_stats.json + docs/phase4/PHASE4_RESULTS.md.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from scipy import stats as sps

from audit.analysis.build_tables import build_tables
from audit.analysis.round3 import _unordered_pair, holm
from audit.config import ROOT

MODELS = ["deepseek_v41_flash", "claude_haiku_55", "gpt6_luna", "qwen38_flash"]
KEYS = ["deepseek", "haiku", "luna", "qwen"]
ARMS = ["sp_none", "sp_fair", "sp_gap"]
OUT: dict = {}


def phase4_tables(model_key: str) -> pd.DataFrame:
    """Phase-4 E2 rows with sysarm joined from the plan.

    Rows are selected by CALL_ID MEMBERSHIP in the phase-4 plan (not run_id:
    the loader's dedup keeps each call's latest valid attempt, whose run_id may
    be a repair2-* dir after the Oct-30 repair passes).
    """
    e2 = build_tables(None, model_key=model_key)["e2"]
    plan = pd.read_parquet("data/plans/phase4_main.parquet", columns=["call_id", "sysarm", "model_key"])
    plan = plan[plan.model_key == model_key]
    e2 = e2[e2.call_id.isin(set(plan.call_id))].copy()
    e2 = e2[~e2.from_repair.astype(bool)]  # repair prompts lack the original
    # candidates; their `chosen` fields are not experimental responses
    e2 = e2.merge(plan[["call_id", "sysarm"]].drop_duplicates(), on="call_id", how="left")
    e2["pair"] = _unordered_pair(e2)
    e2["pc"] = pd.to_numeric(e2["parent_chosen"], errors="coerce")
    e2["wc"] = pd.to_numeric(e2["woman_chosen"], errors="coerce")
    return e2


def _pair_means_arm(e2, arm, contrast, gender=None):
    m = (e2.sysarm == arm) & (e2.contrast == contrast)
    if gender is not None:
        m &= e2.gender == gender
    s = e2[m]
    return s.groupby("pair")["pc"].mean().dropna()


def _matched(a: pd.Series, b: pd.Series, label: str) -> dict:
    common = a.index.intersection(b.index)
    if len(common) < 5:
        return None
    d = (a[common] - b[common]).values
    t, p = sps.ttest_1samp(d, 0)
    se = d.std(ddof=1) / np.sqrt(len(d))
    ci90 = sps.t.ppf(0.95, len(d) - 1) * se
    # TOST at ±0.05
    p_lo = 1 - sps.t.cdf((d.mean() + 0.05) / se, len(d) - 1)
    p_hi = sps.t.cdf((d.mean() - 0.05) / se, len(d) - 1)
    return {"contrast": label, "mean": round(float(d.mean()), 3),
            "ci90": [round(float(d.mean() - ci90), 3), round(float(d.mean() + ci90), 3)],
            "t": round(float(t), 1), "p": round(float(p), 4),
            "tost_p": round(float(max(p_lo, p_hi)), 4),
            "equivalent_5pp": bool(max(p_lo, p_hi) < 0.05), "n_pairs": int(len(common))}


def validity_by_arm() -> dict:
    plan = pd.read_parquet("data/plans/phase4_main.parquet", columns=["call_id", "sysarm", "model_key"])
    res = {}
    for m, k in zip(MODELS, KEYS):
        pm = plan[plan.model_key == m].set_index("call_id")["sysarm"]
        ok, ref = {}, {}
        for f in ROOT.glob(f"runs/*phase4_main-{m}*/logs.jsonl"):
            for l in open(f):
                r = json.loads(l)
                if r.get("repair_of"):
                    continue
                arm = pm.get(r["call_id"])
                if arm is None:
                    continue
                if r.get("refusal_flag"):
                    ref[arm] = ref.get(arm, 0) + 1
                elif r.get("parse_ok"):
                    ok[arm] = ok.get(arm, 0) + 1
        res[k] = {"valid_by_arm": ok, "refusals_by_arm": ref,
                  "n_by_arm": pm.value_counts().to_dict()}
    return res


def hb1_hb3() -> dict:
    """sp_fair - sp_none (H-B1) and sp_gap - sp_none (H-B3) per model x contrast."""
    res = {}
    for m, k in zip(MODELS, KEYS):
        e2 = phase4_tables(m)
        entry: dict = {}
        fam_p = {}
        for contrast in ["parent", "parent_gap", "gap_travel"]:
            for gender in ["female", "male"]:
                none = _pair_means_arm(e2, "sp_none", contrast, gender)
                for arm in ["sp_fair", "sp_gap"]:
                    oth = _pair_means_arm(e2, arm, contrast, gender)
                    r = _matched(oth, none, f"{arm[3:]}-none {contrast} {gender[0]}")
                    if r:
                        entry[f"{contrast}|{gender}|{arm}"] = r
                        fam_p[f"{contrast}|{gender}|{arm}"] = r["p"]
        adj = holm(fam_p)
        for key, v in adj.items():
            entry[key]["holm"] = round(v, 4)
        res[k] = entry
    return res


def hb2() -> dict:
    """Layer-2 responses: Luna's gender_parent preference and Haiku's
    mother-father parent-cue gap, by arm."""
    res = {}
    for m, k in zip(MODELS, KEYS):
        e2 = phase4_tables(m)
        entry: dict = {}
        # direct mother-vs-father preference per arm (parity .5)
        for arm in ARMS:
            s = e2[(e2.sysarm == arm) & (e2.contrast == "gender_parent")]
            if s.empty:
                continue
            pm = s.groupby("pair")["wc"].mean().dropna()
            t, p = sps.ttest_1samp(pm.values, 0.5)
            entry[f"gender_parent|{arm}"] = {"p_woman": round(float(pm.mean()), 3),
                                             "t_vs_half": round(float(t), 1), "p": round(float(p), 4)}
        # mother-father same-gender gap per arm (parent cue)
        for arm in ARMS:
            f = _pair_means_arm(e2, arm, "parent", "female")
            ml = _pair_means_arm(e2, arm, "parent", "male")
            common = f.index.intersection(ml.index)
            if len(common) >= 5:
                d = (f[common] - ml[common]).values
                t, p = sps.ttest_1samp(d, 0)
                entry[f"MF_gap|{arm}"] = {"diff": round(float(d.mean()), 3),
                                          "t": round(float(t), 1), "p": round(float(p), 4),
                                          "n_pairs": int(len(common))}
        res[k] = entry
    return res


def hc1() -> dict:
    """Neutral labels vs travel (sp_none arm): equivalence at ±5pp."""
    res = {}
    for m, k in zip(MODELS, KEYS):
        e2 = phase4_tables(m)
        entry: dict = {}
        for lab in ["gap_closure", "gap_cert"]:
            for gender in ["female", "male"]:
                a = _pair_means_arm(e2, "sp_none", lab, gender)
                b = _pair_means_arm(e2, "sp_none", "gap_travel", gender)
                r = _matched(a, b, f"{lab}-travel {gender[0]}")
                if r:
                    entry[f"{lab}|{gender}"] = r
        # also vs parental label (does a neutral reason beat 'Parental leave'?)
        adj = holm({kk: vv["p"] for kk, vv in entry.items()})
        for kk, v in adj.items():
            entry[kk]["holm"] = round(v, 4)
        res[k] = entry
    return res


if __name__ == "__main__":
    OUT["validity"] = validity_by_arm()
    OUT["hb1_hb3"] = hb1_hb3()
    OUT["hb2"] = hb2()
    OUT["hc1"] = hc1()
    p = ROOT / "docs" / "phase4" / "phase4_stats.json"
    p.write_text(json.dumps(OUT, indent=1))
    print(f"wrote {p}")
    print("\n== H-C1: neutral labels vs travel (sp_none, women) ==")
    for k in KEYS:
        for lab in ["gap_closure", "gap_cert"]:
            r = OUT["hc1"][k].get(f"{lab}|female")
            if r:
                print(f"{k:9} {lab:13} diff {r['mean']:+.3f} CI90 {r['ci90']} equiv(±5pp): {r['equivalent_5pp']}")
    print("\n== H-B1/H-B3: arm effects on penalties (women) ==")
    for k in KEYS:
        for con in ["parent", "parent_gap"]:
            for arm in ["fair", "gap"]:
                r = OUT["hb1_hb3"][k].get(f"{con}|female|sp_{arm}")
                if r:
                    print(f"{k:9} {con:11} sp_{arm:4}: {r['mean']:+.3f} CI90 {r['ci90']} t {r['t']}")
    print("\n== H-B2: Luna gender_parent / Haiku MF gap by arm ==")
    print(json.dumps({k: {kk: vv for kk, vv in OUT["hb2"][k].items() if kk.startswith("gender_parent") or (k == "haiku" and kk.startswith("MF_gap"))} for k in ["luna", "haiku"]}, indent=1))
