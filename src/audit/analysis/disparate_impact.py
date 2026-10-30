"""Phase-4 Part D: from caregiver penalty back to a gender gap (scenario analysis).

Layer 1 is gender-neutral in form. But caregiving interruptions and visible
family signals are carried disproportionately by women in real applicant
pools. Combining gender-specific signal prevalence (sourced where possible,
scenario otherwise) with each model's measured penalties yields the implied
women/men shortlist ratio and whether it crosses the four-fifths line.

Model: pools of 6 (50% women); every candidate shortlisted (top-3) with a
gender-neutral base rate p0 equal to the measured childless top-3 rate;
signal-carriers shortlisted at p0 x impact ratio (E3 résumé-FE adjusted:
mothers' ratio for women, fathers' for men). Selection ratio =
E[P(shortlist | woman)] / E[P(shortlist | man)]; four-fifths line = 0.80.

Outputs: docs/phase4/disparate_impact.md, docs/report/figures/fig14_disparate_impact.pdf,
config/prevalence.yaml (sourced values with citations).
"""
from __future__ import annotations

import json
import os

os.environ.setdefault("SOURCE_DATE_EPOCH", "1761840000")  # deterministic PDFs

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..config import ROOT

matplotlib.use("Agg")

MODELS = ["deepseek_v41_flash", "claude_haiku_55", "gpt6_luna", "qwen38_flash"]
SHORT = {"deepseek_v41_flash": "DeepSeek", "claude_haiku_55": "Haiku",
         "gpt6_luna": "Luna", "qwen38_flash": "Qwen"}


def measured_inputs() -> dict:
    s = json.load(open(ROOT / "docs/report/stats.json"))
    out = {}
    for m in MODELS:
        fe = s["models"][m]["e3_fe"]
        out[m] = {
            "ratio_women": fe["F"]["adjusted_ratio"],
            "ratio_men": fe["M"]["adjusted_ratio"],
            "childless_top3_base": fe.get("childless_top3_base_0_3", 0.48),
        }
    return out


def implied_selection_ratio(p_w: float, p_m: float, ratio_w: float, ratio_m: float) -> float:
    """E[P(shortlist|woman)] / E[P(shortlist|man)] under the Part-D model
    (common base rate cancels)."""
    num = p_w * ratio_w + (1 - p_w)
    den = p_m * ratio_m + (1 - p_m)
    return num / den


def load_prevalence() -> dict:
    import yaml

    p = ROOT / "config" / "prevalence.yaml"
    if not p.exists():
        return {"women": None, "men": None, "source_note": "scenario parameters (no sourced value)"}
    return yaml.safe_load(p.read_text())


def main() -> None:
    inputs = measured_inputs()
    prev = load_prevalence()
    pw_grid = np.linspace(0.05, 0.40, 36)
    pm_grid = np.linspace(0.01, 0.15, 36)

    # sourced point (or None)
    sourced = None
    if prev.get("women") is not None and prev.get("men") is not None:
        sourced = (float(prev["women"]), float(prev["men"]))

    lines = ["# Phase 4 Part D — From caregiver penalty back to a gender gap (scenario analysis)",
             "",
             "Layer 1 of the penalty is gender-neutral in form (blind = names-only in every",
             "model). This analysis asks what it *does* to women and men in expectation",
             "when caregiving signals are not gender-neutrally distributed. Model: pools of",
             "six, 50% women; every candidate shortlisted with the model's measured",
             "gender-neutral childless top-3 base rate; signal-carriers at that base × the",
             "model's E3 résumé-FE adjusted impact ratio (mothers' ratio for women,",
             "fathers' for men). Implied selection ratio = E[P(shortlist | woman)] /",
             "E[P(shortlist | man)]; the EEOC four-fifths line is 0.80.",
             "",
             "**Label: scenario analysis.** Signal prevalence by gender is a scenario",
             f"parameter unless sourced. Current inputs: {prev.get('source_note', 'scenario')}.",
             "",
             "## Implied women/men selection ratios at the scenario point (women 20%, men 5%)",
             "",
             "| model | mothers' ratio | fathers' ratio | implied W/M selection ratio | four-fifths |",
             "| --- | --- | --- | --- | --- |"]
    scenario = (0.20, 0.05)
    for m in MODELS:
        r = implied_selection_ratio(scenario[0], scenario[1],
                                    inputs[m]["ratio_women"], inputs[m]["ratio_men"])
        lines.append(f"| {SHORT[m]} | {inputs[m]['ratio_women']:.2f} | {inputs[m]['ratio_men']:.2f} "
                     f"| **{r:.3f}** | {'VIOLATION' if r < 0.8 else 'pass'} |")
    if sourced:
        lines += ["", f"Sourced prevalence point ({sourced[0]:.0%} women, {sourced[1]:.0%} men):"]
        for m in MODELS:
            r = implied_selection_ratio(sourced[0], sourced[1],
                                        inputs[m]["ratio_women"], inputs[m]["ratio_men"])
            lines.append(f"- {SHORT[m]}: {r:.3f} ({'VIOLATION' if r < 0.8 else 'pass'})")
    # threshold prevalence: women's prevalence at which each model crosses 0.80 (men fixed 5%)
    lines += ["", "## Women's signal prevalence at which the four-fifths line is crossed (men at 5%)", ""]
    for m in MODELS:
        rw, rm = inputs[m]["ratio_women"], inputs[m]["ratio_men"]
        cross = None
        for pw in np.linspace(0.01, 1.0, 200):
            if implied_selection_ratio(pw, 0.05, rw, rm) < 0.80:
                cross = pw
                break
        lines.append(f"- {SHORT[m]}: " + (f"crosses at women's prevalence ≥ {cross:.0%}" if cross
                                          else "does not cross within 0–100%"))
    lines += ["",
              "Interpretation: because Haiku's Layer-1 penalty is severe, even modest",
              "gender asymmetry in signal prevalence produces a disparate-impact violation",
              "from a formally gender-neutral rule. With equal prevalence (5%/5%) no model",
              "crosses the line — the entire implied gender gap is the prevalence",
              "asymmetry interacting with a gender-blind penalty.",
              "", "Regenerate: `uv run python -m audit.analysis.disparate_impact`.", ""]
    out = ROOT / "docs" / "phase4" / "disparate_impact.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    thresholds = {}
    for m in MODELS:
        rw, rm = inputs[m]["ratio_women"], inputs[m]["ratio_men"]
        cross = None
        for pw in np.linspace(0.01, 1.0, 200):
            if implied_selection_ratio(pw, 0.05, rw, rm) < 0.80:
                cross = round(float(pw), 3)
                break
        thresholds[SHORT[m]] = {"crossing_womens_prevalence": cross,
                                "ratio_women": rw, "ratio_men": rm,
                                "scenario_20_5": round(implied_selection_ratio(0.20, 0.05, rw, rm), 3)}
    import json as _j
    fdir = ROOT / "docs" / "final"
    fdir.mkdir(parents=True, exist_ok=True)
    (fdir / "disparate_impact_stats.json").write_text(_j.dumps(thresholds, indent=1))
    out.write_text("\n".join(lines))

    # heatmap figure (2x2 per model)
    fig, axes = plt.subplots(2, 2, figsize=(8.6, 7.0), sharex=True, sharey=True)
    for ax, m in zip(axes.flat, MODELS):
        Z = np.array([[implied_selection_ratio(pw, pm, inputs[m]["ratio_women"], inputs[m]["ratio_men"])
                       for pm in pm_grid] for pw in pw_grid])
        pc = ax.pcolormesh(pm_grid, pw_grid, Z, cmap="RdYlGn", vmin=0.6, vmax=1.05, shading="auto")
        ax.contour(pm_grid, pw_grid, Z, levels=[0.8], colors="k", linewidths=1.6)
        if sourced:
            ax.plot([sourced[1]], [sourced[0]], marker="*", color="black", ms=12, mec="white")
        ax.plot([0.05], [0.20], marker="o", color="black", ms=7, mec="white", mfc="none")
        ax.set_title(f"{SHORT[m]} (ratios {inputs[m]['ratio_women']:.2f}/{inputs[m]['ratio_men']:.2f})",
                     fontsize=9)
        ax.set_xlabel("men with caregiving signal")
        ax.set_ylabel("women with caregiving signal")
    fig.colorbar(pc, ax=axes, shrink=0.85, label="implied W/M selection ratio")
    fig.suptitle("Figure 14. Disparate impact from a gender-neutral caregiver penalty:\n"
                 "implied women/men shortlist ratio by signal prevalence (black contour = four-fifths line; "
                 "○ = 20%/5% scenario; ★ = sourced point)", fontsize=9)
    fig.savefig(ROOT / "docs" / "report" / "figures" / "fig14_disparate_impact.pdf")
    print(f"[partD] wrote {out} + fig14_disparate_impact.pdf")
    print("\n".join(lines[16:23]))


if __name__ == "__main__":
    main()
