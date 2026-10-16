# Pooled report — pooled_gpt6_luna

- Model-scoped pool: `gpt6_luna` — all its runs, deduped by call_id

## 1. Parse & refusal rates

| exp | calls | parse ok | refusal |
| --- | --- | --- | --- |
| e1 | 13200 | 100.0% | 0.0% |
| e2 | 14400 | 96.5% | 0.0% |
| e3 | 5760 | 100.0% | 0.0% |
| e4 | 14400 | 100.0% | 0.0% |

Highest-refusal cells:

| exp | gender | family | refusal |
| --- | --- | --- | --- |

## 2. E1 — independent scoring

### Cell means (pilot occupations pooled)

| gender | family | n | fit | interview | salary | commitment | SD(fit) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| female | none | 1200 | 8.41 | 91.5% | $89,925 | 6.07 | 1.71 |
| female | married | 1200 | 8.32 | 91.2% | $89,560 | 5.42 | 1.65 |
| female | parent | 1200 | 8.33 | 91.8% | $89,193 | 5.89 | 1.64 |
| female | parent_gap | 1200 | 8.16 | 92.1% | $89,372 | 5.86 | 1.59 |
| female | parent_committed | 1200 | 8.27 | 92.5% | $90,220 | 5.98 | 1.56 |
| female | pregnant | 1200 | 8.44 | 92.3% | $88,851 | 6.10 | 1.61 |
| male | none | 1200 | 8.34 | 91.3% | $90,101 | 6.04 | 1.69 |
| male | married | 1200 | 8.25 | 91.4% | $89,647 | 5.35 | 1.69 |
| male | parent | 1200 | 8.26 | 91.3% | $89,347 | 5.84 | 1.65 |
| male | parent_gap | 1200 | 8.05 | 91.8% | $89,772 | 5.83 | 1.58 |
| male | parent_committed | 1200 | 8.20 | 91.9% | $90,480 | 5.89 | 1.58 |

Ceiling check: share of responses at scale maximum.

- overall_fit: 14.7% at max
- interview: 91.7% at max
- commitment: 11.5% at max
- likability: 0.0% at max

### E1 regression: Y ~ family * female + resume FE (+ occupation FE), cluster SE

| outcome | term | coef | SE | p | n |
| --- | --- | --- | --- | --- | --- |
| overall_fit | married (men) | -0.093 | 0.019 | 0.000 | 13200 |
| overall_fit | parent (men) = fatherhood effect | -0.082 | 0.026 | 0.001 | 13200 |
| overall_fit | parent_gap (men) | -0.296 | 0.044 | 0.000 | 13200 |
| overall_fit | parent_committed (men) | -0.142 | 0.029 | 0.000 | 13200 |
| overall_fit | pregnant (women vs childless women) | +0.032 | 0.032 | 0.322 | 13200 |
| overall_fit | parent (women) = motherhood effect | -0.083 | 0.025 | 0.001 | 13200 |
| interview | married (men) | +0.001 | 0.001 | 0.567 | 13200 |
| interview | parent (men) = fatherhood effect | -0.000 | 0.002 | 1.000 | 13200 |
| interview | parent_gap (men) | +0.004 | 0.005 | 0.414 | 13200 |
| interview | parent_committed (men) | +0.006 | 0.006 | 0.319 | 13200 |
| interview | pregnant (women vs childless women) | +0.008 | 0.006 | 0.139 | 13200 |
| interview | parent (women) = motherhood effect | +0.003 | 0.003 | 0.249 | 13200 |
| starting_salary_usd | married (men) | -454.167 | 387.749 | 0.241 | 13200 |
| starting_salary_usd | parent (men) = fatherhood effect | -754.167 | 632.371 | 0.233 | 13200 |
| starting_salary_usd | parent_gap (men) | -329.167 | 539.468 | 0.542 | 13200 |
| starting_salary_usd | parent_committed (men) | +379.167 | 564.294 | 0.502 | 13200 |
| starting_salary_usd | pregnant (women vs childless women) | -1074.167 | 952.804 | 0.260 | 13200 |
| starting_salary_usd | parent (women) = motherhood effect | -731.667 | 636.819 | 0.251 | 13200 |
| competence | married (men) | -0.023 | 0.012 | 0.051 | 13200 |
| competence | parent (men) = fatherhood effect | +0.010 | 0.015 | 0.505 | 13200 |
| competence | parent_gap (men) | -0.065 | 0.021 | 0.002 | 13200 |
| competence | parent_committed (men) | -0.014 | 0.016 | 0.369 | 13200 |
| competence | pregnant (women vs childless women) | +0.075 | 0.021 | 0.000 | 13200 |
| competence | parent (women) = motherhood effect | +0.010 | 0.012 | 0.417 | 13200 |
| commitment | married (men) | -0.694 | 0.040 | 0.000 | 13200 |
| commitment | parent (men) = fatherhood effect | -0.205 | 0.035 | 0.000 | 13200 |
| commitment | parent_gap (men) | -0.212 | 0.045 | 0.000 | 13200 |
| commitment | parent_committed (men) | -0.148 | 0.039 | 0.000 | 13200 |
| commitment | pregnant (women vs childless women) | +0.036 | 0.029 | 0.218 | 13200 |
| commitment | parent (women) = motherhood effect | -0.174 | 0.035 | 0.000 | 13200 |
| promotability | married (men) | -0.086 | 0.022 | 0.000 | 13200 |
| promotability | parent (men) = fatherhood effect | -0.059 | 0.021 | 0.004 | 13200 |
| promotability | parent_gap (men) | -0.108 | 0.029 | 0.000 | 13200 |
| promotability | parent_committed (men) | -0.036 | 0.020 | 0.079 | 13200 |
| promotability | pregnant (women vs childless women) | +0.025 | 0.021 | 0.242 | 13200 |
| promotability | parent (women) = motherhood effect | -0.043 | 0.020 | 0.026 | 13200 |
| likability | married (men) | -0.580 | 0.028 | 0.000 | 13200 |
| likability | parent (men) = fatherhood effect | -0.503 | 0.033 | 0.000 | 13200 |
| likability | parent_gap (men) | -0.508 | 0.035 | 0.000 | 13200 |
| likability | parent_committed (men) | -0.472 | 0.034 | 0.000 | 13200 |
| likability | pregnant (women vs childless women) | -0.117 | 0.025 | 0.000 | 13200 |
| likability | parent (women) = motherhood effect | -0.494 | 0.034 | 0.000 | 13200 |

![E1 outcomes](figures/e1_outcomes.png)

![E1 distributions](figures/e1_distributions.png)

### Occupation-moderator regressions (H3/H4):
Y ~ family * female * Z + resume FE, cluster SE; Z standardized (female_share / median_wage / time_demands)

| Z | outcome | term | coef | SE | p | n |
| --- | --- | --- | --- | --- | --- | --- |
| female_share | interview | fatherhood effect @ mean Z | -0.0000 | 0.0020 | 1.000 | 12000 |
| female_share | interview | parent_gap (men) @ mean Z | +0.0042 | 0.0051 | 0.410 | 12000 |
| female_share | interview | parent_committed (men) @ mean Z | +0.0058 | 0.0059 | 0.319 | 12000 |
| female_share | interview | married (men) @ mean Z | +0.0008 | 0.0015 | 0.567 | 12000 |
| female_share | interview | mother-minus-father gap @ mean Z | +0.0033 | 0.0016 | 0.042 | 12000 |
| female_share | interview | fatherhood x Z | -0.0024 | 0.0014 | 0.091 | 12000 |
| female_share | interview | mother-minus-father gap x Z (H3/H4) | +0.0011 | 0.0014 | 0.407 | 12000 |
| female_share | interview | parent_gap gender gap @ mean Z | +0.0017 | 0.0054 | 0.759 | 12000 |
| female_share | interview | parent_gap gender gap x Z | -0.0045 | 0.0044 | 0.309 | 12000 |
| female_share | starting_salary_usd | fatherhood effect @ mean Z | -754.1667 | 632.6310 | 0.233 | 12000 |
| female_share | starting_salary_usd | parent_gap (men) @ mean Z | -329.1667 | 539.4990 | 0.542 | 12000 |
| female_share | starting_salary_usd | parent_committed (men) @ mean Z | +379.1667 | 564.5233 | 0.502 | 12000 |
| female_share | starting_salary_usd | married (men) @ mean Z | -454.1667 | 387.9832 | 0.242 | 12000 |
| female_share | starting_salary_usd | mother-minus-father gap @ mean Z | +22.5000 | 250.7896 | 0.929 | 12000 |
| female_share | starting_salary_usd | fatherhood x Z | -110.8441 | 360.0008 | 0.758 | 12000 |
| female_share | starting_salary_usd | mother-minus-father gap x Z (H3/H4) | +102.8712 | 214.5431 | 0.632 | 12000 |
| female_share | starting_salary_usd | parent_gap gender gap @ mean Z | -224.1667 | 277.5515 | 0.419 | 12000 |
| female_share | starting_salary_usd | parent_gap gender gap x Z | +373.3299 | 226.7214 | 0.100 | 12000 |
| female_share | commitment | fatherhood effect @ mean Z | -0.2050 | 0.0351 | 0.000 | 12000 |
| female_share | commitment | parent_gap (men) @ mean Z | -0.2117 | 0.0454 | 0.000 | 12000 |
| female_share | commitment | parent_committed (men) @ mean Z | -0.1475 | 0.0379 | 0.000 | 12000 |
| female_share | commitment | married (men) @ mean Z | -0.6942 | 0.0392 | 0.000 | 12000 |
| female_share | commitment | mother-minus-father gap @ mean Z | +0.0308 | 0.0186 | 0.097 | 12000 |
| female_share | commitment | fatherhood x Z | -0.0246 | 0.0359 | 0.493 | 12000 |
| female_share | commitment | mother-minus-father gap x Z (H3/H4) | -0.0152 | 0.0183 | 0.407 | 12000 |
| female_share | commitment | parent_gap gender gap @ mean Z | +0.0050 | 0.0214 | 0.815 | 12000 |
| female_share | commitment | parent_gap gender gap x Z | +0.0045 | 0.0166 | 0.785 | 12000 |
| female_share | competence | fatherhood effect @ mean Z | +0.0100 | 0.0149 | 0.503 | 12000 |
| female_share | competence | parent_gap (men) @ mean Z | -0.0650 | 0.0212 | 0.002 | 12000 |
| female_share | competence | parent_committed (men) @ mean Z | -0.0142 | 0.0158 | 0.369 | 12000 |
| female_share | competence | married (men) @ mean Z | -0.0233 | 0.0118 | 0.047 | 12000 |
| female_share | competence | mother-minus-father gap @ mean Z | +0.0000 | 0.0129 | 1.000 | 12000 |
| female_share | competence | fatherhood x Z | +0.0155 | 0.0144 | 0.280 | 12000 |
| female_share | competence | mother-minus-father gap x Z (H3/H4) | -0.0173 | 0.0141 | 0.220 | 12000 |
| female_share | competence | parent_gap gender gap @ mean Z | +0.0517 | 0.0173 | 0.003 | 12000 |
| female_share | competence | parent_gap gender gap x Z | +0.0044 | 0.0180 | 0.807 | 12000 |
| female_share | overall_fit | fatherhood effect @ mean Z | -0.0817 | 0.0256 | 0.001 | 12000 |
| female_share | overall_fit | parent_gap (men) @ mean Z | -0.2958 | 0.0440 | 0.000 | 12000 |
| female_share | overall_fit | parent_committed (men) @ mean Z | -0.1417 | 0.0289 | 0.000 | 12000 |
| female_share | overall_fit | married (men) @ mean Z | -0.0925 | 0.0193 | 0.000 | 12000 |
| female_share | overall_fit | mother-minus-father gap @ mean Z | -0.0017 | 0.0216 | 0.938 | 12000 |
| female_share | overall_fit | fatherhood x Z | -0.0193 | 0.0273 | 0.479 | 12000 |
| female_share | overall_fit | mother-minus-father gap x Z (H3/H4) | -0.0001 | 0.0211 | 0.995 | 12000 |
| female_share | overall_fit | parent_gap gender gap @ mean Z | +0.0450 | 0.0236 | 0.057 | 12000 |
| female_share | overall_fit | parent_gap gender gap x Z | -0.0060 | 0.0240 | 0.803 | 12000 |
| median_wage | interview | fatherhood effect @ mean Z | +0.0000 | 0.0021 | 1.000 | 12000 |
| median_wage | interview | parent_gap (men) @ mean Z | +0.0042 | 0.0051 | 0.414 | 12000 |
| median_wage | interview | parent_committed (men) @ mean Z | +0.0058 | 0.0059 | 0.319 | 12000 |
| median_wage | interview | married (men) @ mean Z | +0.0008 | 0.0015 | 0.566 | 12000 |
| median_wage | interview | mother-minus-father gap @ mean Z | +0.0033 | 0.0016 | 0.042 | 12000 |
| median_wage | interview | fatherhood x Z | -0.0006 | 0.0009 | 0.479 | 12000 |
| median_wage | interview | mother-minus-father gap x Z (H3/H4) | +0.0004 | 0.0012 | 0.760 | 12000 |
| median_wage | interview | parent_gap gender gap @ mean Z | +0.0017 | 0.0055 | 0.760 | 12000 |
| median_wage | interview | parent_gap gender gap x Z | -0.0003 | 0.0010 | 0.770 | 12000 |
| median_wage | starting_salary_usd | fatherhood effect @ mean Z | -754.1667 | 625.0736 | 0.228 | 12000 |
| median_wage | starting_salary_usd | parent_gap (men) @ mean Z | -329.1667 | 535.5491 | 0.539 | 12000 |
| median_wage | starting_salary_usd | parent_committed (men) @ mean Z | +379.1667 | 558.9404 | 0.498 | 12000 |
| median_wage | starting_salary_usd | married (men) @ mean Z | -454.1667 | 382.3227 | 0.235 | 12000 |
| median_wage | starting_salary_usd | mother-minus-father gap @ mean Z | +22.5000 | 244.0542 | 0.927 | 12000 |
| median_wage | starting_salary_usd | fatherhood x Z | -870.0467 | 720.4470 | 0.227 | 12000 |
| median_wage | starting_salary_usd | mother-minus-father gap x Z (H3/H4) | +521.2636 | 296.9200 | 0.079 | 12000 |
| median_wage | starting_salary_usd | parent_gap gender gap @ mean Z | -224.1667 | 278.1891 | 0.420 | 12000 |
| median_wage | starting_salary_usd | parent_gap gender gap x Z | -334.0893 | 250.9341 | 0.183 | 12000 |
| median_wage | commitment | fatherhood effect @ mean Z | -0.2050 | 0.0351 | 0.000 | 12000 |
| median_wage | commitment | parent_gap (men) @ mean Z | -0.2117 | 0.0454 | 0.000 | 12000 |
| median_wage | commitment | parent_committed (men) @ mean Z | -0.1475 | 0.0387 | 0.000 | 12000 |
| median_wage | commitment | married (men) @ mean Z | -0.6942 | 0.0402 | 0.000 | 12000 |
| median_wage | commitment | mother-minus-father gap @ mean Z | +0.0308 | 0.0184 | 0.094 | 12000 |
| median_wage | commitment | fatherhood x Z | +0.0237 | 0.0333 | 0.476 | 12000 |
| median_wage | commitment | mother-minus-father gap x Z (H3/H4) | +0.0269 | 0.0202 | 0.182 | 12000 |
| median_wage | commitment | parent_gap gender gap @ mean Z | +0.0050 | 0.0211 | 0.813 | 12000 |
| median_wage | commitment | parent_gap gender gap x Z | +0.0287 | 0.0247 | 0.246 | 12000 |
| median_wage | competence | fatherhood effect @ mean Z | +0.0100 | 0.0150 | 0.505 | 12000 |
| median_wage | competence | parent_gap (men) @ mean Z | -0.0650 | 0.0213 | 0.002 | 12000 |
| median_wage | competence | parent_committed (men) @ mean Z | -0.0142 | 0.0158 | 0.369 | 12000 |
| median_wage | competence | married (men) @ mean Z | -0.0233 | 0.0120 | 0.051 | 12000 |
| median_wage | competence | mother-minus-father gap @ mean Z | +0.0000 | 0.0130 | 1.000 | 12000 |
| median_wage | competence | fatherhood x Z | -0.0053 | 0.0137 | 0.700 | 12000 |
| median_wage | competence | mother-minus-father gap x Z (H3/H4) | +0.0049 | 0.0099 | 0.617 | 12000 |
| median_wage | competence | parent_gap gender gap @ mean Z | +0.0517 | 0.0170 | 0.002 | 12000 |
| median_wage | competence | parent_gap gender gap x Z | -0.0267 | 0.0160 | 0.094 | 12000 |
| median_wage | overall_fit | fatherhood effect @ mean Z | -0.0817 | 0.0256 | 0.001 | 12000 |
| median_wage | overall_fit | parent_gap (men) @ mean Z | -0.2958 | 0.0440 | 0.000 | 12000 |
| median_wage | overall_fit | parent_committed (men) @ mean Z | -0.1417 | 0.0293 | 0.000 | 12000 |
| median_wage | overall_fit | married (men) @ mean Z | -0.0925 | 0.0194 | 0.000 | 12000 |
| median_wage | overall_fit | mother-minus-father gap @ mean Z | -0.0017 | 0.0216 | 0.938 | 12000 |
| median_wage | overall_fit | fatherhood x Z | +0.0133 | 0.0232 | 0.565 | 12000 |
| median_wage | overall_fit | mother-minus-father gap x Z (H3/H4) | -0.0023 | 0.0265 | 0.931 | 12000 |
| median_wage | overall_fit | parent_gap gender gap @ mean Z | +0.0450 | 0.0236 | 0.056 | 12000 |
| median_wage | overall_fit | parent_gap gender gap x Z | -0.0146 | 0.0236 | 0.536 | 12000 |
| time_demands | interview | fatherhood effect @ mean Z | -0.0000 | 0.0021 | 1.000 | 12000 |
| time_demands | interview | parent_gap (men) @ mean Z | +0.0042 | 0.0051 | 0.414 | 12000 |
| time_demands | interview | parent_committed (men) @ mean Z | +0.0058 | 0.0059 | 0.319 | 12000 |
| time_demands | interview | married (men) @ mean Z | +0.0008 | 0.0015 | 0.567 | 12000 |
| time_demands | interview | mother-minus-father gap @ mean Z | +0.0033 | 0.0016 | 0.042 | 12000 |
| time_demands | interview | fatherhood x Z | +0.0000 | 0.0002 | 0.911 | 12000 |
| time_demands | interview | mother-minus-father gap x Z (H3/H4) | -0.0004 | 0.0008 | 0.628 | 12000 |
| time_demands | interview | parent_gap gender gap @ mean Z | +0.0017 | 0.0055 | 0.760 | 12000 |
| time_demands | interview | parent_gap gender gap x Z | -0.0004 | 0.0009 | 0.631 | 12000 |
| time_demands | starting_salary_usd | fatherhood effect @ mean Z | -754.1667 | 628.1863 | 0.230 | 12000 |
| time_demands | starting_salary_usd | parent_gap (men) @ mean Z | -329.1667 | 537.4349 | 0.540 | 12000 |
| time_demands | starting_salary_usd | parent_committed (men) @ mean Z | +379.1667 | 563.9464 | 0.501 | 12000 |
| time_demands | starting_salary_usd | married (men) @ mean Z | -454.1667 | 385.7463 | 0.239 | 12000 |
| time_demands | starting_salary_usd | mother-minus-father gap @ mean Z | +22.5000 | 249.8049 | 0.928 | 12000 |
| time_demands | starting_salary_usd | fatherhood x Z | -671.8209 | 276.5873 | 0.015 | 12000 |
| time_demands | starting_salary_usd | mother-minus-father gap x Z (H3/H4) | +221.8235 | 175.1787 | 0.205 | 12000 |
| time_demands | starting_salary_usd | parent_gap gender gap @ mean Z | -224.1667 | 280.7145 | 0.425 | 12000 |
| time_demands | starting_salary_usd | parent_gap gender gap x Z | +32.0918 | 147.8030 | 0.828 | 12000 |
| time_demands | commitment | fatherhood effect @ mean Z | -0.2050 | 0.0350 | 0.000 | 12000 |
| time_demands | commitment | parent_gap (men) @ mean Z | -0.2117 | 0.0454 | 0.000 | 12000 |
| time_demands | commitment | parent_committed (men) @ mean Z | -0.1475 | 0.0376 | 0.000 | 12000 |
| time_demands | commitment | married (men) @ mean Z | -0.6942 | 0.0391 | 0.000 | 12000 |
| time_demands | commitment | mother-minus-father gap @ mean Z | +0.0308 | 0.0185 | 0.096 | 12000 |
| time_demands | commitment | fatherhood x Z | +0.0334 | 0.0284 | 0.239 | 12000 |
| time_demands | commitment | mother-minus-father gap x Z (H3/H4) | +0.0197 | 0.0211 | 0.351 | 12000 |
| time_demands | commitment | parent_gap gender gap @ mean Z | +0.0050 | 0.0213 | 0.815 | 12000 |
| time_demands | commitment | parent_gap gender gap x Z | +0.0142 | 0.0179 | 0.426 | 12000 |
| time_demands | competence | fatherhood effect @ mean Z | +0.0100 | 0.0149 | 0.503 | 12000 |
| time_demands | competence | parent_gap (men) @ mean Z | -0.0650 | 0.0207 | 0.002 | 12000 |
| time_demands | competence | parent_committed (men) @ mean Z | -0.0142 | 0.0157 | 0.366 | 12000 |
| time_demands | competence | married (men) @ mean Z | -0.0233 | 0.0120 | 0.051 | 12000 |
| time_demands | competence | mother-minus-father gap @ mean Z | +0.0000 | 0.0129 | 1.000 | 12000 |
| time_demands | competence | fatherhood x Z | -0.0149 | 0.0125 | 0.233 | 12000 |
| time_demands | competence | mother-minus-father gap x Z (H3/H4) | +0.0161 | 0.0135 | 0.232 | 12000 |
| time_demands | competence | parent_gap gender gap @ mean Z | +0.0517 | 0.0173 | 0.003 | 12000 |
| time_demands | competence | parent_gap gender gap x Z | +0.0058 | 0.0164 | 0.721 | 12000 |
| time_demands | overall_fit | fatherhood effect @ mean Z | -0.0817 | 0.0256 | 0.001 | 12000 |
| time_demands | overall_fit | parent_gap (men) @ mean Z | -0.2958 | 0.0440 | 0.000 | 12000 |
| time_demands | overall_fit | parent_committed (men) @ mean Z | -0.1417 | 0.0293 | 0.000 | 12000 |
| time_demands | overall_fit | married (men) @ mean Z | -0.0925 | 0.0192 | 0.000 | 12000 |
| time_demands | overall_fit | mother-minus-father gap @ mean Z | -0.0017 | 0.0216 | 0.938 | 12000 |
| time_demands | overall_fit | fatherhood x Z | -0.0194 | 0.0213 | 0.363 | 12000 |
| time_demands | overall_fit | mother-minus-father gap x Z (H3/H4) | +0.0055 | 0.0198 | 0.781 | 12000 |
| time_demands | overall_fit | parent_gap gender gap @ mean Z | +0.0450 | 0.0236 | 0.057 | 12000 |
| time_demands | overall_fit | parent_gap gender gap x Z | +0.0077 | 0.0212 | 0.715 | 12000 |

## 3. E2 — paired comparison

Parent-candidate share chosen (0.5 = no bias):

| contrast | gender | P(parent chosen) | n |
| --- | --- | --- | --- |
| parent | female | 0.299 | 2307 |
| parent | male | 0.303 | 2321 |
| parent_committed | female | 0.235 | 2315 |
| parent_committed | male | 0.254 | 2315 |
| parent_gap | female | 0.193 | 2320 |
| parent_gap | male | 0.190 | 2322 |

Position bias — P(chosen = A) = 0.528 (0.5 = none).

Paired differences (parent − childless):

| metric | contrast | gender | mean diff | t | n |
| --- | --- | --- | --- | --- | --- |
| diff_starting_salary_usd | parent | female | -1548.33 | -7.08 | 2307 |
| diff_starting_salary_usd | parent | male | -1217.15 | -5.67 | 2321 |
| diff_starting_salary_usd | parent_committed | female | -1371.92 | -6.32 | 2315 |
| diff_starting_salary_usd | parent_committed | male | -1318.79 | -6.03 | 2315 |
| diff_starting_salary_usd | parent_gap | female | -2126.72 | -8.79 | 2320 |
| diff_starting_salary_usd | parent_gap | male | -2150.73 | -9.35 | 2322 |
| diff_overall_fit | parent | female | -0.38 | -11.44 | 2307 |
| diff_overall_fit | parent | male | -0.38 | -11.29 | 2321 |
| diff_overall_fit | parent_committed | female | -0.51 | -15.57 | 2315 |
| diff_overall_fit | parent_committed | male | -0.51 | -15.53 | 2315 |
| diff_overall_fit | parent_gap | female | -0.70 | -21.26 | 2320 |
| diff_overall_fit | parent_gap | male | -0.70 | -20.97 | 2322 |
| diff_commitment | parent | female | -0.50 | -30.57 | 2307 |
| diff_commitment | parent | male | -0.50 | -30.97 | 2321 |
| diff_commitment | parent_committed | female | -0.34 | -21.87 | 2315 |
| diff_commitment | parent_committed | male | -0.33 | -20.01 | 2315 |
| diff_commitment | parent_gap | female | -0.56 | -38.03 | 2320 |
| diff_commitment | parent_gap | male | -0.59 | -38.09 | 2322 |
| diff_competence | parent | female | -0.22 | -10.58 | 2307 |
| diff_competence | parent | male | -0.21 | -9.97 | 2321 |
| diff_competence | parent_committed | female | -0.26 | -12.82 | 2315 |
| diff_competence | parent_committed | male | -0.25 | -12.29 | 2315 |
| diff_competence | parent_gap | female | -0.34 | -17.13 | 2320 |
| diff_competence | parent_gap | male | -0.35 | -17.77 | 2322 |

![E2 choice](figures/e2_choice.png)

## 4. E3 — ranking pools

Top-1 / Top-3 rates by candidate type:

| composition | gender | family | top1 | top3 |
| --- | --- | --- | --- | --- |
| a | female | none | 0.220 | 0.607 |
| a | female | parent | 0.109 | 0.357 |
| a | male | none | 0.150 | 0.476 |
| b | female | none | 0.184 | 0.506 |
| b | male | none | 0.181 | 0.569 |
| b | male | parent | 0.086 | 0.342 |
| c | female | none | 0.206 | 0.503 |
| c | female | parent | 0.143 | 0.520 |
| c | male | none | 0.196 | 0.465 |
| c | male | parent | 0.116 | 0.527 |
| d | female | parent | 0.202 | 0.510 |
| d | male | parent | 0.132 | 0.490 |

Four-fifths (adverse impact) check:

| group | top3 rate | childless ref | impact ratio |
| --- | --- | --- | --- |
| parent female (comp a) | 0.357 | 0.607 | 0.59 |
| parent male (comp b) | 0.342 | 0.569 | 0.60 |

Position bias (top-1 rate by screen label C1..C6): C1=0.18, C2=0.19, C3=0.16, C4=0.15, C5=0.19, C6=0.12

![E3 top3](figures/e3_top3.png)

## 5. E4 — JD context

| JD variant | gender | family | interview | salary | commitment |
| --- | --- | --- | --- | --- | --- |
| base | female | none | 96.9% | $74,271 | 6.28 |
| base | female | parent | 96.9% | $73,733 | 6.10 |
| base | female | parent_gap | 96.9% | $73,981 | 5.95 |
| base | male | none | 96.9% | $73,762 | 6.26 |
| base | male | parent | 96.5% | $73,246 | 6.02 |
| base | male | parent_gap | 96.9% | $73,727 | 5.91 |
| eeo | female | none | 96.9% | $74,185 | 6.36 |
| eeo | female | parent | 96.9% | $74,527 | 6.25 |
| eeo | female | parent_gap | 96.5% | $74,840 | 5.98 |
| eeo | male | none | 96.9% | $73,906 | 6.30 |
| eeo | male | parent | 96.9% | $74,579 | 6.22 |
| eeo | male | parent_gap | 96.9% | $74,788 | 5.95 |
| family_friendly | female | none | 96.9% | $75,733 | 6.33 |
| family_friendly | female | parent | 96.7% | $76,227 | 6.11 |
| family_friendly | female | parent_gap | 95.8% | $76,102 | 5.94 |
| family_friendly | male | none | 96.7% | $75,642 | 6.26 |
| family_friendly | male | parent | 96.2% | $76,181 | 6.04 |
| family_friendly | male | parent_gap | 96.0% | $75,654 | 5.91 |
| greedy | female | none | 96.2% | $74,104 | 5.59 |
| greedy | female | parent | 96.7% | $74,185 | 5.44 |
| greedy | female | parent_gap | 95.4% | $73,973 | 5.45 |
| greedy | male | none | 96.7% | $73,567 | 5.54 |
| greedy | male | parent | 96.9% | $74,048 | 5.39 |
| greedy | male | parent_gap | 95.8% | $73,990 | 5.40 |
| greedy_ff | female | none | 95.8% | $75,794 | 5.74 |
| greedy_ff | female | parent | 96.9% | $75,838 | 5.65 |
| greedy_ff | female | parent_gap | 95.6% | $75,675 | 5.63 |
| greedy_ff | male | none | 96.5% | $75,371 | 5.73 |
| greedy_ff | male | parent | 96.7% | $75,738 | 5.60 |
| greedy_ff | male | parent_gap | 95.6% | $75,900 | 5.58 |

![E4 gap](figures/e4_gap.png)

## 6. Rationale mentions of family cues

| exp | family | share of rationales mentioning family |
| --- | --- | --- |
| e1 | married | 6.9% |
| e1 | none | 7.0% |
| e1 | parent | 54.3% |
| e1 | parent_committed | 56.3% |
| e1 | parent_gap | 61.9% |
| e1 | pregnant | 99.7% |
| e2 | parent | 55.7% |
| e2 | parent_committed | 54.8% |
| e2 | parent_gap | 61.7% |
| e4 | none | 10.7% |
| e4 | parent | 67.2% |
| e4 | parent_gap | 71.9% |

Within-cell SD (overall_fit): median 1.64, min 1.56, max 1.71.

## 7. Measured tokens & Phase 1 cost estimate

- e1: mean input 892, mean output 121 (n=13200)
- e2: mean input 1490, mean output 203 (n=13936)
- e3: mean input 3748, mean output 83 (n=5760)
- e4: mean input 941, mean output 122 (n=14400)
