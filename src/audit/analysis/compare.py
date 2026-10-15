"""Cross-model comparison: same design, different models (spec §10 'pooled and
separately per LLM'). Produces one compact table + figure of the headline
motherhood/fatherhood effects per model."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from ..config import RUNS_DIR, load_models
from .build_tables import build_tables

SLUG_NAMES = {m.key: m.slug for m in load_models().models}


def _per_model_effects(model_key: str) -> dict:
    t = build_tables(None, model_key=model_key)
    out: dict = {"model_key": model_key, "slug": SLUG_NAMES.get(model_key)}
    e2 = t.get("e2")
    if e2 is not None and not e2.empty:
        for contrast in ["parent", "parent_gap", "parent_committed"]:
            for gender in ["female", "male"]:
                sub = e2[(e2["contrast"] == contrast) & (e2["gender"] == gender)]
                out[f"e2_P_parent_{contrast}_{gender}"] = sub["parent_chosen"].mean() if len(sub) else float("nan")
        out["e2_pos_bias_A"] = e2["position_a"].mean() if "position_a" in e2 else float("nan")
        out["e2_salary_gap_mother"] = e2[(e2.contrast == "parent") & (e2.gender == "female")][
            "diff_starting_salary_usd"
        ].mean()
        out["e2_salary_gap_father"] = e2[(e2.contrast == "parent") & (e2.gender == "male")][
            "diff_starting_salary_usd"
        ].mean()
    e3 = t.get("e3")
    if e3 is not None and not e3.empty:
        for comp, fam, g in [("a", "parent", "female"), ("b", "parent", "male")]:
            sub = e3[e3["composition"] == comp]
            rate = sub.groupby(["family_code", "gender"])["top3"].mean()
            try:
                out[f"e3_impact_{fam}_{g}"] = rate.loc[(fam, g)] / rate.loc[("none", g)]
            except KeyError:
                pass
        pos = e3.groupby("position")["top1"].mean()
        out["e3_pos_C1"] = pos.get(1, float("nan"))
        out["e3_pos_C6"] = pos.get(6, float("nan"))
    e14 = t.get("e1_e4")
    if e14 is not None and not e14.empty:
        e1 = e14[e14["experiment"] == "e1"]
        for y, key in [("interview", "e1_interview"), ("starting_salary_usd", "e1_salary"), ("commitment", "e1_commit")]:
            cell = e1.groupby(["gender", "family_code"])[y].mean()
            try:
                out[f"{key}_mother_none_diff"] = cell.loc[("female", "parent")] - cell.loc[("female", "none")]
                out[f"{key}_father_none_diff"] = cell.loc[("male", "parent")] - cell.loc[("male", "none")]
                out[f"{key}_gapmother_none_diff"] = cell.loc[("female", "parent_gap")] - cell.loc[("female", "none")]
            except KeyError:
                continue
        e4 = e14[e14["experiment"] == "e4"]
        if not e4.empty:
            cell4 = e4.groupby(["jd_variant", "gender", "family_code"])["interview"].mean()
            try:
                out["e4_greedy_gap_mother_pp"] = 100 * (
                    cell4.loc[("greedy", "female", "parent_gap")] - cell4.loc[("greedy", "female", "none")]
                )
                out["e4_greedy_gap_father_pp"] = 100 * (
                    cell4.loc[("greedy", "male", "parent_gap")] - cell4.loc[("greedy", "male", "none")]
                )
            except KeyError:
                pass
    # diagnostics
    diag = t.get("diagnostics")
    if diag is not None and not diag.empty:
        eff = diag.assign(_ok=diag["parse_ok"].fillna(False)).groupby("call_id")["_ok"].max()
        out["parse_ok"] = eff.mean()
        out["refusal"] = diag["refusal_flag"].fillna(False).mean()
    return out


def compare_models(out_dir: Path | None = None) -> pd.DataFrame:
    rows = []
    for f in sorted(RUNS_DIR.glob("*/logs.jsonl")):
        keys = set()
        for line in f.read_text().splitlines():
            try:
                keys.add(json.loads(line).get("model_key"))
            except json.JSONDecodeError:
                continue
        rows.extend(k for k in keys if k)
    model_keys = sorted(set(rows))
    table = pd.DataFrame([_per_model_effects(k) for k in model_keys])
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        table.to_csv(out_dir / "model_comparison.csv", index=False)
        _figure(table, out_dir)
    return table


def _figure(table: pd.DataFrame, out_dir) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    x = range(len(table))
    labels = [r["slug"].split("/")[-1] for _, r in table.iterrows()]
    ax = axes[0]
    w = 0.35
    ax.bar([i - w / 2 for i in x], table.get("e2_P_parent_parent_female", float("nan")), w, label="mothers", color="#c25b4e")
    ax.bar([i + w / 2 for i in x], table.get("e2_P_parent_parent_male", float("nan")), w, label="fathers", color="#4e7fc2")
    ax.axhline(0.5, color="gray", ls="--", lw=1)
    ax.set_xticks(list(x)); ax.set_xticklabels(labels, rotation=15)
    ax.set_ylabel("E2: P(parent chosen)"); ax.set_ylim(0, 1); ax.legend()
    ax.set_title("Parenthood penalty (PTA cue)")
    ax = axes[1]
    ax.bar([i - w / 2 for i in x], table.get("e2_P_parent_parent_gap_female", float("nan")), w, label="mothers", color="#c25b4e")
    ax.bar([i + w / 2 for i in x], table.get("e2_P_parent_parent_gap_male", float("nan")), w, label="fathers", color="#4e7fc2")
    ax.axhline(0.5, color="gray", ls="--", lw=1)
    ax.set_xticks(list(x)); ax.set_xticklabels(labels, rotation=15)
    ax.set_ylabel("E2: P(parent chosen)"); ax.set_ylim(0, 1)
    ax.set_title("Leave-gap penalty")
    ax = axes[2]
    ax.bar([i - w / 2 for i in x], table.get("e3_impact_parent_female", float("nan")), w, label="mothers", color="#c25b4e")
    ax.bar([i + w / 2 for i in x], table.get("e3_impact_parent_male", float("nan")), w, label="fathers", color="#4e7fc2")
    ax.axhline(0.80, color="darkred", ls="--", lw=1, label="four-fifths line")
    ax.set_xticks(list(x)); ax.set_xticklabels(labels, rotation=15)
    ax.set_ylabel("E3: top-3 impact ratio"); ax.legend()
    ax.set_title("Token-parent adverse impact")
    for ax in axes:
        ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "model_comparison.png", dpi=150)
    plt.close(fig)
