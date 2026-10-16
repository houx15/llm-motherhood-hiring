"""Publication figures (vector PDF) for the audit report.

Every figure is computed live from the run logs via build_tables(None, model_key=...).
Output: docs/report/figures/*.pdf (matplotlib PDF backend, vector).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..config import RUNS_DIR, load_models
from .build_tables import build_tables
from .stats import Z95, binom_test_phalf, paired_d, wilson_ci

MODELS = ["deepseek_v41_flash", "claude_haiku_55", "gpt6_luna", "qwen38_flash"]
SHORT = {
    "deepseek_v41_flash": "DeepSeek\nV4.1 Flash",
    "claude_haiku_55": "Claude\nHaiku 5.5",
    "gpt6_luna": "GPT-6\nLuna",
    "qwen38_flash": "Qwen3.8\nFlash",
}
COLORS = {"female": "#c25b4e", "male": "#4e7fc2"}
OUT = Path("docs/report/figures")

plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "legend.fontsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "pdf.fonttype": 42,
})


def _tables() -> dict[str, dict]:
    return {m: build_tables(None, model_key=m) for m in MODELS}


def fig_design(tables, out=OUT):
    """E2 forest: P(parent chosen) with Wilson 95% CIs — model x contrast x gender."""
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 6.2), sharey=True)
    contrasts = ["parent", "parent_committed", "parent_gap"]
    titles = {"parent": "Parent (PTA cue)", "parent_committed": "Parent + high commitment", "parent_gap": "Parent + leave gap"}
    ylabels, yvals, first = [], [], True
    for ax, contrast in zip(axes, contrasts):
        rows = []
        for m in MODELS:
            e2 = tables[m].get("e2")
            if e2 is None or e2.empty:
                continue
            for gender in ["female", "male"]:
                sub = e2[(e2["contrast"] == contrast) & (e2["gender"] == gender)]
                n = len(sub)
                k = sub["parent_chosen"].sum()
                p, lo, hi = wilson_ci(k, n)
                pval = binom_test_phalf(int(k), n)
                rows.append((SHORT[m], gender, p, lo, hi, pval, n))
        ypos = np.arange(len(rows))[::-1]
        for y, (label, gender, p, lo, hi, pval, n) in zip(ypos, rows):
            color = COLORS[gender]
            ax.errorbar(p, y, xerr=[[p - lo], [hi - p]], fmt="o", color=color,
                        capsize=2.5, lw=1.2, ms=4.5)
            star = "***" if pval < 0.001 else ("**" if pval < 0.01 else ("*" if pval < 0.05 else ""))
            ax.text(hi + 0.02, y, star, va="center", fontsize=7, color="0.35")
            if first:
                ylabels.append(f"{label}\n{'women' if gender=='female' else 'men'}")
                yvals.append(y)
        first = False
        ax.axvline(0.5, color="0.4", ls="--", lw=0.9)
        ax.set_xlim(0, 0.95)
        ax.set_xlabel("P(parent candidate chosen)")
        ax.set_title(titles[contrast])
        ax.grid(axis="x", alpha=0.25)
    axes[0].set_yticks(yvals)
    axes[0].set_yticklabels(ylabels, fontsize=7.5)
    fig.suptitle("Figure 2. Paired comparison (E2): probability the parent candidate is chosen\n(binomial test vs 0.5; * p<.05, ** p<.01, *** p<.001)", y=1.02, fontsize=10)
    fig.savefig(out / "fig2_e2_forest.pdf")
    plt.close(fig)


def fig_e1_cells(tables, out=OUT):
    """E1 cell means: interview rate + salary by family x gender, per model."""
    order = ["none", "married", "parent", "parent_gap", "parent_committed", "pregnant"]
    fig, axes = plt.subplots(2, 4, figsize=(11.5, 5.2), sharex=True)
    for c, m in enumerate(MODELS):
        e1 = tables[m].get("e1")
        ax = axes[0, c]
        if e1 is not None and not e1.empty:
            piv = e1.groupby(["family_code", "gender"])["interview"].mean().unstack()
            piv = piv.reindex([o for o in order if o in piv.index])
            x = np.arange(len(piv))
            ax.bar(x - 0.2, piv.get("female", pd.Series(dtype=float)), 0.4, color=COLORS["female"], label="women")
            ax.bar(x + 0.2, piv.get("male", pd.Series(dtype=float)), 0.4, color=COLORS["male"], label="men")
            ax.set_ylim(0.5, 1.02)
        ax.set_title(SHORT[m].replace("\n", " "))
        if c == 0:
            ax.set_ylabel("Interview rate")
            ax.legend(loc="lower left")
        ax = axes[1, c]
        if e1 is not None and not e1.empty:
            piv = e1.groupby(["family_code", "gender"])["starting_salary_usd"].mean().unstack()
            piv = piv.reindex([o for o in order if o in piv.index])
            x = np.arange(len(piv))
            ax.bar(x - 0.2, piv.get("female", pd.Series(dtype=float)) / 1000, 0.4, color=COLORS["female"])
            ax.bar(x + 0.2, piv.get("male", pd.Series(dtype=float)) / 1000, 0.4, color=COLORS["male"])
        ax.set_xticks(x)
        lab = [o.replace("_", "\n") for o in (piv.index if piv is not None else [])]
        ax.set_xticklabels(lab, fontsize=6.5)
        if c == 0:
            ax.set_ylabel("Mean salary ($1,000)")
    fig.suptitle("Figure 3. E1 independent scoring: interview rate and recommended salary by condition", y=1.01)
    fig.tight_layout()
    fig.savefig(out / "fig3_e1_cells.pdf")
    plt.close(fig)


def fig_e3_impact(tables, out=OUT):
    """E3: top-3 rates by candidate type per model + impact ratios vs 0.80 line."""
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    ax = axes[0]
    width = 0.38
    cats = [("a", "none", "female"), ("a", "parent", "female"), ("b", "none", "male"), ("b", "parent", "male")]
    labels = ["childless\nwomen", "mother\n(token)", "childless\nmen", "father\n(token)"]
    x = np.arange(len(cats))
    for i, m in enumerate(MODELS):
        e3 = tables[m].get("e3")
        rates = []
        for comp, fam, g in cats:
            sub = e3[e3["composition"] == comp]
            r = sub[(sub["family_code"] == fam) & (sub["gender"] == g)]["top3"].mean()
            rates.append(r)
        ax.bar(x + (i - 1.5) * width / 1.6, rates, width / 1.6, label=SHORT[m].replace("\n", " "))
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("P(top-3 of 6)")
    ax.set_title("Token-parent selection rates (compositions a/b)")
    ax.legend(fontsize=6.5, ncol=2)
    ax.grid(axis="y", alpha=0.25)
    ax = axes[1]
    for i, m in enumerate(MODELS):
        e3 = tables[m].get("e3")
        ratios = []
        for comp, fam, g in [("a", "parent", "female"), ("b", "parent", "male")]:
            sub = e3[e3["composition"] == comp]
            rate = sub.groupby(["family_code", "gender"])["top3"].mean()
            ratios.append(rate.loc[(fam, g)] / rate.loc[("none", g)])
        ax.plot([i - 0.12, i + 0.12], ratios, "o-", color="#6a9f58", ms=6)
        ax.annotate("F" if ratios[1] > ratios[0] else "M", (i + 0.12, ratios[1]), fontsize=7, xytext=(4, 4), textcoords="offset points")
    ax.axhline(0.80, color="darkred", ls="--", lw=1.2)
    ax.text(3.42, 0.805, "four-fifths rule", color="darkred", fontsize=7, ha="right")
    ax.set_xticks(range(len(MODELS)))
    ax.set_xticklabels([SHORT[m].replace("\n", " ") for m in MODELS], fontsize=7)
    ax.set_ylabel("Top-3 impact ratio\n(parent / childless, same gender)")
    ax.set_ylim(0, 1.0)
    ax.set_title("Adverse-impact ratios (● left = mothers, ● right = fathers)")
    ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Figure 4. Ranking pools (E3): token parents vs childless candidates", y=1.02)
    fig.tight_layout()
    fig.savefig(out / "fig4_e3_impact.pdf")
    plt.close(fig)


def fig_e4_context(tables, out=OUT):
    """E4: parent_gap minus none interview gap by JD variant, per model & gender."""
    variants = ["base", "eeo", "family_friendly", "greedy", "greedy_ff"]
    vlabel = ["Base", "EEO", "Family-\nfriendly", "Greedy", "Greedy +\nFF"]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.9), sharey=True)
    for ax, gender in zip(axes, ["female", "male"]):
        for m in MODELS:
            t = tables[m]
            e4 = t.get("e4")
            if e4 is None or e4.empty:
                continue
            cell = e4.groupby(["jd_variant", "gender", "family_code"])["interview"].mean()
            gaps = []
            for v in variants:
                try:
                    gaps.append(100 * (cell.loc[(v, gender, "parent_gap")] - cell.loc[(v, gender, "none")]))
                except KeyError:
                    gaps.append(float("nan"))
            ax.plot(range(len(variants)), gaps, "o-", label=SHORT[m].replace("\n", " "), ms=4.5, lw=1.3)
        ax.axhline(0, color="0.4", lw=0.9)
        ax.set_xticks(range(len(variants)))
        ax.set_xticklabels(vlabel, fontsize=7.5)
        ax.set_title("Mothers (parent_gap − none)" if gender == "female" else "Fathers (parent_gap − none)")
        ax.grid(alpha=0.25)
        ax.set_ylabel("Interview-rate gap (pp)") if gender == "female" else None
    axes[1].legend(fontsize=6.5)
    fig.suptitle("Figure 5. Job-description context (E4): leave-gap interview penalty by JD wording", y=1.03)
    fig.tight_layout()
    fig.savefig(out / "fig5_e4_context.pdf")
    plt.close(fig)


def fig_quality(tables, out=OUT):
    """Data quality: parse/refusal rates; E2 position bias; E3 position decay."""
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.6))
    names = [SHORT[m].replace("\n", " ") for m in MODELS]
    parse, refusal = [], []
    for m in MODELS:
        diag = tables[m].get("diagnostics")
        eff = diag.assign(_ok=diag["parse_ok"].fillna(False)).groupby("call_id")["_ok"].max()
        parse.append(100 * eff.mean())
        refusal.append(100 * diag["refusal_flag"].fillna(False).mean())
    ax = axes[0]
    ax.bar(names, parse, color="#4e7fc2", width=0.6)
    ax.axhline(98, color="darkred", ls="--", lw=1)
    ax.text(0.02, 98.15, "98% acceptance bar", color="darkred", fontsize=6.5, transform=ax.get_yaxis_transform())
    ax.set_ylim(90, 100.5)
    ax.set_ylabel("Valid parse rate (%)")
    ax.set_title("Output validity")
    ax.tick_params(axis="x", labelsize=6.5)
    ax.grid(axis="y", alpha=0.25)
    for i, (p, r) in enumerate(zip(parse, refusal)):
        ax.text(i, p + 0.15, f"{p:.1f}%", ha="center", fontsize=7)
        if r > 0:
            ax.text(i, 91, f"refusals\n{r:.1f}%", ha="center", fontsize=6, color="#c25b4e")
    ax = axes[1]
    posA = []
    for m in MODELS:
        e2 = tables[m].get("e2")
        posA.append(e2["position_a"].mean() if e2 is not None and not e2.empty else float("nan"))
    ax.bar(names, posA, color="#8888aa", width=0.6)
    ax.axhline(0.5, color="0.3", ls="--", lw=1)
    ax.set_ylim(0, 1)
    ax.set_ylabel("P(chosen = A)")
    ax.set_title("E2 first-position preference")
    ax.tick_params(axis="x", labelsize=6.5)
    ax.grid(axis="y", alpha=0.25)
    for i, p in enumerate(posA):
        ax.text(i, p + 0.02, f"{p:.2f}", ha="center", fontsize=7)
    ax = axes[2]
    for m in MODELS:
        e3 = tables[m].get("e3")
        if e3 is None or e3.empty:
            continue
        pos = e3.groupby("position")["top1"].mean()
        ax.plot(pos.index, pos.values, "o-", ms=4, lw=1.2, label=SHORT[m].replace("\n", " "))
    ax.set_xlabel("Screen position (C1…C6)")
    ax.set_ylabel("P(top-1)")
    ax.set_title("E3 position decay")
    ax.legend(fontsize=6.5)
    ax.grid(alpha=0.25)
    fig.suptitle("Figure 6. Data quality and positional robustness checks", y=1.03)
    fig.tight_layout()
    fig.savefig(out / "fig6_quality.pdf")
    plt.close(fig)


def fig_benchmark(tables, out=OUT):
    """E2 mothers: paired effects vs Correll et al. (2007) human benchmark."""
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.0))
    ax = axes[0]
    xs, labels = [], []
    for i, m in enumerate(MODELS):
        e2 = tables[m].get("e2")
        sub = e2[(e2["contrast"] == "parent") & (e2["gender"] == "female")]
        d = 100 * (sub["diff_starting_salary_usd"].mean() / sub["A.starting_salary_usd"].mean()) if "A.starting_salary_usd" in sub else float("nan")
        xs.append(d)
        labels.append(SHORT[m].replace("\n", " "))
    ax.bar(labels, xs, color="#c25b4e", width=0.55)
    ax.axhline(-7.4, color="0.2", ls=":", lw=1.4)
    ax.text(2.9, -7.0, "Human lab benchmark\n(Correll et al. 2007: −7.4%)", fontsize=6.5, ha="center")
    ax.set_ylabel("Mother salary penalty (% of childless offer)")
    ax.set_title("E2 mothers: recommended-salary penalty")
    ax.tick_params(axis="x", labelsize=6.5)
    ax.grid(axis="y", alpha=0.25)
    for i, v in enumerate(xs):
        ax.text(i, v - 0.25, f"{v:.1f}%", ha="center", fontsize=7)
    ax = axes[1]
    ys, ylabels = [], []
    for m in MODELS:
        e2 = tables[m].get("e2")
        sub = e2[(e2["contrast"] == "parent") & (e2["gender"] == "female")]
        d, lo, hi, n = paired_d(sub["diff_commitment"])
        ys.append((d, lo, hi))
        ylabels.append(SHORT[m].replace("\n", " "))
    ypos = np.arange(len(ys))[::-1]
    for y, (d, lo, hi) in zip(ypos, ys):
        ax.errorbar(d, y, xerr=[[d - lo], [hi - d]], fmt="s", color="#6a9f58", capsize=3, ms=5)
    ax.axvline(0, color="0.4", lw=0.9)
    ax.set_yticks(ypos)
    ax.set_yticklabels(ylabels, fontsize=7.5)
    ax.set_xlabel("Paired difference in commitment rating (parent − childless), 95% CI")
    ax.set_title("E2 mothers: commitment penalty")
    ax.grid(axis="x", alpha=0.25)
    fig.suptitle("Figure 7. Benchmarking LLM penalties against human evaluators", y=1.03)
    fig.tight_layout()
    fig.savefig(out / "fig7_benchmark.pdf")
    plt.close(fig)


def fig_moderator(tables, out=OUT):
    """Occupation-level gradients (DeepSeek, full 20-occ E1): leave-gap mother
    interview/salary effect vs standardized female share & time demands."""
    t = tables["deepseek_v41_flash"]
    e1 = t.get("e1")
    if e1 is None or e1.empty:
        return
    for z in ["female_share", "time_demands"]:
        e1[z] = e1.groupby("occupation_id")[z].transform("first")
    sub = e1[e1["family_code"].isin(["none", "parent_gap"])]
    cell = sub.groupby(["occupation_id", "gender", "family_code"])[["interview", "starting_salary_usd"]].mean().reset_index()
    zlook = {z: e1.groupby("occupation_id")[z].first() for z in ["female_share", "time_demands"]}
    td = zlook["time_demands"]
    ztd = (td - td.mean()) / td.std()

    def gap(df, y):
        piv = df.pivot_table(index="occupation_id", columns="family_code", values=y)
        return piv.index, 100 * (piv["parent_gap"] - piv["none"])

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.0))
    ax = axes[0]
    for gender, color, name in [("female", "#c25b4e", "mothers"), ("male", "#4e7fc2", "fathers")]:
        g = cell[cell["gender"] == gender]
        occs, gy = gap(g, "interview")
        zx = [zlook["female_share"].loc[o] for o in occs]
        ax.scatter(zx, gy, s=18, color=color, alpha=0.75, label=name)
        if len(zx) > 2:
            b, a = np.polyfit(zx, gy, 1)
            xs = np.linspace(min(zx), max(zx), 10)
            ax.plot(xs, a + b * xs, color=color, lw=1.2)
    ax.axhline(0, color="0.4", lw=0.9)
    ax.set_xlabel("Occupation female share (raw)")
    ax.set_ylabel("Leave-gap interview penalty (pp)")
    ax.set_title("H4: gender composition gradient")
    ax.legend()
    ax.grid(alpha=0.25)
    ax = axes[1]
    for gender, color, name in [("female", "#c25b4e", "mothers"), ("male", "#4e7fc2", "fathers")]:
        g = cell[cell["gender"] == gender]
        occs, gy = gap(g, "interview")
        xt = [ztd.loc[o] for o in occs]
        ax.scatter(xt, gy, s=18, color=color, alpha=0.75, label=name)
        if len(xt) > 2:
            b, a = np.polyfit(xt, gy, 1)
            xs = np.linspace(min(xt), max(xt), 10)
            ax.plot(xs, a + b * xs, color=color, lw=1.2)
    ax.axhline(0, color="0.4", lw=0.9)
    ax.set_xlabel("Occupation time demands (O*NET composite, z)")
    ax.set_title("H3: greedy-job gradient")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.suptitle("Figure 8. Occupational moderation of the leave-gap interview penalty (DeepSeek, E1)", y=1.03)
    fig.tight_layout()
    fig.savefig(out / "fig8_moderators.pdf")
    plt.close(fig)


def fig_design_schematic(out=OUT):
    """Figure 1: the 2x5+1 factor grid and task sensitivity schematic."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 3.6))
    codes = ["none", "married", "parent", "parent_\ngap", "parent_\ncommitted", "pregnant\n(W only)"]
    ax1.axis("off")
    ax1.set_title("Family-status conditions (cue text identical across genders)", loc="left")
    notes = [
        "not mentioned",
        "\"…married and relocating with my spouse.\"",
        "PTA line + \"married with two children\"",
        "PTA + dated \"Parental leave\" entry",
        "PTA + top-performer / extra-hours bullets",
        "\"…currently pregnant.\"",
    ]
    for i, (c, n) in enumerate(zip(codes, notes)):
        ax1.text(0.02, 0.92 - i * 0.17, f"● {c.replace(chr(10), ' ')}", fontsize=8.5, fontweight="bold", transform=ax1.transAxes)
        ax1.text(0.34, 0.92 - i * 0.17, n, fontsize=7.5, transform=ax1.transAxes, color="0.3")
    tasks = ["E1\nscore one", "E2\nchoose one of two", "E3\nrank six"]
    sizes = [1.4, 2.2, 3.0]
    for i, (t, s) in enumerate(zip(tasks, sizes)):
        ax2.scatter([i], [0], s=s * 260, color=["#c8c8d8", "#8f9fc8", "#4e7fc2"][i], alpha=0.85)
        ax2.text(i, 0, t, ha="center", va="center", fontsize=7.5, color="white", fontweight="bold")
    ax2.set_xlim(-0.6, 2.6)
    ax2.set_ylim(-1.2, 1.4)
    ax2.axis("off")
    ax2.set_title("Discrimination grows with comparison task (circle ∝ penalty magnitude)", loc="left")
    ax2.annotate("", xy=(2.45, -0.85), xytext=(-0.45, -0.85),
                 arrowprops=dict(arrowstyle="->", color="0.35", lw=1.1))
    ax2.text(1.0, -1.05, "relational, not absolute", fontsize=7.5, ha="center", color="0.35")
    fig.suptitle("Figure 1. Design overview", y=1.02)
    fig.tight_layout()
    fig.savefig(out / "fig1_design.pdf")
    plt.close(fig)


def generate_all(out_dir: str | Path = OUT) -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tables = _tables()
    fig_design_schematic(out)
    fig_design(tables, out)
    fig_e1_cells(tables, out)
    fig_e3_impact(tables, out)
    fig_e4_context(tables, out)
    fig_quality(tables, out)
    fig_benchmark(tables, out)
    fig_moderator(tables, out)
    pdfs = sorted(out.glob("*.pdf"))
    print(f"[figures] wrote {len(pdfs)} vector PDFs -> {out}")
    return pdfs
