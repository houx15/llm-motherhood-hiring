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


def fig_design(tables, out=OUT, stats_path="docs/report/stats.json"):
    """E2 forest: P(parent chosen) marginal means with pair-clustered 95% CIs."""
    import json as _json

    stats = _json.loads(Path(stats_path).read_text()) if Path(stats_path).exists() else None
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 6.2), sharey=True)
    contrasts = ["parent", "parent_committed", "parent_gap"]
    titles = {"parent": "Parent (PTA cue)", "parent_committed": "Parent + high commitment", "parent_gap": "Parent + leave gap"}
    ylabels, yvals, first = [], [], True
    for ax, contrast in zip(axes, contrasts):
        rows = []
        for m in MODELS:
            for gender in ["female", "male"]:
                if stats:
                    c = stats["models"][m]["e2_clustered"]["cells"][f"{contrast}|{gender}"]
                    p, se, z = c["p"], c["se"], c["z_vs_half"]
                else:  # fallback: naive Wilson
                    e2 = tables[m].get("e2")
                    sub = e2[(e2["contrast"] == contrast) & (e2["gender"] == gender)]
                    p, lo, hi = wilson_ci(sub["parent_chosen"].sum(), len(sub))
                    se, z = (hi - lo) / 3.92, None
                rows.append((SHORT[m], gender, p, 1.96 * se, z))
        ypos = np.arange(len(rows))[::-1]
        for y, (label, gender, p, w, z) in zip(ypos, rows):
            color = COLORS[gender]
            ax.errorbar(p, y, xerr=[[w], [w]], fmt="o", color=color, capsize=2.5, lw=1.2, ms=4.5)
            if z is not None:
                star = "***" if abs(z) > 3.3 else ("**" if abs(z) > 2.6 else ("*" if abs(z) > 2.0 else ""))
                ax.text(min(p + w + 0.02, 0.88), y, star, va="center", fontsize=7, color="0.35")
            if first:
                ylabels.append(f"{label}\n{'women' if gender == 'female' else 'men'}")
                yvals.append(y)
        first = False
        ax.axvline(0.5, color="0.4", ls="--", lw=0.9)
        ax.set_xlim(0, 0.95)
        ax.set_xlabel("P(parent candidate chosen)")
        ax.set_title(titles[contrast])
        ax.grid(axis="x", alpha=0.25)
    axes[0].set_yticks(yvals)
    axes[0].set_yticklabels(ylabels, fontsize=7.5)
    fig.suptitle("Figure 2. Paired comparison (E2): probability the parent candidate is chosen\n"
                 "marginal means ± 95% CI, SEs clustered by résumé pair (40 clusters); * |z|>2, ** >2.6, *** >3.3",
                 y=1.04, fontsize=9.5)
    fig.savefig(out / "fig2_e2_forest.pdf")
    plt.close(fig)


def fig_e1_cells(tables, out=OUT):
    """E1 cell means: interview rate + salary (excluding withheld zeros) by family x gender."""
    order = ["none", "married", "parent", "parent_gap", "parent_committed", "pregnant"]
    fig, axes = plt.subplots(2, 4, figsize=(11.5, 5.2), sharex=True)
    for c, m in enumerate(MODELS):
        e1 = tables[m].get("e1").copy()
        e1.loc[e1["starting_salary_usd"].fillna(0) == 0, "starting_salary_usd"] = np.nan
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
            ax.set_ylabel("Mean salary ($1,000)\n(withheld $0 excluded)")
    fig.suptitle("Figure 3. E1 independent scoring: interview rate and recommended salary by condition", y=1.01)
    fig.tight_layout()
    fig.savefig(out / "fig3_e1_cells.pdf")
    plt.close(fig)


def fig_e3_impact(tables, out=OUT, stats_path="docs/report/stats.json"):
    """E3: top-3 rates per model + naive AND resume-FE-adjusted impact ratios."""
    import json as _json

    stats = _json.loads(Path(stats_path).read_text()) if Path(stats_path).exists() else None
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
        if stats:
            r = stats["models"][m]["e3_fe"]
            naive = [r["F"]["naive_ratio"], r["M"]["naive_ratio"]]
            adj = [r["F"]["adjusted_ratio"], r["M"]["adjusted_ratio"]]
        else:
            naive = adj = [float("nan"), float("nan")]
        ax.plot([i - 0.14, i + 0.14], naive, "o", color="0.62", ms=6, label="naïve" if i == 0 else None)
        ax.plot([i - 0.14, i + 0.14], adj, "s-", color="#6a9f58", ms=6, label="résumé-FE adjusted" if i == 0 else None)
    ax.axhline(0.80, color="darkred", ls="--", lw=1.2)
    ax.text(3.42, 0.805, "four-fifths rule", color="darkred", fontsize=7, ha="right")
    ax.set_xticks(range(len(MODELS)))
    ax.set_xticklabels([SHORT[m].replace("\n", " ") for m in MODELS], fontsize=7)
    ax.set_ylabel("Top-3 impact ratio (parent / childless)\n● naïve  ■ résumé-FE adjusted")
    ax.set_ylim(0, 1.05)
    ax.set_title("Adverse-impact ratios (left = mothers, right = fathers)")
    ax.legend(fontsize=7)
    ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Figure 4. Ranking pools (E3): token parents vs childless candidates", y=1.03)
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
    """Data quality: parse rates; salary withholding; E2 position bias; E3 decay."""
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 6.4))
    names = [SHORT[m].replace("\n", " ") for m in MODELS]
    parse, refusal = [], []
    for m in MODELS:
        diag = tables[m].get("diagnostics")
        eff = diag.assign(_ok=diag["parse_ok"].fillna(False)).groupby("call_id")["_ok"].max()
        parse.append(100 * eff.mean())
        refusal.append(100 * diag["refusal_flag"].fillna(False).mean())
    ax = axes[0, 0]
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
            ax.text(i, 91, f"refusals {r:.1f}%", ha="center", fontsize=6, color="#c25b4e")
    ax = axes[0, 1]
    order = ["none", "married", "parent", "parent_gap", "parent_committed", "pregnant"]
    palette = {"deepseek_v41_flash": "#4e7fc2", "claude_haiku_55": "#c25b4e", "gpt6_luna": "#6a9f58", "qwen38_flash": "#c8a03c"}
    for m in MODELS:
        e1 = tables[m]["e1"]
        w = e1[e1.gender == "female"].copy()
        w["withheld"] = (w["starting_salary_usd"].fillna(0) == 0)
        rates = w.groupby("family_code")["withheld"].mean().reindex([o for o in order if o in set(w.family_code)])
        ax.plot(range(len(rates)), 100 * rates.values, "o-", color=palette[m], ms=4,
                label=SHORT[m].replace("\n", " "))
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([o.replace("_", " ") for o in order], rotation=30, fontsize=6.5)
    ax.set_ylabel("Salary withheld ($0), % of E1 women")
    ax.set_title("Salary withholding by condition")
    ax.legend(fontsize=6.5)
    ax.grid(alpha=0.25)
    ax = axes[1, 0]
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
    ax = axes[1, 1]
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
    fig.suptitle("Figure 6. Data quality, salary withholding, and positional robustness checks", y=1.01)
    fig.tight_layout()
    fig.savefig(out / "fig6_quality.pdf")
    plt.close(fig)


def fig_benchmark(tables, out=OUT, stats_path="docs/report/stats.json"):
    """Benchmark vs Correll et al. (2007): salary % penalty and hire-rate gaps.

    Human benchmark (lab study): recommended hire 84% childless women vs 47% mothers
    (−37pp); salary ≈ −$11,000 (≈ −9%). LLM E2 choice gap is within-decision;
    human hire rate is between-persons — scale caveat in caption.
    """
    import json as _json

    stats = _json.loads(Path(stats_path).read_text()) if Path(stats_path).exists() else None
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.0))
    ax = axes[0]
    xs, labels = [], []
    for m in MODELS:
        if stats:
            d = stats["models"][m]["e2_parent_salary_f"]["pct"]
        else:
            e2 = tables[m].get("e2")
            sub = e2[(e2["contrast"] == "parent") & (e2["gender"] == "female")]
            base = sub[[c for c in sub.columns if c.startswith("A.starting")][0]].mean()
            d = 100 * sub["diff_starting_salary_usd"].mean() / base
        xs.append(d)
        labels.append(SHORT[m].replace("\n", " "))
    ax.bar(labels, xs, color="#c25b4e", width=0.55)
    ax.axhline(-9.3, color="0.2", ls=":", lw=1.4)
    ax.text(1.5, -10.6, "human lab benchmark ≈ −9%\n(Correll et al. 2007)", fontsize=6.5, ha="center")
    ax.set_ylabel("Mother salary penalty (% of childless offer)")
    ax.set_title("E2 mothers: recommended-salary penalty")
    ax.tick_params(axis="x", labelsize=6.5)
    ax.grid(axis="y", alpha=0.25)
    for i, v in enumerate(xs):
        ax.text(i, v - 0.35, f"{v:.1f}%", ha="center", fontsize=7)
    ax = axes[1]
    # hire/choice-rate gap in pp: humans (84−47); LLMs: 100*(0.5 − P(parent chosen))
    gaps = []
    for m in MODELS:
        p = stats["models"][m]["e2_clustered"]["cells"]["parent|female"]["p"] if stats else float("nan")
        gaps.append(100 * (0.5 - p))
    ax.bar(names := [SHORT[m].replace("\n", " ") for m in MODELS], gaps, color="#4e7fc2", width=0.55)
    ax.axhline(37.0, color="0.2", ls=":", lw=1.4)
    ax.text(1.5, 38.2, "human lab benchmark: 84% vs 47%\nrecommended hire (−37pp)", fontsize=6.5, ha="center")
    ax.set_ylabel("Childless-women advantage (pp)")
    ax.set_title("Selection gap: E2 choice (LLMs) vs hire rate (human lab)")
    ax.tick_params(axis="x", labelsize=6.5)
    ax.grid(axis="y", alpha=0.25)
    for i, v in enumerate(gaps):
        ax.text(i, v + 0.6, f"{v:.1f}", ha="center", fontsize=7)
    fig.suptitle("Figure 7. LLM penalties vs human evaluators (Correll et al. 2007). NB: LLM gap is a\n"
                 "within-pair choice share; human gap is a between-persons hire rate — directionally, not metrically, comparable.",
                 y=1.10, fontsize=8.5)
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
