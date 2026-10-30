# Phase 4 Part D — From caregiver penalty back to a gender gap (scenario analysis)

Layer 1 of the penalty is gender-neutral in form (blind = names-only in every
model). This analysis asks what it *does* to women and men in expectation
when caregiving signals are not gender-neutrally distributed. Model: pools of
six, 50% women; every candidate shortlisted with the model's measured
gender-neutral childless top-3 base rate; signal-carriers at that base × the
model's E3 résumé-FE adjusted impact ratio (mothers' ratio for women,
fathers' for men). Implied selection ratio = E[P(shortlist | woman)] /
E[P(shortlist | man)]; the EEOC four-fifths line is 0.80.

**Label: scenario analysis.** Signal prevalence by gender is a scenario
parameter unless sourced. Current inputs: scenario parameters (no sourced value).

## Implied women/men selection ratios at the scenario point (women 20%, men 5%)

| model | mothers' ratio | fathers' ratio | implied W/M selection ratio | four-fifths |
| --- | --- | --- | --- | --- |
| DeepSeek | 0.71 | 0.70 | **0.956** | pass |
| Haiku | 0.25 | 0.23 | **0.884** | pass |
| Luna | 0.78 | 0.81 | **0.964** | pass |
| Qwen | 0.75 | 0.80 | **0.960** | pass |

## Women's signal prevalence at which the four-fifths line is crossed (men at 5%)

- DeepSeek: crosses at women's prevalence ≥ 73%
- Haiku: crosses at women's prevalence ≥ 31%
- Luna: crosses at women's prevalence ≥ 93%
- Qwen: crosses at women's prevalence ≥ 84%

Interpretation: because Haiku's Layer-1 penalty is severe, even modest
gender asymmetry in signal prevalence produces a disparate-impact violation
from a formally gender-neutral rule. With equal prevalence (5%/5%) no model
crosses the line — the entire implied gender gap is the prevalence
asymmetry interacting with a gender-blind penalty.

Regenerate: `uv run python -m audit.analysis.disparate_impact`.
