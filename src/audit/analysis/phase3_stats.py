"""Phase-3 analysis (SPEC_PHASE3 §8): pilot checks and cue-level reports.

pilot_checks(): parse/refusal rates, salary withholding by cue level, position
bias — the §6.4 gate before the full run.
phase3_report(): the §8 tables — gender preference by cue level, parent penalty
by cue level, placebo decomposition, mother-vs-father by outcome, abstention,
drift anchors. Everything is computed from logs; outputs markdown.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from ..config import RUNS_DIR
from .build_tables import build_tables

LEVELS = ["name", "name_field", "initial_field", "blind"]
LEVEL_NAMES = {"name": "L0 name", "name_field": "L1 name+field",
               "initial_field": "L2 initial+field", "blind": "L3 blind"}
MODELS = ["deepseek_v41_flash", "claude_haiku_55", "gpt6_luna", "qwen38_flash"]
SHORT = {"deepseek_v41_flash": "DeepSeek", "claude_haiku_55": "Haiku",
         "gpt6_luna": "Luna", "qwen38_flash": "Qwen"}


def _tables_for(model_key: str, phase3_only: bool = True) -> dict[str, pd.DataFrame]:
    tabs = build_tables(None, model_key=model_key)
    if phase3_only:
        out = {}
        for k, df in tabs.items():
            if "run_id" in df.columns:
                # keep only phase-3 runs (plan phase recorded in run dir name)
                sub = df[df["run_id"].str.contains("phase3")]
                if len(sub):
                    out[k] = sub
        return out
    return tabs


def manip_summary(model_keys: list[str] | None = None) -> pd.DataFrame:
    """Gender-perception accuracy by cue level (spec §2.2)."""
    rows = []
    for mk in model_keys or MODELS:
        tabs = build_tables(None, model_key=mk)
        m = tabs.get("manip")
        if m is None or m.empty:
            continue
        for lvl in ["name", "name_field", "initial_field", "blind"]:
            sub = m[m["cue_level"] == lvl]
            if sub.empty:
                continue
            if lvl == "blind":
                row = {
                    "model": SHORT.get(mk, mk), "level": LEVEL_NAMES[lvl], "n": len(sub),
                    "pct_female": round(float((sub.perceived_gender == "female").mean()), 3),
                    "pct_male": round(float((sub.perceived_gender == "male").mean()), 3),
                    "pct_unknown": round(float((sub.perceived_gender == "unknown").mean()), 3),
                    "pct_correct": None,
                }
            else:
                row = {
                    "model": SHORT.get(mk, mk), "level": LEVEL_NAMES[lvl], "n": len(sub),
                    "pct_female": round(float((sub.perceived_gender == "female").mean()), 3),
                    "pct_male": round(float((sub.perceived_gender == "male").mean()), 3),
                    "pct_unknown": round(float((sub.perceived_gender == "unknown").mean()), 3),
                    "pct_correct": round(float(sub["correct"].mean()), 3),
                }
            rows.append(row)
    return pd.DataFrame(rows)


def pilot_checks(run_id: str) -> str:
    """§6.4 gate: parse rates, refusals, withholding by cue level, position bias."""
    lines = [f"# Phase-3 pilot checks — {run_id}", ""]
    tabs = build_tables(run_id)
    diag = tabs.get("diagnostics")
    if diag is None or diag.empty:
        return "no diagnostics"
    ok = diag["parse_ok"].fillna(False)
    ref = diag["refusal_flag"].fillna(False)
    lines.append(f"- calls: {len(diag)} | parse ok: {ok.mean():.3f} | refusals: {ref.sum()}")
    lines.append("")
    lines.append("## by experiment x cue level")
    lines.append("")
    g = diag.assign(_ok=ok.astype(float)).groupby(["experiment", diag.get("cue_level", pd.Series("name", index=diag.index)).fillna("name")])
    lines.append(g.agg(n=("call_id", "size"), ok=("_ok", "mean")).round(3).to_markdown())
    lines.append("")
    e1 = tabs.get("e1")
    if e1 is not None and not e1.empty:
        lines.append("## E1 salary withholding ($0) by cue level x family (women)")
        lines.append("")
        w = e1[(e1.gender == "female")].pivot_table(
            index="family_code", columns="cue_level", values="withheld", aggfunc="mean"
        ).round(3)
        lines.append(w.to_markdown())
        lines.append("")
    e2 = tabs.get("e2")
    if e2 is not None and not e2.empty:
        lines.append("## E2 position bias (P(chosen=A)) and P(parent chosen) by cue level")
        lines.append("")
        pb = e2.groupby("cue_level").agg(
            n=("call_id", "size"),
            p_A=("position_a", "mean"),
            p_parent=("parent_chosen", lambda s: np.nanmean(s.astype(float))),
            p_woman=("woman_chosen", lambda s: np.nanmean(s.astype(float))),
        ).round(3)
        lines.append(pb.to_markdown())
        lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------------- §8 reports

def _e2_cell_means(e2: pd.DataFrame, contrasts: list[str], level: str) -> pd.DataFrame:
    sub = e2[(e2.cue_level == level) & (e2.contrast.isin(contrasts))]
    return sub.groupby(["contrast", "gender"])["parent_chosen"].agg(["mean", "size"]).round(3)


def cue_level_penalties(model_key: str) -> pd.DataFrame:
    """§8.2: parent penalty (P(parent chosen)) by gender and cue level + L3."""
    tabs = _tables_for(model_key)
    e2 = tabs.get("e2")
    if e2 is None or e2.empty:
        return pd.DataFrame()
    rows = []
    for lvl in LEVELS:
        sub = e2[(e2.cue_level == lvl) & (e2.contrast.isin(["parent", "parent_gap", "parent_committed",
                                                            "personal", "gap_travel", "gap_parental_only"]))]
        for contrast, g in sub.groupby("contrast"):
            row = {"level": LEVEL_NAMES[lvl], "contrast": contrast, "n": len(g),
                   "P(parent)": round(float(g["parent_chosen"].astype(float).mean()), 3)}
            if lvl != "blind":
                row["gender"] = g["gender"].iloc[0] if g["gender"].notna().all() else None
            rows.append(row)
    return pd.DataFrame(rows)


def gender_preference(model_key: str) -> pd.DataFrame:
    """§8.1: P(woman chosen) in direct contrasts + E1 childless woman-man gap, by level."""
    tabs = _tables_for(model_key)
    rows = []
    e2 = tabs.get("e2")
    if e2 is not None and not e2.empty:
        d = e2[e2.direct]
        for lvl in ["name", "name_field", "initial_field"]:
            for contrast in ["gender_none", "gender_parent"]:
                sub = d[(d.cue_level == lvl) & (d.contrast == contrast)]
                if len(sub):
                    rows.append({
                        "source": f"E2 {contrast}", "level": LEVEL_NAMES[lvl],
                        "stat": "P(woman chosen)", "value": round(float(sub["woman_chosen"].astype(float).mean()), 3),
                        "n": len(sub),
                    })
                    sd = sub["woman_minus_man_starting_salary_usd"].dropna()
                    sd = sd[sd != 0]
                    if len(sd):
                        rows.append({
                            "source": f"E2 {contrast}", "level": LEVEL_NAMES[lvl],
                            "stat": "salary W-M ($, excl withheld)", "value": int(sd.mean()), "n": len(sd),
                        })
    e1 = tabs.get("e1")
    if e1 is not None and not e1.empty:
        for lvl in ["name", "name_field", "initial_field"]:
            sub = e1[(e1.cue_level == lvl) & (e1.family_code == "none")]
            g = sub.groupby("gender").agg(fit=("overall_fit", "mean"), sal=("starting_salary_usd", "mean"))
            if {"female", "male"} <= set(g.index):
                rows.append({"source": "E1 childless", "level": LEVEL_NAMES[lvl],
                             "stat": "fit W-M", "value": round(float(g.loc["female", "fit"] - g.loc["male", "fit"]), 2), "n": len(sub)})
                sal_f = sub[(sub.gender == "female") & (sub.withheld == 0)]["starting_salary_usd"]
                sal_m = sub[(sub.gender == "male") & (sub.withheld == 0)]["starting_salary_usd"]
                rows.append({"source": "E1 childless", "level": LEVEL_NAMES[lvl],
                             "stat": "salary W-M ($)", "value": int(sal_f.mean() - sal_m.mean()), "n": len(sal_f) + len(sal_m)})
    return pd.DataFrame(rows)


def placebo_decomposition(model_key: str) -> pd.DataFrame:
    """§8.3: E2 decomposition per cue level (means of pair clusters at cell level)."""
    tabs = _tables_for(model_key)
    e2 = tabs.get("e2")
    if e2 is None or e2.empty:
        return pd.DataFrame()
    rows = []
    for lvl in ["name", "name_field", "initial_field", "blind"]:
        sub = e2[e2.cue_level == lvl]
        if sub.empty:
            continue
        def pc(contrast, gender=None):
            s = sub[sub.contrast == contrast]
            if gender:
                s = s[s.gender == gender]
            return float(s["parent_chosen"].astype(float).mean()) if len(s) else np.nan
        def boot_se(cells):
            # cluster by résumé pair
            if not len(cells):
                return np.nan
            cl = cells.groupby("resume_ids")["parent_chosen"].mean()
            return float(cl.std(ddof=1) / np.sqrt(len(cl))) if len(cl) > 1 else np.nan
        for gender, glabel in [("female", "mothers"), ("male", "fathers"), (None, "all")]:
            if lvl == "blind" and gender:
                continue
            r = {"level": LEVEL_NAMES[lvl], "group": glabel}
            parent = sub[(sub.contrast == "parent") & ((sub.gender == gender) if gender else True)]
            personal = sub[(sub.contrast == "personal") & ((sub.gender == gender) if gender else True)]
            gap_only = sub[(sub.contrast == "gap_parental_only") & ((sub.gender == gender) if gender else True)]
            travel = sub[(sub.contrast == "gap_travel") & ((sub.gender == gender) if gender else True)]
            parent_gap = sub[(sub.contrast == "parent_gap") & ((sub.gender == gender) if gender else True)]
            r["parenthood (parent-personal)"] = round(pc("parent", gender) - pc("personal", gender), 3)
            r["caregiving (gap_par-gap_travel)"] = round(pc("gap_parental_only", gender) - pc("gap_travel", gender), 3)
            r["bundle (parent_gap-gap_par)"] = round(pc("parent_gap", gender) - pc("gap_parental_only", gender), 3)
            r["se parent cell"] = round(boot_se(parent), 3)
            rows.append(r)
    return pd.DataFrame(rows)


def abstention(model_key: str) -> pd.DataFrame:
    """§8.6: salary withholding + refusals by cue level x family (E1 women)."""
    tabs = _tables_for(model_key)
    e1 = tabs.get("e1")
    if e1 is None or e1.empty:
        return pd.DataFrame()
    sub = e1[e1.gender == "female"]
    pv = sub.pivot_table(index="family_code", columns="cue_level", values="withheld", aggfunc="mean").round(3)
    return pv


def drift(model_key: str) -> pd.DataFrame:
    """§8.7: compare phase-3 L0 anchor cells (none/parent) with the main run."""
    new = _tables_for(model_key).get("e1")
    old = build_tables(None, model_key=model_key).get("e1")
    if new is None or old is None:
        return pd.DataFrame()
    old = old[~old.run_id.str.contains("phase3")]
    rows = []
    for gender in ("female", "male"):
        for fam in ("none", "parent"):
            o = old[(old.gender == gender) & (old.family_code == fam)]
            n = new[(new.gender == gender) & (new.family_code == fam) & (new.cue_level == "name")]
            if len(o) and len(n):
                rows.append({
                    "gender": gender, "family": fam,
                    "main P(interview)": round(float(o["interview"].astype(float).mean()), 3),
                    "phase3 anchor": round(float(n["interview"].astype(float).mean()), 3),
                    "delta": round(float(n["interview"].astype(float).mean() - o["interview"].astype(float).mean()), 3),
                })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(manip_summary().to_string())
