"""Run reports (markdown + PNG figures)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..budget import TOKEN_EST, Ledger
from ..config import RUNS_DIR
from .build_tables import build_tables
from .models import diagnostics, e1_moderator_regressions, e1_regressions, e2_analysis, e3_analysis

ORDER = ["none", "married", "parent", "parent_gap", "parent_committed", "pregnant"]


def _fmt_p(p):
    return f"{p:.3f}" if p is not None and not np.isnan(p) else "—"


def make_report(run_id: str) -> Path:
    pooled = run_id in ("pooled", "all")
    run_dir = RUNS_DIR / ("pooled" if pooled else run_id)
    figdir = run_dir / "figures"
    figdir.mkdir(parents=True, exist_ok=True)
    tables = build_tables(None if pooled else run_id)
    lines = [f"# {'Pooled' if pooled else 'Run'} report — {run_id}", ""]
    manifest = {}
    if not pooled:
        mf = run_dir / "manifest.json"
        if mf.exists():
            manifest = json.loads(mf.read_text())
            lines += [
                f"- Model: `{manifest.get('model', {}).get('slug')}` · plan: `{manifest.get('plan')}`",
                f"- Calls planned: {manifest.get('plan_calls')} · estimate: ${manifest.get('estimate_usd', 0):.2f}",
            ]
        ledger = Ledger().load()
        run_rows = ledger[ledger["run_id"] == run_id] if not ledger.empty else pd.DataFrame()
        if not run_rows.empty:
            lines.append(f"- Actual ledger cost: ${run_rows['cost_usd'].sum():.2f}")
    else:
        lines.append("- Aggregates ALL runs' logs (deduped by call_id, valid parses kept)")
    lines.append("")

    diag = tables.get("diagnostics", pd.DataFrame())

    # ---- 1. parse / refusal ----
    lines += ["## 1. Parse & refusal rates", ""]
    if not diag.empty:
        agg = (
            diag.assign(
                parse_ok=diag["parse_ok"].fillna(False),
                refusal=diag["refusal_flag"].fillna(False),
            )
            .groupby("experiment")
            .agg(n=("call_id", "count"), parse_ok=("parse_ok", "mean"), refusal=("refusal", "mean"))
        )
        lines += ["| exp | calls | parse ok | refusal |", "| --- | --- | --- | --- |"]
        for exp, r in agg.iterrows():
            lines.append(f"| {exp} | {int(r.n)} | {r.parse_ok:.1%} | {r.refusal:.1%} |")
        by_c = (
            diag.assign(
                parse_ok=diag["parse_ok"].fillna(False), refusal=diag["refusal_flag"].fillna(False)
            )
            .groupby(["experiment", "gender", "family_code"])
            .agg(parse_ok=("parse_ok", "mean"), refusal=("refusal", "mean"))
            .reset_index()
        )
        worst_ref = by_c.sort_values("refusal", ascending=False).head(5)
        lines += ["", "Highest-refusal cells:", ""]
        lines += ["| exp | gender | family | refusal |", "| --- | --- | --- | --- |"]
        for _, r in worst_ref.iterrows():
            if r.refusal > 0:
                lines.append(f"| {r.experiment} | {r.gender} | {r.family_code} | {r.refusal:.1%} |")
    lines.append("")

    # ---- 2. E1 outcomes & distributions ----
    e1 = tables.get("e1")
    if e1 is not None and not e1.empty:
        lines += ["## 2. E1 — independent scoring", ""]
        cell = (
            e1.groupby(["gender", "family_code"])
            .agg(
                n=("overall_fit", "size"),
                fit=("overall_fit", "mean"),
                interview=("interview", "mean"),
                salary=("starting_salary_usd", "mean"),
                commit=("commitment", "mean"),
                sd_fit=("overall_fit", lambda s: s.std(ddof=1)),
            )
            .reindex(pd.MultiIndex.from_product(
                [["female", "male"], [c for c in ORDER if c in set(e1['family_code'])]],
                names=["gender", "family_code"],
            ))
            .dropna(how="all")
            .reset_index()
        )
        lines += [
            "### Cell means (pilot occupations pooled)",
            "",
            "| gender | family | n | fit | interview | salary | commitment | SD(fit) |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for _, r in cell.iterrows():
            lines.append(
                f"| {r.gender} | {r.family_code} | {int(r.n)} | {r.fit:.2f} | {r.interview:.1%} | "
                f"${r.salary:,.0f} | {r.commit:.2f} | {r.sd_fit:.2f} |"
            )
        lines += ["", "Ceiling check: share of responses at scale maximum.", ""]
        ceil = e1.assign(
            fit10=(e1["overall_fit"] == 10).mean() if len(e1) else np.nan,
        )
        for y, mx in [("overall_fit", 10), ("interview", 1), ("commitment", 7), ("likability", 7)]:
            share = (e1[y] == mx).mean()
            lines.append(f"- {y}: {share:.1%} at max")
        lines.append("")

        # figure: outcomes by gender x family
        fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))
        for ax, (y, title, fmt) in zip(
            axes,
            [("interview", "Interview rate", "{:.0%}"), ("starting_salary_usd", "Mean salary (USD)", "${:,.0f}"), ("commitment", "Commitment (1-7)", "{:.1f}")],
        ):
            piv = e1.groupby(["family_code", "gender"])[y].mean().unstack()
            piv = piv.reindex([c for c in ORDER if c in piv.index])
            piv.plot.bar(ax=ax, legend=(ax == axes[0]), color=["#c25b4e", "#4e7fc2"])
            ax.set_title(title)
            ax.set_xlabel("")
            ax.tick_params(axis="x", rotation=30)
            if y == "interview":
                ax.set_ylim(0, 1)
            ax.grid(axis="y", alpha=0.3)
        fig.suptitle("E1 outcomes by family status x gender (pilot)")
        fig.tight_layout()
        fig.savefig(figdir / "e1_outcomes.png", dpi=150)
        plt.close(fig)

        # figure: rating distributions
        fig, axes = plt.subplots(1, 4, figsize=(14, 3.2), sharey=False)
        for ax, y in zip(axes, ["overall_fit", "competence", "commitment", "likability"]):
            data = [e1[e1["family_code"] == c][y].dropna() for c in ORDER if c in set(e1["family_code"])]
            labels = [c for c in ORDER if c in set(e1["family_code"])]
            ax.boxplot(data, tick_labels=labels, showmeans=True)
            ax.set_title(y)
            ax.tick_params(axis="x", rotation=45)
            ax.grid(axis="y", alpha=0.3)
        fig.suptitle("E1 score distributions by family code (ceiling check)")
        fig.tight_layout()
        fig.savefig(figdir / "e1_distributions.png", dpi=150)
        plt.close(fig)

        # regression table
        reg = e1_regressions(e1[~e1["family_code"].isna()])
        if not reg.empty and "error" not in reg.columns:
            lines += [
                "### E1 regression: Y ~ family * female + resume FE (+ occupation FE), cluster SE",
                "",
                "| outcome | term | coef | SE | p | n |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
            for _, r in reg.iterrows():
                lines.append(
                    f"| {r['outcome']} | {r['term']} | {r['coef']:+.3f} | {r['se']:.3f} | {_fmt_p(r['pvalue'])} | {int(r['n'])} |"
                )
            lines.append("")
        lines += ["![E1 outcomes](figures/e1_outcomes.png)", "", "![E1 distributions](figures/e1_distributions.png)", ""]

        # ---- moderator regressions (spec §10; needs >= 10 occupations) ----
        mod_reg = e1_moderator_regressions(e1[~e1["family_code"].isna()])
        if mod_reg is not None and not mod_reg.empty:
            if "note" in mod_reg.columns:
                lines += [f"*Moderator regressions: {mod_reg['note'].iloc[0]}*", ""]
            elif not mod_reg.empty:
                lines += [
                    "### Occupation-moderator regressions (H3/H4):",
                    "Y ~ family * female * Z + resume FE, cluster SE; Z standardized (female_share / median_wage / time_demands)",
                    "",
                    "| Z | outcome | term | coef | SE | p | n |",
                    "| --- | --- | --- | --- | --- | --- | --- |",
                ]
                for _, r in mod_reg.iterrows():
                    lines.append(
                        f"| {r.get('Z','')} | {r['outcome']} | {r['term']} | {r['coef']:+.4f} | "
                        f"{r['se']:.4f} | {_fmt_p(r['pvalue'])} | {int(r['n'])} |"
                    )
                lines.append("")

    # ---- 3. E2 ----
    e2 = tables.get("e2")
    if e2 is not None and not e2.empty:
        lines += ["## 3. E2 — paired comparison", ""]
        res = e2_analysis(e2)
        rates = res.get("parent_choice_rates")
        if rates is not None and not rates.empty:
            lines += ["Parent-candidate share chosen (0.5 = no bias):", "",
                      "| contrast | gender | P(parent chosen) | n |", "| --- | --- | --- | --- |"]
            for _, r in rates.iterrows():
                lines.append(f"| {r['contrast']} | {r['gender']} | {r['mean']:.3f} | {int(r['count'])} |")
            lines.append("")
        pos = res.get("position_bias")
        if pos is not None and not pos.empty:
            lines.append(f"Position bias — P(chosen = A) = {pos['share_chosen_A'].iloc[0]:.3f} (0.5 = none).")
            lines.append("")
        diffs = res.get("paired_diffs")
        if diffs is not None and not diffs.empty:
            lines += ["Paired differences (parent − childless):", "",
                      "| metric | contrast | gender | mean diff | t | n |", "| --- | --- | --- | --- | --- | --- |"]
            for _, r in diffs.iterrows():
                lines.append(f"| {r['metric']} | {r['contrast']} | {r['gender']} | {r['mean_diff_parent_minus_childless']:+.2f} | {r['t']:+.2f} | {int(r['n'])} |")
            lines.append("")
        fig, ax = plt.subplots(figsize=(6.5, 3.6))
        if rates is not None and not rates.empty:
            piv = rates.pivot(index="contrast", columns="gender", values="mean").reindex(
                ["parent", "parent_gap", "parent_committed"]
            )
            piv.plot.bar(ax=ax, color=["#c25b4e", "#4e7fc2"])
            ax.axhline(0.5, color="gray", ls="--", lw=1)
            ax.set_ylim(0, 1)
            ax.set_ylabel("P(parent chosen)")
            ax.set_xlabel("")
            ax.grid(axis="y", alpha=0.3)
        fig.suptitle("E2 parent-choice rate by contrast x gender")
        fig.tight_layout()
        fig.savefig(figdir / "e2_choice.png", dpi=150)
        plt.close(fig)
        lines += ["![E2 choice](figures/e2_choice.png)", ""]

    # ---- 4. E3 ----
    e3 = tables.get("e3")
    if e3 is not None and not e3.empty:
        lines += ["## 4. E3 — ranking pools", ""]
        res = e3_analysis(e3)
        sel = res.get("selection_rates")
        if sel is not None and not sel.empty:
            lines += ["Top-1 / Top-3 rates by candidate type:", "",
                      "| composition | gender | family | top1 | top3 |", "| --- | --- | --- | --- | --- |"]
            for _, r in sel.iterrows():
                lines.append(f"| {r['composition']} | {r['gender']} | {r['family_code']} | {r['top1']:.3f} | {r['top3']:.3f} |")
            lines.append("")
        ff = res.get("four_fifths")
        if ff is not None and not ff.empty:
            lines += ["Four-fifths (adverse impact) check:", "",
                      "| group | top3 rate | childless ref | impact ratio |", "| --- | --- | --- | --- |"]
            for _, r in ff.iterrows():
                lines.append(f"| {r['group']} (comp {r['composition']}) | {r['top3_rate']:.3f} | {r['childless_rate']:.3f} | {r['impact_ratio']:.2f} |")
            lines.append("")
        pos = res.get("position_bias")
        if pos is not None and not pos.empty:
            lines += ["Position bias (top-1 rate by screen label C1..C6): " + ", ".join(f"C{int(r['position'])}={r['top1']:.2f}" for _, r in pos.iterrows())]
            lines.append("")
        fig, ax = plt.subplots(figsize=(6.5, 3.6))
        if sel is not None and not sel.empty:
            key = sel.assign(cat=sel["family_code"] + " " + sel["gender"].str[:1])
            piv = key.groupby("cat")["top3"].mean()
            piv.plot.bar(ax=ax, color="#6a9f58")
            ax.set_ylabel("P(top-3)")
            ax.grid(axis="y", alpha=0.3)
            ax.tick_params(axis="x", rotation=45)
        fig.suptitle("E3 top-3 inclusion by candidate type")
        fig.tight_layout()
        fig.savefig(figdir / "e3_top3.png", dpi=150)
        plt.close(fig)
        lines += ["![E3 top3](figures/e3_top3.png)", ""]

    # ---- 5. E4 ----
    e4 = tables.get("e4")
    if e4 is not None and not e4.empty:
        lines += ["## 5. E4 — JD context", ""]
        piv = (
            e4[e4["family_code"].isin(["none", "parent", "parent_gap"])]
            .groupby(["jd_variant", "gender", "family_code"])[["interview", "starting_salary_usd", "commitment"]]
            .mean()
            .reset_index()
        )
        lines += ["| JD variant | gender | family | interview | salary | commitment |", "| --- | --- | --- | --- | --- | --- |"]
        for _, r in piv.iterrows():
            lines.append(f"| {r['jd_variant']} | {r['gender']} | {r['family_code']} | {r['interview']:.1%} | ${r['starting_salary_usd']:,.0f} | {r['commitment']:.2f} |")
        lines.append("")
        fig, ax = plt.subplots(figsize=(7.5, 3.8))
        mother_cost = (
            e4[e4["family_code"].isin(["none", "parent"])]
            .groupby(["jd_variant", "gender", "family_code"])["interview"].mean().reset_index()
        )
        gaps = {}
        for jd in mother_cost["jd_variant"].unique():
            sub = mother_cost[mother_cost["jd_variant"] == jd]
            for g in ["female", "male"]:
                base = sub[(sub["family_code"] == "none") & (sub["gender"] == g)]["interview"]
                par = sub[(sub["family_code"] == "parent") & (sub["gender"] == g)]["interview"]
                if len(base) and len(par):
                    gaps[(jd, g)] = float(par.iloc[0] - base.iloc[0]) * 100
        if gaps:
            gd = pd.Series(gaps).unstack()
            gd.plot.bar(ax=ax, color=["#c25b4e", "#4e7fc2"])
            ax.axhline(0, color="gray", lw=1)
            ax.set_ylabel("parent − childless interview rate (pp)")
            ax.set_xlabel("")
            ax.grid(axis="y", alpha=0.3)
            ax.tick_params(axis="x", rotation=20)
            fig.suptitle("E4: parenthood gap in interview rate by JD variant")
            fig.tight_layout()
            fig.savefig(figdir / "e4_gap.png", dpi=150)
        plt.close(fig)
        lines += ["![E4 gap](figures/e4_gap.png)", ""]

    # ---- 6. rationale keyword rate + within-cell SD ----
    d = diagnostics(diag)
    if "rationale_family_mention" in d:
        s = d["rationale_family_mention"]
        lines += ["## 6. Rationale mentions of family cues", "",
                  "| exp | family | share of rationales mentioning family |", "| --- | --- | --- |"]
        for (exp, fam), v in s.items():
            lines.append(f"| {exp} | {fam} | {v:.1%} |")
        lines.append("")
    if e1 is not None and not e1.empty:
        sd = e1.groupby(["gender", "family_code"])["overall_fit"].std(ddof=1)
        lines += [f"Within-cell SD (overall_fit): median {sd.median():.2f}, min {sd.min():.2f}, max {sd.max():.2f}.", ""]

    # ---- 7. Phase 1 cost estimate from measured tokens ----
    lines += ["## 7. Measured tokens & Phase 1 cost estimate", ""]
    if not diag.empty:
        tok = diag[diag["input_tokens"].notna()]
        for exp, g in tok.groupby("experiment"):
            lines.append(
                f"- {exp}: mean input {g['input_tokens'].mean():.0f}, mean output {g['output_tokens'].mean():.0f} (n={len(g)})"
            )
        lines.append("")
        import pandas as _pd
        man = manifest
        pin = man.get("pricing", {}).get("input_per_mtok")
        pout = man.get("pricing", {}).get("output_per_mtok")
        if pin and pout:
            counts = {"e1": 13200, "e2": 14400, "e3": 5760, "e4": 14400}
            total = 0.0
            for exp, g in tok.groupby("experiment"):
                if exp in counts:
                    est = counts[exp] * (g["input_tokens"].mean() * pin + g["output_tokens"].mean() * pout) / 1e6
                    total += est
                    lines.append(f"- Phase 1 {exp}: ~${est:.2f}")
            lines.append(f"- **Phase 1 (DeepSeek full E1–E4) total: ~${total:.2f} at run pricing**")
            lines.append("")

    out = run_dir / "report.md"
    out.write_text("\n".join(lines))
    print(f"[report] {out}")
    return out
