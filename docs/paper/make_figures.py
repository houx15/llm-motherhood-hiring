"""Manuscript figures (docs/paper/figures/*.pdf).

Reads only committed, claim-checked statistics:
  docs/report/stats.json, docs/phase3/round{3,5,6}_stats.json,
  docs/final/coding_stats.json
Run from the repo root:  uv run python docs/paper/make_figures.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SOURCE_DATE_EPOCH", "1761840000")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "docs/paper/figures"
OUT.mkdir(parents=True, exist_ok=True)

INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE = "#2a78d6", "#eb6834"
MODELS_ALL = ["deepseek", "haiku", "luna", "qwen"]
# Main text: three models; Claude Haiku is reported separately (Appendix A).
MODELS = ["deepseek", "luna", "qwen"]
NAME = {"deepseek": "DeepSeek", "haiku": "Haiku", "luna": "Luna", "qwen": "Qwen"}
FULL = {"deepseek": "deepseek_v41_flash", "haiku": "claude_haiku_55",
        "luna": "gpt6_luna", "qwen": "qwen38_flash"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5, "axes.titlesize": 9,
    "axes.labelsize": 8.5, "xtick.labelsize": 8, "ytick.labelsize": 8.5,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
    "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.7, "pdf.fonttype": 42, "legend.frameon": False,
    "axes.titlelocation": "left", "axes.titleweight": "bold",
})


def load(rel):
    return json.load(open(ROOT / rel))


S = load("docs/report/stats.json")
R3 = load("docs/phase3/round3_stats.json")
R5 = load("docs/phase3/round5_stats.json")["primary_decomposition"]
R6 = load("docs/phase3/round6_stats.json")
COD = load("docs/final/coding_stats.json")


def sg(v, nd=1):
    return f"{v:+.{nd}f}".replace("-", "\u2212")


def note(fig, text, y=0.005):
    fig.text(0.01, y, text, fontsize=7.2, color=INK2, ha="left", va="bottom", wrap=True)


def xgrid(ax):
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(OUT / name, metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


# ---------------------------------------------------------------- Figure 1
def fig1_design():
    fig, ax = plt.subplots(figsize=(7.0, 3.3))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
    cols = [
        ("Family signal\n(within the same résumé)",
         ["none (childless baseline)", "parent: children + PTA line",
          "parent + 8-month parental leave", "parent + commitment evidence",
          "pregnant (women only)", "placebo: personal line",
          "placebo: travel gap (same dates)", "placebo: parental leave only"]),
        ("Gender information\n(phase 3)",
         ["L0  gendered first name", "L1  name + \"Gender:\" line",
          "L2  initial + \"Gender:\" line", "L3  initials only (blind)",
          "", "direct woman-vs-man pairs", "(same family status)"]),
        ("Decision task",
         ["E1  score one applicant", "      fit, interview, salary,",
          "      four ratings", "E2  choose 1 of 2 finalists",
          "E3  shortlist 3 of 6", "E4  job-ad wording × leave gap"]),
    ]
    x0s = [0.1, 3.55, 6.85]; widths = [3.2, 3.0, 3.05]
    for (title, items), x0, w in zip(cols, x0s, widths):
        ax.add_patch(FancyBboxPatch((x0, 0.25), w, 4.15, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc="#f4f3f0", ec="#c9c8c2", lw=0.8))
        ax.text(x0 + 0.15, 4.62, title, fontsize=9, fontweight="bold", color=INK, va="center")
        for i, it in enumerate(items):
            ax.text(x0 + 0.18, 4.05 - i * 0.47, it, fontsize=7.8, color=INK, va="center")
    for xa in (3.34, 6.6):
        ax.text(xa, 2.35, "×", fontsize=16, color=INK2, ha="center", va="center")
    note(fig, "Every estimate compares a résumé with itself: the same résumé, occupation, and model with and "
              "without the signal. 4 models × 28 occupations × 154 résumés; 616,419 logged decisions.")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.08)
    save(fig, "fig1_design.pdf")


# ---------------------------------------------------------------- Figure 2
def fig2_scores_vs_choices():
    nm = R6["noise_model2"]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.9), sharey=True)
    for ax, cue, title in zip(axes, ["parent", "parent_gap"],
                              ["a. Parent signal", "b. Parent + parental leave"]):
        for i, m in enumerate(MODELS):
            r = nm[m][cue]; y = len(MODELS) - 1 - i
            ax.plot([r["predicted_P"], r["observed_P"]], [y, y], color="#b9b8b2", lw=1.6, zorder=1)
            ax.scatter(r["predicted_P"], y, s=42, facecolor="white", edgecolor=INK2, lw=1.3, zorder=3)
            ax.scatter(r["observed_P"], y, s=42, color=BLUE, zorder=4)
            d = r["obs_minus_pred"] * 100; lo, hi = (v * 100 for v in r["boot_ci95"])
            xt = min(r["predicted_P"], r["observed_P"]) - 0.02
            ax.text(xt, y + 0.28, f"{sg(d)} [{sg(lo)}, {sg(hi)}]", fontsize=7, color=INK2, ha="left")
        ax.axvline(0.5, color=INK2, ls=(0, (3, 2)), lw=0.8)
        ax.set_xlim(0.05, 0.85); ax.set_ylim(-0.6, len(MODELS) - 0.3)
        ax.set_title(title); xgrid(ax)
        ax.set_xlabel("probability the parent is chosen")
    axes[0].set_yticks(range(len(MODELS))); axes[0].set_yticklabels([NAME[m] for m in reversed(MODELS)])
    axes[1].text(0.51, -0.55, "equal treatment", fontsize=6.8, color=INK2, va="bottom")
    h = [plt.Line2D([], [], marker="o", ls="", mfc="white", mec=INK2, label="predicted from the model's own scores"),
         plt.Line2D([], [], marker="o", ls="", color=BLUE, label="observed in pairwise choice")]
    fig.legend(handles=h, loc="upper right", ncol=2, fontsize=7.5, bbox_to_anchor=(0.99, 1.0))
    note(fig, "Mothers vs. an equally qualified childless woman. Labels: observed − predicted, percentage points "
              "[95% bootstrap CI over résumé pairs]. Prediction converts each model's score gap into a choice "
              "probability using its within-résumé rating noise.")
    fig.subplots_adjust(left=0.1, right=0.99, top=0.84, bottom=0.27, wspace=0.08)
    save(fig, "fig2_scores_vs_choices.pdf")


# ---------------------------------------------------------------- Figure 3
def fig3_decomposition():
    comps = [("interruption", "a. Interruption\ntravel gap vs. 0.5"),
             ("label", "b. Leave label\nparental − travel"),
             ("bundle", "c. Family signals\nparent+leave − leave"),
             ("parenthood", "d. Parenthood\nparent − placebo")]
    fig, axes = plt.subplots(1, 4, figsize=(7.0, 2.8), sharey=True)
    for ax, (c, title) in zip(axes, comps):
        for i, m in enumerate(MODELS):
            y = len(MODELS) - 1 - i
            if c == "interruption":
                cell = R5[m]["cell_gap_travel"]
                d = (cell["P"] - 0.5) * 100; se = d / cell["t_vs_half"]; lo, hi = d - 2.023 * se, d + 2.023 * se
            else:
                r = R5[m][c]; d = r["diff"] * 100; lo, hi = (v * 100 for v in r["ci95"])
            ax.plot([lo, hi], [y, y], color=BLUE, lw=1.6, solid_capstyle="round")
            ax.scatter(d, y, s=30, color=BLUE, zorder=3)
            ax.text(d, y + 0.22, sg(d), fontsize=6.8, color=INK2, ha="center")
        ax.axvline(0, color=INK2, lw=0.8)
        ax.set_xlim(-32, 12); ax.set_xticks([-30, -20, -10, 0, 10]); xgrid(ax)
        ax.set_title(title, fontsize=7.8, fontweight="bold")
    axes[0].set_yticks(range(len(MODELS))); axes[0].set_yticklabels([NAME[m] for m in reversed(MODELS)])
    axes[0].set_ylim(-0.5, len(MODELS) - 0.4)
    fig.supxlabel("change in probability of being chosen (percentage points, 95% CI)", fontsize=8, y=0.11)
    note(fig, "Mothers, 20 main occupations, gender stated explicitly (40 résumé pairs). Negative = the applicant "
              "with the signal is chosen less often. The parental-leave label never adds a penalty (b).")
    fig.subplots_adjust(left=0.11, right=0.99, top=0.83, bottom=0.27, wspace=0.12)
    save(fig, "fig3_decomposition.pdf")


# ---------------------------------------------------------------- Figure 4
def fig4_invariance():
    eq = R6["equivalence"]; lv = load("docs/phase3/phase3_key_stats.json")["cue_level_o8_only"]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.9), gridspec_kw={"width_ratios": [1.05, 1]})
    ax = axes[0]
    rows = [(m, c) for m in MODELS for c in ("parent", "parent_gap")]
    for i, (m, c) in enumerate(rows):
        y = len(rows) - 1 - i
        a_, b_ = lv[m][c]["name"], lv[m][c]["blind"]
        ax.plot([a_, b_], [y, y], color="#b9b8b2", lw=1.4)
        ax.scatter(a_, y, s=34, color=BLUE, zorder=3)
        ax.scatter(b_, y, s=34, marker="D", facecolor="white", edgecolor=INK, lw=1.2, zorder=4)
    ax.axvline(0.5, color=INK2, ls=(0, (3, 2)), lw=0.8)
    ax.text(0.495, len(rows) - 0.45, "equal treatment", fontsize=6.8, color=INK2, ha="right")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{NAME[m]} · {'parent' if c == 'parent' else 'parent + leave'}" for m, c in reversed(rows)], fontsize=7.6)
    ax.set_xlim(0, 0.55); ax.set_ylim(-0.6, len(rows) - 0.2); xgrid(ax)
    ax.set_xlabel("probability the parent is chosen")
    ax.set_title("a. With names vs. with no gender")
    h = [plt.Line2D([], [], marker="o", ls="", color=BLUE, label="gendered names"),
         plt.Line2D([], [], marker="D", ls="", mfc="white", mec=INK, label="initials only (no gender)")]
    ax.legend(handles=h, fontsize=7, loc="lower left", bbox_to_anchor=(0.0, -0.02))
    ax = axes[1]
    ax.axvspan(-5, 5, color="#eef3fb", zorder=0)
    for i, (m, c) in enumerate(rows):
        y = len(rows) - 1 - i
        r = eq[m][f"blind_minus_names_{c}"]; d = r["mean"] * 100; lo, hi = (v * 100 for v in r["ci90"])
        ax.plot([lo, hi], [y, y], color=INK, lw=1.4)
        ax.scatter(d, y, s=26, color=INK, zorder=3)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_xlim(-8, 8); ax.set_ylim(-0.6, len(rows) - 0.2); ax.set_yticks([])
    ax.text(0, len(rows) - 0.45, "±5 points: practically no change", fontsize=6.8, color=INK2, ha="center")
    ax.set_xlabel("no gender − names (points, 90% CI)"); xgrid(ax)
    ax.set_title("b. Difference (equivalence test)")
    note(fig, "Read (a): both markers sit far below 0.5 and almost on top of each other — the parent is penalized just as much when the "
              "model cannot know the applicant's gender. Read (b): an interval inside the shaded band means the difference is statistically "
              "equivalent to zero (two one-sided tests). 8 added occupations, 16 résumé pairs.")
    fig.subplots_adjust(left=0.23, right=0.98, top=0.9, bottom=0.31, wspace=0.1)
    save(fig, "fig5_invariance.pdf")


# ---------------------------------------------------------------- Figure 5
def fig5_direct_gender():
    eq = R6["equivalence"]; levels = ["name", "name_field", "initial_field"]
    lab = ["name", "name\n+ line", "initial\n+ line"]
    fig, axes = plt.subplots(1, len(MODELS), figsize=(6.2, 2.6), sharey=True)
    for ax, m in zip(axes, MODELS):
        for con, col, mk, off, ln in [("gender_none", BLUE, "o", -0.06, "childless woman vs. man"),
                                      ("gender_parent", ORANGE, "s", 0.06, "mother vs. father")]:
            xs, ys = [], []
            for j, lv in enumerate(levels):
                r = eq[m]["direct_parity"][f"{con}@{lv}"]
                p = R3["direct_gender"][m]["parity"][f"{con}@{lv}"]
                v = p["p_woman"]; lo, hi = (0.5 + c for c in r["ci90"])
                x = j + off; xs.append(x); ys.append(v)
                ax.plot([x, x], [lo, hi], color=col, lw=1.4)
                sig = p["holm"] < 0.05
                ax.scatter(x, v, s=26, marker=mk, color=col if sig else "white", edgecolor=col, lw=1.2, zorder=3)
            ax.plot(xs, ys, color=col, lw=0.9, alpha=0.6, label=ln)
        ax.axhline(0.5, color=INK2, ls=(0, (3, 2)), lw=0.8)
        ax.set_title(NAME[m]); ax.set_xticks(range(3)); ax.set_xticklabels(lab, fontsize=6.8)
        ax.set_xlim(-0.4, 2.4); ax.set_ylim(0.44, 0.69)
        ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
    axes[0].set_ylabel("probability the woman is chosen")
    h = [plt.Line2D([], [], marker="o", color=BLUE, label="childless woman vs. childless man"),
         plt.Line2D([], [], marker="s", color=ORANGE, label="mother vs. father")]
    fig.legend(handles=h, loc="upper right", ncol=2, fontsize=7.5, bbox_to_anchor=(0.99, 1.0))
    note(fig, "Both candidates share a family status (56 résumé pairs). 0.5 = no gender preference; above = "
              "women preferred. Filled marker = differs from 0.5 after Holm correction; bars = 90% CI. "
              "\"line\" = explicit \"Gender: Female/Male\" line.")
    fig.subplots_adjust(left=0.09, right=0.99, top=0.8, bottom=0.27, wspace=0.08)
    save(fig, "fig6_direct_gender.pdf")


# ---------------------------------------------------------------- Figure 6
def fig6_withholding():
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw={"width_ratios": [1.6, 1]})
    ax = axes[0]; x = np.arange(len(MODELS_ALL)); w = 0.36
    base = [S["models"][FULL[m]]["withheld"]["rates"]["female|none"] * 100 for m in MODELS_ALL]
    preg = [S["models"][FULL[m]]["withheld"]["rates"]["female|pregnant"] * 100 for m in MODELS_ALL]
    ax.bar(x - w / 2 - 0.01, base, w, color="#9fc3ee", label="childless women")
    ax.bar(x + w / 2 + 0.01, preg, w, color=BLUE, label="pregnant applicants")
    for xi, v in zip(x, preg):
        ax.text(xi + w / 2, v + 0.5, f"{v:.1f}", ha="center", fontsize=7, color=INK2)
    ax.set_xticks(x); ax.set_xticklabels([NAME[m] for m in MODELS_ALL])
    ax.set_ylabel("salary offer withheld (%)"); ax.set_ylim(0, 24)
    ax.set_title("a. Withheld salary offers"); ax.legend(fontsize=7.5, loc="upper right")
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
    ax = axes[1]
    pf = S["models"]["claude_haiku_55"]["pregnancy_full"]["interview_by_withheld"]
    vals = [pf["pregnant|offered"]["rate"] * 100, pf["pregnant|withheld"]["rate"] * 100]
    ns = [pf["pregnant|offered"]["n"], pf["pregnant|withheld"]["n"]]
    ax.bar([0, 1], vals, 0.55, color=[ "#9fc3ee", BLUE])
    for i, (v, n) in enumerate(zip(vals, ns)):
        ax.text(i, v + 2, f"{v:.0f}%\n(n = {n})", ha="center", fontsize=7, color=INK2)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["offer made", "offer withheld"])
    ax.set_ylabel("recommended for interview (%)"); ax.set_ylim(0, 125); ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_title("b. Haiku, pregnant applicants")
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
    note(fig, "Main run, gender conveyed by name. Withholding is a refusal to propose any salary. With an explicit "
              "gender line, Haiku withholds for 27.5% of pregnant applicants.")
    fig.subplots_adjust(left=0.08, right=0.99, top=0.9, bottom=0.2, wspace=0.3)
    save(fig, "figA1_withholding.pdf")


# ---------------------------------------------------------------- Figure 7
def fig7_disparate_impact():
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    pw = np.linspace(0, 1, 401); pm = 0.05; ends = {}
    styles = {"deepseek": (BLUE, "-"), "haiku": (ORANGE, "-"), "luna": ("#1baf7a", "--"), "qwen": ("#6250d6", "-.")}
    for m in MODELS:
        fe = S["models"][FULL[m]]["e3_fe"]; rw, rm = fe["F"]["adjusted_ratio"], fe["M"]["adjusted_ratio"]
        ratio = (pw * rw + (1 - pw)) / (pm * rm + (1 - pm))
        col, ls = styles[m]
        ax.plot(pw * 100, ratio, color=col, ls=ls, lw=1.8)
        below = np.where(ratio < 0.8)[0]
        xc = pw[below[0]] * 100 if len(below) else None
        ends[m] = (ratio[-1], xc)
        if xc is not None:
            ax.scatter(xc, 0.8, s=26, color=col, zorder=4, edgecolor="white", lw=0.8)
    order = sorted(ends, key=lambda k: -ends[k][0]); ys = []
    for k in order:
        y = ends[k][0]
        if ys and ys[-1] - y < 0.05:
            y = ys[-1] - 0.05
        ys.append(y)
        xc = ends[k][1]
        ax.text(101.5, y, f"{NAME[k]} (crosses at {xc:.0f}%)" if xc else NAME[k], fontsize=7.2, color=INK, va="center")
    ax.axhline(0.8, color=INK2, lw=0.9, ls=(0, (3, 2)))
    ax.text(1, 0.808, "four-fifths line", fontsize=7, color=INK2)
    ax.axvline(20, color=GRID, lw=0.8); ax.text(20.5, 1.005, "scenario: 20% of women", fontsize=6.8, color=INK2, va="bottom")
    ax.set_xlim(0, 100); ax.set_ylim(0.6, 1.04)
    ax.set_xlabel("share of women applicants with a caregiving signal (%)  [men fixed at 5%]")
    ax.set_ylabel("women's / men's shortlist rate")
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
    note(fig, "Applies each model's measured shortlist penalty, which is the same for women and men, to pools in "
              "which women carry the signal more often. Below 0.8 = adverse impact under the four-fifths rule.")
    fig.subplots_adjust(left=0.1, right=0.75, top=0.96, bottom=0.27)
    save(fig, "fig8_disparate_impact.pdf")


# ---------------------------------------------------------------- Figure 8
def fig8_reasons():
    sh = COD["shares_losing"]; key = {"deepseek": "deepseek", "haiku": "claude", "luna": "gpt6", "qwen": "qwen38"}
    cues = [("personal", "personal placebo"), ("gap_travel", "travel gap"),
            ("gap_parental_only", "parental leave only"), ("parent", "parent"),
            ("parent_committed", "parent + commitment"), ("parent_gap", "parent + leave")]
    codes = [("gap", "gap"), ("availability", "availability"), ("family", "family"),
             ("disclosure_irrelevant", "'irrelevant'")]
    fig, axes = plt.subplots(1, len(MODELS), figsize=(6.0, 2.9), sharey=True)
    for ax, m in zip(axes, MODELS):
        M = np.array([[sh[key[m]][c][k]["share"] for k, _ in codes] for c, _ in cues]) * 100
        ax.imshow(M, cmap="Blues", vmin=0, vmax=100, aspect="auto")
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                ax.text(j, i, f"{M[i, j]:.0f}", ha="center", va="center", fontsize=6.8,
                        color="white" if M[i, j] > 55 else INK)
        ax.set_xticks(range(len(codes))); ax.set_xticklabels([l for _, l in codes], fontsize=6.6, rotation=35, ha="right", rotation_mode="anchor")
        ax.set_title(NAME[m]); ax.tick_params(length=0)
        for s in ax.spines.values(): s.set_visible(False)
    axes[0].set_yticks(range(len(cues))); axes[0].set_yticklabels([l for _, l in cues], fontsize=7.5)
    note(fig, "Percent of explanations citing each reason when the applicant with the signal lost; 'irrelevant' = calls family information irrelevant (LLM-coded, "
              "exploratory; κ for availability and family is .68/.63 on non-DeepSeek explanations). "
              "Darker = more often cited.")
    fig.subplots_adjust(left=0.2, right=0.99, top=0.91, bottom=0.27, wspace=0.06)
    save(fig, "fig4_reasons.pdf")



# ---------------------------------------------------------------- Figure S2 (R16)
def fig_s2_occupations():
    """Per-occupation leave-gap penalty vs female share, one panel per model.
    Main text: DeepSeek, Luna, Qwen. Appendix variant: Haiku."""
    rows = load("docs/final/occupations.json")
    import matplotlib.pyplot as plt

    panels_main = ["deepseek", "luna", "qwen"]
    for variant, models in [("S2", panels_main), ("S2a_haiku", ["haiku"])]:
        fig, axes = plt.subplots(1, len(models), figsize=(4.6 * len(models), 3.8),
                                 sharey=True, squeeze=False)
        for ax, mk in zip(axes[0], models):
            rs = [r for r in rows if r["model"] == mk and r.get("mother_p") is not None
                  and r.get("female_share") is not None]
            for r in rs:
                x = r["female_share"]
                y = r["mother_p"] - 0.5
                lo = r["mother_ci"][0] - 0.5
                hi = r["mother_ci"][1] - 0.5
                color = "#b08a35" if r["cohort"] == "o8" else "#4e7fc2"
                ax.errorbar(x, y, yerr=[[max(0.0, y - lo)], [max(0.0, hi - y)]],
                            fmt="o", ms=4, color=color, ecolor=color, elinewidth=1, capsize=2)
            ax.axhline(0, color="0.3", ls="--", lw=0.8)
            ax.set_title({"deepseek": "DeepSeek", "luna": "GPT-6 Luna",
                          "qwen": "Qwen3.8", "haiku": "Claude Haiku 5.5"}[mk], fontsize=10)
            ax.set_xlabel("Occupation female share")
            ax.set_ylim(-0.55, 0.15)
        axes[0][0].set_ylabel("Leave-gap penalty, mothers (P chosen \u2212 .5)")
        note(fig, "P(parent+leave gap chosen) vs childless finalist by occupation; 95% CIs clustered by "
                  "r\u00e9sum\u00e9 pair. Blue = original 20 occupations; gold = phase-3 additions.")
        save(fig, f"fig{variant}_occupations.pdf")


# ---------------------------------------------------------------- Supplement S1
def fig_s1_reasons():
    """Supplementary Fig. S1: rationale code shares (fig4_reasons content,
    3 models) for the supplement."""
    import shutil
    from pathlib import Path

    src = Path("docs/report/figures/fig15_coding.pdf")
    if src.exists():
        shutil.copy(src, Path("docs/paper/figures/figS1_reasons.pdf"))
        print("ok figS1_reasons (copied from fig15)")

if __name__ == "__main__":
    # Figures 1 and 9 (framework) are TikZ: docs/paper/figures/tikz/framework.tex
    for f in [fig2_scores_vs_choices, fig3_decomposition, fig4_invariance,
              fig5_direct_gender, fig6_withholding, fig7_disparate_impact, fig8_reasons,
              fig_s2_occupations, fig_s1_reasons]:
        f(); print("ok", f.__name__)
