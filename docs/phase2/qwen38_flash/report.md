# Pooled report — pooled_qwen38_flash

- Model-scoped pool: `qwen38_flash` — all its runs, deduped by call_id

## 1. Parse & refusal rates

| exp | calls | parse ok | refusal |
| --- | --- | --- | --- |
| e1 | 13200 | 100.0% | 0.0% |
| e2 | 14400 | 99.9% | 0.0% |
| e3 | 5760 | 98.9% | 0.0% |
| e4 | 14400 | 100.0% | 0.0% |

Highest-refusal cells:

| exp | gender | family | refusal |
| --- | --- | --- | --- |

## 2. E1 — independent scoring

### Cell means (pilot occupations pooled)

| gender | family | n | fit | interview | salary | commitment | SD(fit) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| female | none | 1200 | 8.24 | 90.7% | $81,089 | 5.20 | 1.90 |
| female | married | 1200 | 8.22 | 91.5% | $80,324 | 5.30 | 1.81 |
| female | parent | 1200 | 8.22 | 91.3% | $79,501 | 5.38 | 1.79 |
| female | parent_gap | 1200 | 8.10 | 89.6% | $80,251 | 5.38 | 1.96 |
| female | parent_committed | 1200 | 8.21 | 92.1% | $79,759 | 5.45 | 1.76 |
| female | pregnant | 1200 | 8.35 | 91.3% | $79,527 | 5.59 | 1.89 |
| male | none | 1200 | 8.16 | 89.8% | $80,627 | 5.14 | 1.93 |
| male | married | 1200 | 8.12 | 89.8% | $79,656 | 5.20 | 1.90 |
| male | parent | 1200 | 8.20 | 92.4% | $79,729 | 5.33 | 1.79 |
| male | parent_gap | 1200 | 8.11 | 90.0% | $80,842 | 5.38 | 1.91 |
| male | parent_committed | 1200 | 8.18 | 91.4% | $79,939 | 5.39 | 1.80 |

Ceiling check: share of responses at scale maximum.

- overall_fit: 7.8% at max
- interview: 90.9% at max
- commitment: 7.4% at max
- likability: 4.5% at max

### E1 regression: Y ~ family * female + resume FE (+ occupation FE), cluster SE

| outcome | term | coef | SE | p | n |
| --- | --- | --- | --- | --- | --- |
| overall_fit | married (men) | -0.044 | 0.027 | 0.103 | 13200 |
| overall_fit | parent (men) = fatherhood effect | +0.034 | 0.044 | 0.441 | 13200 |
| overall_fit | parent_gap (men) | -0.054 | 0.048 | 0.259 | 13200 |
| overall_fit | parent_committed (men) | +0.016 | 0.041 | 0.698 | 13200 |
| overall_fit | pregnant (women vs childless women) | +0.108 | 0.040 | 0.007 | 13200 |
| overall_fit | parent (women) = motherhood effect | -0.024 | 0.037 | 0.519 | 13200 |
| interview | married (men) | -0.000 | 0.006 | 1.000 | 13200 |
| interview | parent (men) = fatherhood effect | +0.026 | 0.013 | 0.039 | 13200 |
| interview | parent_gap (men) | +0.002 | 0.012 | 0.886 | 13200 |
| interview | parent_committed (men) | +0.016 | 0.006 | 0.012 | 13200 |
| interview | pregnant (women vs childless women) | +0.007 | 0.008 | 0.385 | 13200 |
| interview | parent (women) = motherhood effect | +0.007 | 0.009 | 0.444 | 13200 |
| starting_salary_usd | married (men) | -970.833 | 504.087 | 0.054 | 13200 |
| starting_salary_usd | parent (men) = fatherhood effect | -897.500 | 602.352 | 0.136 | 13200 |
| starting_salary_usd | parent_gap (men) | +215.000 | 535.373 | 0.688 | 13200 |
| starting_salary_usd | parent_committed (men) | -687.500 | 470.662 | 0.144 | 13200 |
| starting_salary_usd | pregnant (women vs childless women) | -1562.500 | 699.214 | 0.025 | 13200 |
| starting_salary_usd | parent (women) = motherhood effect | -1588.333 | 478.634 | 0.001 | 13200 |
| competence | married (men) | +0.038 | 0.020 | 0.055 | 13200 |
| competence | parent (men) = fatherhood effect | +0.073 | 0.028 | 0.010 | 13200 |
| competence | parent_gap (men) | +0.015 | 0.031 | 0.632 | 13200 |
| competence | parent_committed (men) | +0.052 | 0.025 | 0.038 | 13200 |
| competence | pregnant (women vs childless women) | +0.106 | 0.024 | 0.000 | 13200 |
| competence | parent (women) = motherhood effect | +0.049 | 0.026 | 0.059 | 13200 |
| commitment | married (men) | +0.051 | 0.049 | 0.300 | 13200 |
| commitment | parent (men) = fatherhood effect | +0.190 | 0.062 | 0.002 | 13200 |
| commitment | parent_gap (men) | +0.232 | 0.056 | 0.000 | 13200 |
| commitment | parent_committed (men) | +0.249 | 0.068 | 0.000 | 13200 |
| commitment | pregnant (women vs childless women) | +0.390 | 0.062 | 0.000 | 13200 |
| commitment | parent (women) = motherhood effect | +0.186 | 0.058 | 0.001 | 13200 |
| promotability | married (men) | -0.085 | 0.031 | 0.006 | 13200 |
| promotability | parent (men) = fatherhood effect | -0.009 | 0.041 | 0.824 | 13200 |
| promotability | parent_gap (men) | -0.070 | 0.043 | 0.105 | 13200 |
| promotability | parent_committed (men) | +0.034 | 0.037 | 0.359 | 13200 |
| promotability | pregnant (women vs childless women) | -0.030 | 0.033 | 0.366 | 13200 |
| promotability | parent (women) = motherhood effect | -0.036 | 0.029 | 0.214 | 13200 |
| likability | married (men) | +0.237 | 0.048 | 0.000 | 13200 |
| likability | parent (men) = fatherhood effect | -0.157 | 0.060 | 0.008 | 13200 |
| likability | parent_gap (men) | +0.048 | 0.060 | 0.421 | 13200 |
| likability | parent_committed (men) | -0.124 | 0.065 | 0.055 | 13200 |
| likability | pregnant (women vs childless women) | +0.546 | 0.056 | 0.000 | 13200 |
| likability | parent (women) = motherhood effect | -0.183 | 0.056 | 0.001 | 13200 |

![E1 outcomes](figures/e1_outcomes.png)

![E1 distributions](figures/e1_distributions.png)

### Occupation-moderator regressions (H3/H4):
Y ~ family * female * Z + resume FE, cluster SE; Z standardized (female_share / median_wage / time_demands)

| Z | outcome | term | coef | SE | p | n |
| --- | --- | --- | --- | --- | --- | --- |
| female_share | interview | fatherhood effect @ mean Z | +0.0258 | 0.0125 | 0.038 | 12000 |
| female_share | interview | parent_gap (men) @ mean Z | +0.0017 | 0.0117 | 0.886 | 12000 |
| female_share | interview | parent_committed (men) @ mean Z | +0.0158 | 0.0063 | 0.012 | 12000 |
| female_share | interview | married (men) @ mean Z | +0.0000 | 0.0057 | 1.000 | 12000 |
| female_share | interview | mother-minus-father gap @ mean Z | -0.0192 | 0.0137 | 0.163 | 12000 |
| female_share | interview | fatherhood x Z | -0.0110 | 0.0118 | 0.351 | 12000 |
| female_share | interview | mother-minus-father gap x Z (H3/H4) | +0.0014 | 0.0122 | 0.909 | 12000 |
| female_share | interview | parent_gap gender gap @ mean Z | -0.0125 | 0.0112 | 0.266 | 12000 |
| female_share | interview | parent_gap gender gap x Z | +0.0016 | 0.0100 | 0.874 | 12000 |
| female_share | starting_salary_usd | fatherhood effect @ mean Z | -897.5000 | 602.6961 | 0.136 | 12000 |
| female_share | starting_salary_usd | parent_gap (men) @ mean Z | +215.0000 | 534.9773 | 0.688 | 12000 |
| female_share | starting_salary_usd | parent_committed (men) @ mean Z | -687.5000 | 466.0632 | 0.140 | 12000 |
| female_share | starting_salary_usd | married (men) @ mean Z | -970.8333 | 504.1303 | 0.054 | 12000 |
| female_share | starting_salary_usd | mother-minus-father gap @ mean Z | -690.8333 | 680.0688 | 0.310 | 12000 |
| female_share | starting_salary_usd | fatherhood x Z | -45.1702 | 572.1664 | 0.937 | 12000 |
| female_share | starting_salary_usd | mother-minus-father gap x Z (H3/H4) | +808.5230 | 607.0523 | 0.183 | 12000 |
| female_share | starting_salary_usd | parent_gap gender gap @ mean Z | -1053.3333 | 779.0198 | 0.176 | 12000 |
| female_share | starting_salary_usd | parent_gap gender gap x Z | +625.0853 | 673.8638 | 0.354 | 12000 |
| female_share | commitment | fatherhood effect @ mean Z | +0.1900 | 0.0615 | 0.002 | 12000 |
| female_share | commitment | parent_gap (men) @ mean Z | +0.2317 | 0.0564 | 0.000 | 12000 |
| female_share | commitment | parent_committed (men) @ mean Z | +0.2492 | 0.0682 | 0.000 | 12000 |
| female_share | commitment | married (men) @ mean Z | +0.0508 | 0.0490 | 0.300 | 12000 |
| female_share | commitment | mother-minus-father gap @ mean Z | -0.0042 | 0.0430 | 0.923 | 12000 |
| female_share | commitment | fatherhood x Z | +0.0197 | 0.0517 | 0.703 | 12000 |
| female_share | commitment | mother-minus-father gap x Z (H3/H4) | -0.0775 | 0.0448 | 0.084 | 12000 |
| female_share | commitment | parent_gap gender gap @ mean Z | -0.0442 | 0.0462 | 0.339 | 12000 |
| female_share | commitment | parent_gap gender gap x Z | -0.0136 | 0.0451 | 0.763 | 12000 |
| female_share | competence | fatherhood effect @ mean Z | +0.0725 | 0.0280 | 0.010 | 12000 |
| female_share | competence | parent_gap (men) @ mean Z | +0.0150 | 0.0313 | 0.632 | 12000 |
| female_share | competence | parent_committed (men) @ mean Z | +0.0517 | 0.0248 | 0.037 | 12000 |
| female_share | competence | married (men) @ mean Z | +0.0383 | 0.0200 | 0.055 | 12000 |
| female_share | competence | mother-minus-father gap @ mean Z | -0.0233 | 0.0288 | 0.419 | 12000 |
| female_share | competence | fatherhood x Z | +0.0087 | 0.0265 | 0.743 | 12000 |
| female_share | competence | mother-minus-father gap x Z (H3/H4) | -0.0340 | 0.0286 | 0.235 | 12000 |
| female_share | competence | parent_gap gender gap @ mean Z | -0.0142 | 0.0295 | 0.631 | 12000 |
| female_share | competence | parent_gap gender gap x Z | +0.0301 | 0.0319 | 0.345 | 12000 |
| female_share | overall_fit | fatherhood effect @ mean Z | +0.0342 | 0.0441 | 0.439 | 12000 |
| female_share | overall_fit | parent_gap (men) @ mean Z | -0.0542 | 0.0479 | 0.258 | 12000 |
| female_share | overall_fit | parent_committed (men) @ mean Z | +0.0158 | 0.0405 | 0.696 | 12000 |
| female_share | overall_fit | married (men) @ mean Z | -0.0442 | 0.0267 | 0.099 | 12000 |
| female_share | overall_fit | mother-minus-father gap @ mean Z | -0.0583 | 0.0430 | 0.175 | 12000 |
| female_share | overall_fit | fatherhood x Z | -0.0457 | 0.0381 | 0.231 | 12000 |
| female_share | overall_fit | mother-minus-father gap x Z (H3/H4) | -0.0135 | 0.0412 | 0.744 | 12000 |
| female_share | overall_fit | parent_gap gender gap @ mean Z | -0.0850 | 0.0405 | 0.036 | 12000 |
| female_share | overall_fit | parent_gap gender gap x Z | +0.0184 | 0.0368 | 0.616 | 12000 |
| median_wage | interview | fatherhood effect @ mean Z | +0.0258 | 0.0125 | 0.039 | 12000 |
| median_wage | interview | parent_gap (men) @ mean Z | +0.0017 | 0.0117 | 0.886 | 12000 |
| median_wage | interview | parent_committed (men) @ mean Z | +0.0158 | 0.0063 | 0.012 | 12000 |
| median_wage | interview | married (men) @ mean Z | +0.0000 | 0.0057 | 1.000 | 12000 |
| median_wage | interview | mother-minus-father gap @ mean Z | -0.0192 | 0.0137 | 0.163 | 12000 |
| median_wage | interview | fatherhood x Z | +0.0034 | 0.0094 | 0.713 | 12000 |
| median_wage | interview | mother-minus-father gap x Z (H3/H4) | -0.0015 | 0.0074 | 0.838 | 12000 |
| median_wage | interview | parent_gap gender gap @ mean Z | -0.0125 | 0.0112 | 0.266 | 12000 |
| median_wage | interview | parent_gap gender gap x Z | +0.0005 | 0.0055 | 0.935 | 12000 |
| median_wage | starting_salary_usd | fatherhood effect @ mean Z | -897.5000 | 599.0956 | 0.134 | 12000 |
| median_wage | starting_salary_usd | parent_gap (men) @ mean Z | +215.0000 | 535.1700 | 0.688 | 12000 |
| median_wage | starting_salary_usd | parent_committed (men) @ mean Z | -687.5000 | 469.0939 | 0.143 | 12000 |
| median_wage | starting_salary_usd | married (men) @ mean Z | -970.8333 | 501.6106 | 0.053 | 12000 |
| median_wage | starting_salary_usd | mother-minus-father gap @ mean Z | -690.8333 | 685.5053 | 0.314 | 12000 |
| median_wage | starting_salary_usd | fatherhood x Z | -583.9968 | 471.0007 | 0.215 | 12000 |
| median_wage | starting_salary_usd | mother-minus-father gap x Z (H3/H4) | -268.4316 | 608.1033 | 0.659 | 12000 |
| median_wage | starting_salary_usd | parent_gap gender gap @ mean Z | -1053.3333 | 781.2766 | 0.178 | 12000 |
| median_wage | starting_salary_usd | parent_gap gender gap x Z | +338.8886 | 723.0264 | 0.639 | 12000 |
| median_wage | commitment | fatherhood effect @ mean Z | +0.1900 | 0.0616 | 0.002 | 12000 |
| median_wage | commitment | parent_gap (men) @ mean Z | +0.2317 | 0.0561 | 0.000 | 12000 |
| median_wage | commitment | parent_committed (men) @ mean Z | +0.2492 | 0.0681 | 0.000 | 12000 |
| median_wage | commitment | married (men) @ mean Z | +0.0508 | 0.0475 | 0.284 | 12000 |
| median_wage | commitment | mother-minus-father gap @ mean Z | -0.0042 | 0.0438 | 0.924 | 12000 |
| median_wage | commitment | fatherhood x Z | -0.0146 | 0.0568 | 0.797 | 12000 |
| median_wage | commitment | mother-minus-father gap x Z (H3/H4) | +0.0247 | 0.0327 | 0.451 | 12000 |
| median_wage | commitment | parent_gap gender gap @ mean Z | -0.0442 | 0.0462 | 0.339 | 12000 |
| median_wage | commitment | parent_gap gender gap x Z | +0.0120 | 0.0334 | 0.720 | 12000 |
| median_wage | competence | fatherhood effect @ mean Z | +0.0725 | 0.0279 | 0.009 | 12000 |
| median_wage | competence | parent_gap (men) @ mean Z | +0.0150 | 0.0313 | 0.632 | 12000 |
| median_wage | competence | parent_committed (men) @ mean Z | +0.0517 | 0.0247 | 0.037 | 12000 |
| median_wage | competence | married (men) @ mean Z | +0.0383 | 0.0197 | 0.052 | 12000 |
| median_wage | competence | mother-minus-father gap @ mean Z | -0.0233 | 0.0291 | 0.423 | 12000 |
| median_wage | competence | fatherhood x Z | +0.0197 | 0.0213 | 0.354 | 12000 |
| median_wage | competence | mother-minus-father gap x Z (H3/H4) | -0.0001 | 0.0205 | 0.995 | 12000 |
| median_wage | competence | parent_gap gender gap @ mean Z | -0.0142 | 0.0297 | 0.633 | 12000 |
| median_wage | competence | parent_gap gender gap x Z | -0.0061 | 0.0187 | 0.744 | 12000 |
| median_wage | overall_fit | fatherhood effect @ mean Z | +0.0342 | 0.0443 | 0.441 | 12000 |
| median_wage | overall_fit | parent_gap (men) @ mean Z | -0.0542 | 0.0480 | 0.260 | 12000 |
| median_wage | overall_fit | parent_committed (men) @ mean Z | +0.0158 | 0.0398 | 0.691 | 12000 |
| median_wage | overall_fit | married (men) @ mean Z | -0.0442 | 0.0269 | 0.101 | 12000 |
| median_wage | overall_fit | mother-minus-father gap @ mean Z | -0.0583 | 0.0430 | 0.175 | 12000 |
| median_wage | overall_fit | fatherhood x Z | +0.0248 | 0.0362 | 0.493 | 12000 |
| median_wage | overall_fit | mother-minus-father gap x Z (H3/H4) | -0.0089 | 0.0341 | 0.794 | 12000 |
| median_wage | overall_fit | parent_gap gender gap @ mean Z | -0.0850 | 0.0405 | 0.036 | 12000 |
| median_wage | overall_fit | parent_gap gender gap x Z | -0.0124 | 0.0304 | 0.683 | 12000 |
| time_demands | interview | fatherhood effect @ mean Z | +0.0258 | 0.0125 | 0.039 | 12000 |
| time_demands | interview | parent_gap (men) @ mean Z | +0.0017 | 0.0117 | 0.886 | 12000 |
| time_demands | interview | parent_committed (men) @ mean Z | +0.0158 | 0.0063 | 0.012 | 12000 |
| time_demands | interview | married (men) @ mean Z | +0.0000 | 0.0057 | 1.000 | 12000 |
| time_demands | interview | mother-minus-father gap @ mean Z | -0.0192 | 0.0137 | 0.163 | 12000 |
| time_demands | interview | fatherhood x Z | +0.0072 | 0.0064 | 0.261 | 12000 |
| time_demands | interview | mother-minus-father gap x Z (H3/H4) | -0.0050 | 0.0052 | 0.340 | 12000 |
| time_demands | interview | parent_gap gender gap @ mean Z | -0.0125 | 0.0112 | 0.266 | 12000 |
| time_demands | interview | parent_gap gender gap x Z | -0.0051 | 0.0046 | 0.269 | 12000 |
| time_demands | starting_salary_usd | fatherhood effect @ mean Z | -897.5000 | 597.9301 | 0.133 | 12000 |
| time_demands | starting_salary_usd | parent_gap (men) @ mean Z | +215.0000 | 535.1950 | 0.688 | 12000 |
| time_demands | starting_salary_usd | parent_committed (men) @ mean Z | -687.5000 | 470.8232 | 0.144 | 12000 |
| time_demands | starting_salary_usd | married (men) @ mean Z | -970.8333 | 502.4186 | 0.053 | 12000 |
| time_demands | starting_salary_usd | mother-minus-father gap @ mean Z | -690.8333 | 680.0914 | 0.310 | 12000 |
| time_demands | starting_salary_usd | fatherhood x Z | +671.0866 | 568.5509 | 0.238 | 12000 |
| time_demands | starting_salary_usd | mother-minus-father gap x Z (H3/H4) | -807.0309 | 468.8466 | 0.085 | 12000 |
| time_demands | starting_salary_usd | parent_gap gender gap @ mean Z | -1053.3333 | 782.0507 | 0.178 | 12000 |
| time_demands | starting_salary_usd | parent_gap gender gap x Z | -141.5301 | 376.9673 | 0.707 | 12000 |
| time_demands | commitment | fatherhood effect @ mean Z | +0.1900 | 0.0613 | 0.002 | 12000 |
| time_demands | commitment | parent_gap (men) @ mean Z | +0.2317 | 0.0563 | 0.000 | 12000 |
| time_demands | commitment | parent_committed (men) @ mean Z | +0.2492 | 0.0681 | 0.000 | 12000 |
| time_demands | commitment | married (men) @ mean Z | +0.0508 | 0.0490 | 0.299 | 12000 |
| time_demands | commitment | mother-minus-father gap @ mean Z | -0.0042 | 0.0437 | 0.924 | 12000 |
| time_demands | commitment | fatherhood x Z | -0.0527 | 0.0429 | 0.220 | 12000 |
| time_demands | commitment | mother-minus-father gap x Z (H3/H4) | +0.0306 | 0.0463 | 0.508 | 12000 |
| time_demands | commitment | parent_gap gender gap @ mean Z | -0.0442 | 0.0462 | 0.339 | 12000 |
| time_demands | commitment | parent_gap gender gap x Z | -0.0188 | 0.0349 | 0.590 | 12000 |
| time_demands | competence | fatherhood effect @ mean Z | +0.0725 | 0.0278 | 0.009 | 12000 |
| time_demands | competence | parent_gap (men) @ mean Z | +0.0150 | 0.0312 | 0.631 | 12000 |
| time_demands | competence | parent_committed (men) @ mean Z | +0.0517 | 0.0249 | 0.038 | 12000 |
| time_demands | competence | married (men) @ mean Z | +0.0383 | 0.0199 | 0.054 | 12000 |
| time_demands | competence | mother-minus-father gap @ mean Z | -0.0233 | 0.0288 | 0.417 | 12000 |
| time_demands | competence | fatherhood x Z | -0.0273 | 0.0266 | 0.305 | 12000 |
| time_demands | competence | mother-minus-father gap x Z (H3/H4) | +0.0388 | 0.0248 | 0.117 | 12000 |
| time_demands | competence | parent_gap gender gap @ mean Z | -0.0142 | 0.0296 | 0.633 | 12000 |
| time_demands | competence | parent_gap gender gap x Z | -0.0190 | 0.0215 | 0.377 | 12000 |
| time_demands | overall_fit | fatherhood effect @ mean Z | +0.0342 | 0.0444 | 0.442 | 12000 |
| time_demands | overall_fit | parent_gap (men) @ mean Z | -0.0542 | 0.0480 | 0.260 | 12000 |
| time_demands | overall_fit | parent_committed (men) @ mean Z | +0.0158 | 0.0408 | 0.698 | 12000 |
| time_demands | overall_fit | married (men) @ mean Z | -0.0442 | 0.0269 | 0.100 | 12000 |
| time_demands | overall_fit | mother-minus-father gap @ mean Z | -0.0583 | 0.0430 | 0.175 | 12000 |
| time_demands | overall_fit | fatherhood x Z | +0.0053 | 0.0321 | 0.870 | 12000 |
| time_demands | overall_fit | mother-minus-father gap x Z (H3/H4) | -0.0079 | 0.0323 | 0.806 | 12000 |
| time_demands | overall_fit | parent_gap gender gap @ mean Z | -0.0850 | 0.0403 | 0.035 | 12000 |
| time_demands | overall_fit | parent_gap gender gap x Z | -0.0355 | 0.0250 | 0.157 | 12000 |

## 3. E2 — paired comparison

Parent-candidate share chosen (0.5 = no bias):

| contrast | gender | P(parent chosen) | n |
| --- | --- | --- | --- |
| parent | female | 0.387 | 2396 |
| parent | male | 0.398 | 2395 |
| parent_committed | female | 0.407 | 2397 |
| parent_committed | male | 0.430 | 2397 |
| parent_gap | female | 0.229 | 2398 |
| parent_gap | male | 0.256 | 2397 |

Position bias — P(chosen = A) = 0.634 (0.5 = none).

Paired differences (parent − childless):

| metric | contrast | gender | mean diff | t | n |
| --- | --- | --- | --- | --- | --- |
| diff_starting_salary_usd | parent | female | -1775.46 | -6.29 | 2396 |
| diff_starting_salary_usd | parent | male | -1513.15 | -5.46 | 2395 |
| diff_starting_salary_usd | parent_committed | female | -1335.42 | -4.72 | 2397 |
| diff_starting_salary_usd | parent_committed | male | -1028.79 | -3.69 | 2397 |
| diff_starting_salary_usd | parent_gap | female | -3145.33 | -11.15 | 2398 |
| diff_starting_salary_usd | parent_gap | male | -2621.61 | -8.94 | 2397 |
| diff_overall_fit | parent | female | -0.66 | -12.18 | 2396 |
| diff_overall_fit | parent | male | -0.59 | -10.84 | 2395 |
| diff_overall_fit | parent_committed | female | -0.67 | -12.16 | 2397 |
| diff_overall_fit | parent_committed | male | -0.60 | -10.59 | 2397 |
| diff_overall_fit | parent_gap | female | -1.21 | -23.25 | 2398 |
| diff_overall_fit | parent_gap | male | -1.16 | -21.65 | 2397 |
| diff_commitment | parent | female | -1.14 | -27.76 | 2396 |
| diff_commitment | parent | male | -1.10 | -26.16 | 2395 |
| diff_commitment | parent_committed | female | -0.85 | -20.59 | 2397 |
| diff_commitment | parent_committed | male | -0.79 | -18.21 | 2397 |
| diff_commitment | parent_gap | female | -1.56 | -43.20 | 2398 |
| diff_commitment | parent_gap | male | -1.58 | -42.20 | 2397 |
| diff_competence | parent | female | -0.26 | -8.55 | 2396 |
| diff_competence | parent | male | -0.22 | -7.15 | 2395 |
| diff_competence | parent_committed | female | -0.24 | -7.77 | 2397 |
| diff_competence | parent_committed | male | -0.19 | -5.93 | 2397 |
| diff_competence | parent_gap | female | -0.59 | -19.89 | 2398 |
| diff_competence | parent_gap | male | -0.54 | -17.73 | 2397 |

![E2 choice](figures/e2_choice.png)

## 4. E3 — ranking pools

Top-1 / Top-3 rates by candidate type:

| composition | gender | family | top1 | top3 |
| --- | --- | --- | --- | --- |
| a | female | none | 0.215 | 0.596 |
| a | female | parent | 0.111 | 0.339 |
| a | male | none | 0.153 | 0.489 |
| b | female | none | 0.155 | 0.482 |
| b | male | none | 0.210 | 0.600 |
| b | male | parent | 0.115 | 0.353 |
| c | female | none | 0.157 | 0.479 |
| c | female | parent | 0.164 | 0.524 |
| c | male | none | 0.188 | 0.461 |
| c | male | parent | 0.138 | 0.551 |
| d | female | parent | 0.206 | 0.534 |
| d | male | parent | 0.128 | 0.466 |

Four-fifths (adverse impact) check:

| group | top3 rate | childless ref | impact ratio |
| --- | --- | --- | --- |
| parent female (comp a) | 0.339 | 0.596 | 0.57 |
| parent male (comp b) | 0.353 | 0.600 | 0.59 |

Position bias (top-1 rate by screen label C1..C6): C1=0.41, C2=0.19, C3=0.15, C4=0.11, C5=0.09, C6=0.05

![E3 top3](figures/e3_top3.png)

## 5. E4 — JD context

| JD variant | gender | family | interview | salary | commitment |
| --- | --- | --- | --- | --- | --- |
| base | female | none | 94.8% | $66,450 | 5.54 |
| base | female | parent | 95.0% | $65,656 | 5.64 |
| base | female | parent_gap | 95.2% | $66,965 | 5.64 |
| base | male | none | 93.8% | $65,892 | 5.43 |
| base | male | parent | 95.2% | $66,025 | 5.60 |
| base | male | parent_gap | 93.8% | $66,296 | 5.59 |
| eeo | female | none | 95.4% | $66,658 | 5.62 |
| eeo | female | parent | 95.6% | $66,719 | 5.96 |
| eeo | female | parent_gap | 94.8% | $66,119 | 5.82 |
| eeo | male | none | 95.2% | $67,229 | 5.57 |
| eeo | male | parent | 95.8% | $66,190 | 5.90 |
| eeo | male | parent_gap | 94.8% | $66,752 | 5.83 |
| family_friendly | female | none | 95.2% | $69,027 | 5.51 |
| family_friendly | female | parent | 95.0% | $67,988 | 5.77 |
| family_friendly | female | parent_gap | 93.8% | $68,460 | 5.83 |
| family_friendly | male | none | 94.8% | $69,010 | 5.49 |
| family_friendly | male | parent | 94.6% | $67,977 | 5.72 |
| family_friendly | male | parent_gap | 94.4% | $68,619 | 5.80 |
| greedy | female | none | 91.2% | $66,083 | 5.14 |
| greedy | female | parent | 90.0% | $63,552 | 5.13 |
| greedy | female | parent_gap | 89.6% | $65,231 | 5.19 |
| greedy | male | none | 90.6% | $65,846 | 4.93 |
| greedy | male | parent | 90.4% | $62,938 | 5.09 |
| greedy | male | parent_gap | 89.6% | $63,398 | 5.17 |
| greedy_ff | female | none | 91.9% | $67,933 | 5.23 |
| greedy_ff | female | parent | 90.4% | $66,415 | 5.34 |
| greedy_ff | female | parent_gap | 91.0% | $67,148 | 5.42 |
| greedy_ff | male | none | 93.1% | $68,002 | 5.27 |
| greedy_ff | male | parent | 87.7% | $63,671 | 5.16 |
| greedy_ff | male | parent_gap | 90.0% | $65,879 | 5.44 |

![E4 gap](figures/e4_gap.png)

## 6. Rationale mentions of family cues

| exp | family | share of rationales mentioning family |
| --- | --- | --- |
| e1 | married | 5.0% |
| e1 | none | 8.9% |
| e1 | parent | 15.0% |
| e1 | parent_committed | 14.1% |
| e1 | parent_gap | 31.4% |
| e1 | pregnant | 92.5% |
| e2 | parent | 14.1% |
| e2 | parent_committed | 13.6% |
| e2 | parent_gap | 22.4% |
| e4 | none | 11.1% |
| e4 | parent | 40.9% |
| e4 | parent_gap | 61.3% |

Within-cell SD (overall_fit): median 1.89, min 1.76, max 1.96.

## 7. Measured tokens & Phase 1 cost estimate

- e1: mean input 980, mean output 122 (n=13200)
- e2: mean input 1419, mean output 236 (n=14400)
- e3: mean input 3476, mean output 118 (n=5760)
- e4: mean input 1017, mean output 123 (n=14400)
