# Pooled report — pooled

- Aggregates ALL runs' logs (deduped by call_id, valid parses kept)

## 1. Parse & refusal rates

| exp | calls | parse ok | refusal |
| --- | --- | --- | --- |
| e1 | 13200 | 100.0% | 0.0% |
| e2 | 14400 | 99.7% | 0.0% |
| e3 | 5760 | 100.0% | 0.0% |
| e4 | 14400 | 100.0% | 0.0% |

Highest-refusal cells:

| exp | gender | family | refusal |
| --- | --- | --- | --- |

## 2. E1 — independent scoring

### Cell means (pilot occupations pooled)

| gender | family | n | fit | interview | salary | commitment | SD(fit) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| female | none | 1200 | 8.52 | 92.0% | $84,009 | 6.23 | 1.75 |
| female | married | 1200 | 8.28 | 92.2% | $82,392 | 5.49 | 1.61 |
| female | parent | 1200 | 8.39 | 93.1% | $82,669 | 6.09 | 1.58 |
| female | parent_gap | 1200 | 8.17 | 90.5% | $82,799 | 5.80 | 1.69 |
| female | parent_committed | 1200 | 8.39 | 93.9% | $83,771 | 6.18 | 1.53 |
| female | pregnant | 1200 | 8.37 | 93.9% | $83,158 | 5.87 | 1.47 |
| male | none | 1200 | 8.39 | 90.9% | $83,332 | 6.09 | 1.73 |
| male | married | 1200 | 8.27 | 92.2% | $82,287 | 5.43 | 1.56 |
| male | parent | 1200 | 8.28 | 92.6% | $82,175 | 6.04 | 1.56 |
| male | parent_gap | 1200 | 8.13 | 90.8% | $83,393 | 5.79 | 1.68 |
| male | parent_committed | 1200 | 8.32 | 92.6% | $82,973 | 6.14 | 1.57 |

Ceiling check: share of responses at scale maximum.

- overall_fit: 12.1% at max
- interview: 92.2% at max
- commitment: 24.9% at max
- likability: 6.3% at max

### E1 regression: Y ~ family * female + resume FE (+ occupation FE), cluster SE

| outcome | term | coef | SE | p | n |
| --- | --- | --- | --- | --- | --- |
| overall_fit | married (men) | -0.125 | nan | — | 13200 |
| overall_fit | parent (men) = fatherhood effect | -0.111 | 50.431 | 0.998 | 13200 |
| overall_fit | parent_gap (men) | -0.261 | 130.824 | 0.998 | 13200 |
| overall_fit | parent_committed (men) | -0.072 | 228.164 | 1.000 | 13200 |
| overall_fit | pregnant (women vs childless women) | -0.141 | 25.679 | 0.996 | 13200 |
| overall_fit | parent (women) = motherhood effect | -0.128 | nan | — | 13200 |
| interview | married (men) | +0.013 | 14.655 | 0.999 | 13200 |
| interview | parent (men) = fatherhood effect | +0.017 | nan | — | 13200 |
| interview | parent_gap (men) | -0.002 | nan | — | 13200 |
| interview | parent_committed (men) | +0.017 | 3.337 | 0.996 | 13200 |
| interview | pregnant (women vs childless women) | +0.019 | 8.291 | 0.998 | 13200 |
| interview | parent (women) = motherhood effect | +0.011 | 10.588 | 0.999 | 13200 |
| starting_salary_usd | married (men) | -1045.812 | 2051419.467 | 1.000 | 13200 |
| starting_salary_usd | parent (men) = fatherhood effect | -1157.170 | 314731.652 | 0.997 | 13200 |
| starting_salary_usd | parent_gap (men) | +65.343 | 1540196.458 | 1.000 | 13200 |
| starting_salary_usd | parent_committed (men) | -351.238 | 2827039.708 | 1.000 | 13200 |
| starting_salary_usd | pregnant (women vs childless women) | -849.993 | 2318375.651 | 1.000 | 13200 |
| starting_salary_usd | parent (women) = motherhood effect | -1339.382 | nan | — | 13200 |
| competence | married (men) | -0.033 | 123.333 | 1.000 | 13200 |
| competence | parent (men) = fatherhood effect | -0.050 | 8.303 | 0.995 | 13200 |
| competence | parent_gap (men) | -0.092 | 102.933 | 0.999 | 13200 |
| competence | parent_committed (men) | -0.029 | 212.382 | 1.000 | 13200 |
| competence | pregnant (women vs childless women) | +0.020 | nan | — | 13200 |
| competence | parent (women) = motherhood effect | -0.026 | nan | — | 13200 |
| commitment | married (men) | -0.664 | 155.282 | 0.997 | 13200 |
| commitment | parent (men) = fatherhood effect | -0.047 | 44.375 | 0.999 | 13200 |
| commitment | parent_gap (men) | -0.302 | 123.821 | 0.998 | 13200 |
| commitment | parent_committed (men) | +0.055 | 175.409 | 1.000 | 13200 |
| commitment | pregnant (women vs childless women) | -0.356 | nan | — | 13200 |
| commitment | parent (women) = motherhood effect | -0.136 | nan | — | 13200 |
| promotability | married (men) | -0.118 | 75.030 | 0.999 | 13200 |
| promotability | parent (men) = fatherhood effect | -0.176 | nan | — | 13200 |
| promotability | parent_gap (men) | -0.296 | 246.453 | 0.999 | 13200 |
| promotability | parent_committed (men) | -0.078 | 100.905 | 0.999 | 13200 |
| promotability | pregnant (women vs childless women) | -0.131 | 198.550 | 0.999 | 13200 |
| promotability | parent (women) = motherhood effect | -0.148 | nan | — | 13200 |
| likability | married (men) | -0.294 | nan | — | 13200 |
| likability | parent (men) = fatherhood effect | -0.375 | 53.047 | 0.994 | 13200 |
| likability | parent_gap (men) | -0.261 | nan | — | 13200 |
| likability | parent_committed (men) | -0.289 | nan | — | 13200 |
| likability | pregnant (women vs childless women) | -0.078 | nan | — | 13200 |
| likability | parent (women) = motherhood effect | -0.380 | nan | — | 13200 |

![E1 outcomes](figures/e1_outcomes.png)

![E1 distributions](figures/e1_distributions.png)

### Occupation-moderator regressions (H3/H4):
Y ~ family * female * Z + resume FE, cluster SE; Z standardized (female_share / median_wage / time_demands)

| Z | outcome | term | coef | SE | p | n |
| --- | --- | --- | --- | --- | --- | --- |
| female_share | interview | fatherhood effect @ mean Z | +0.0167 | 0.0113 | 0.141 | 12000 |
| female_share | interview | parent_gap (men) @ mean Z | -0.0017 | 0.0069 | 0.810 | 12000 |
| female_share | interview | parent_committed (men) @ mean Z | +0.0167 | 0.0120 | 0.164 | 12000 |
| female_share | interview | married (men) @ mean Z | +0.0125 | 0.0101 | 0.215 | 12000 |
| female_share | interview | mother-minus-father gap @ mean Z | -0.0058 | 0.0095 | 0.537 | 12000 |
| female_share | interview | fatherhood x Z | -0.0120 | 0.0106 | 0.255 | 12000 |
| female_share | interview | mother-minus-father gap x Z (H3/H4) | +0.0045 | 0.0093 | 0.628 | 12000 |
| female_share | interview | parent_gap gender gap @ mean Z | -0.0133 | 0.0102 | 0.191 | 12000 |
| female_share | interview | parent_gap gender gap x Z | +0.0038 | 0.0101 | 0.709 | 12000 |
| female_share | starting_salary_usd | fatherhood effect @ mean Z | -1157.0833 | 662.8389 | 0.081 | 12000 |
| female_share | starting_salary_usd | parent_gap (men) @ mean Z | +61.2500 | 585.9393 | 0.917 | 12000 |
| female_share | starting_salary_usd | parent_committed (men) @ mean Z | -358.7500 | 543.5377 | 0.509 | 12000 |
| female_share | starting_salary_usd | married (men) @ mean Z | -1045.4167 | 423.2978 | 0.014 | 12000 |
| female_share | starting_salary_usd | mother-minus-father gap @ mean Z | -182.9167 | 711.5740 | 0.797 | 12000 |
| female_share | starting_salary_usd | fatherhood x Z | -77.9808 | 468.5086 | 0.868 | 12000 |
| female_share | starting_salary_usd | mother-minus-father gap x Z (H3/H4) | +309.6221 | 652.6170 | 0.635 | 12000 |
| female_share | starting_salary_usd | parent_gap gender gap @ mean Z | -1271.2500 | 523.3599 | 0.015 | 12000 |
| female_share | starting_salary_usd | parent_gap gender gap x Z | +194.1893 | 328.7394 | 0.555 | 12000 |
| female_share | commitment | fatherhood effect @ mean Z | -0.0467 | 0.0313 | 0.136 | 12000 |
| female_share | commitment | parent_gap (men) @ mean Z | -0.3017 | 0.0313 | 0.000 | 12000 |
| female_share | commitment | parent_committed (men) @ mean Z | +0.0550 | 0.0343 | 0.108 | 12000 |
| female_share | commitment | married (men) @ mean Z | -0.6633 | 0.0348 | 0.000 | 12000 |
| female_share | commitment | mother-minus-father gap @ mean Z | -0.0900 | 0.0288 | 0.002 | 12000 |
| female_share | commitment | fatherhood x Z | -0.0291 | 0.0292 | 0.318 | 12000 |
| female_share | commitment | mother-minus-father gap x Z (H3/H4) | +0.0346 | 0.0278 | 0.213 | 12000 |
| female_share | commitment | parent_gap gender gap @ mean Z | -0.1233 | 0.0325 | 0.000 | 12000 |
| female_share | commitment | parent_gap gender gap x Z | +0.0115 | 0.0288 | 0.690 | 12000 |
| female_share | competence | fatherhood effect @ mean Z | -0.0500 | 0.0191 | 0.009 | 12000 |
| female_share | competence | parent_gap (men) @ mean Z | -0.0917 | 0.0213 | 0.000 | 12000 |
| female_share | competence | parent_committed (men) @ mean Z | -0.0292 | 0.0234 | 0.212 | 12000 |
| female_share | competence | married (men) @ mean Z | -0.0333 | 0.0195 | 0.087 | 12000 |
| female_share | competence | mother-minus-father gap @ mean Z | +0.0242 | 0.0212 | 0.254 | 12000 |
| female_share | competence | fatherhood x Z | -0.0005 | 0.0201 | 0.979 | 12000 |
| female_share | competence | mother-minus-father gap x Z (H3/H4) | +0.0050 | 0.0237 | 0.833 | 12000 |
| female_share | competence | parent_gap gender gap @ mean Z | -0.0175 | 0.0228 | 0.443 | 12000 |
| female_share | competence | parent_gap gender gap x Z | -0.0572 | 0.0240 | 0.017 | 12000 |
| female_share | overall_fit | fatherhood effect @ mean Z | -0.1117 | 0.0439 | 0.011 | 12000 |
| female_share | overall_fit | parent_gap (men) @ mean Z | -0.2617 | 0.0405 | 0.000 | 12000 |
| female_share | overall_fit | parent_committed (men) @ mean Z | -0.0725 | 0.0461 | 0.116 | 12000 |
| female_share | overall_fit | married (men) @ mean Z | -0.1250 | 0.0390 | 0.001 | 12000 |
| female_share | overall_fit | mother-minus-father gap @ mean Z | -0.0167 | 0.0370 | 0.652 | 12000 |
| female_share | overall_fit | fatherhood x Z | -0.0597 | 0.0395 | 0.131 | 12000 |
| female_share | overall_fit | mother-minus-father gap x Z (H3/H4) | +0.0307 | 0.0363 | 0.397 | 12000 |
| female_share | overall_fit | parent_gap gender gap @ mean Z | -0.0867 | 0.0340 | 0.011 | 12000 |
| female_share | overall_fit | parent_gap gender gap x Z | -0.0289 | 0.0374 | 0.440 | 12000 |
| median_wage | interview | fatherhood effect @ mean Z | +0.0167 | 0.0114 | 0.143 | 12000 |
| median_wage | interview | parent_gap (men) @ mean Z | -0.0017 | 0.0069 | 0.810 | 12000 |
| median_wage | interview | parent_committed (men) @ mean Z | +0.0167 | 0.0119 | 0.162 | 12000 |
| median_wage | interview | married (men) @ mean Z | +0.0125 | 0.0101 | 0.215 | 12000 |
| median_wage | interview | mother-minus-father gap @ mean Z | -0.0058 | 0.0095 | 0.538 | 12000 |
| median_wage | interview | fatherhood x Z | +0.0025 | 0.0060 | 0.684 | 12000 |
| median_wage | interview | mother-minus-father gap x Z (H3/H4) | +0.0008 | 0.0068 | 0.906 | 12000 |
| median_wage | interview | parent_gap gender gap @ mean Z | -0.0133 | 0.0102 | 0.189 | 12000 |
| median_wage | interview | parent_gap gender gap x Z | -0.0090 | 0.0072 | 0.212 | 12000 |
| median_wage | starting_salary_usd | fatherhood effect @ mean Z | -1157.0833 | 655.0755 | 0.077 | 12000 |
| median_wage | starting_salary_usd | parent_gap (men) @ mean Z | +61.2500 | 583.4217 | 0.916 | 12000 |
| median_wage | starting_salary_usd | parent_committed (men) @ mean Z | -358.7500 | 534.7769 | 0.502 | 12000 |
| median_wage | starting_salary_usd | married (men) @ mean Z | -1045.4167 | 421.7141 | 0.013 | 12000 |
| median_wage | starting_salary_usd | mother-minus-father gap @ mean Z | -182.9167 | 710.8523 | 0.797 | 12000 |
| median_wage | starting_salary_usd | fatherhood x Z | -898.7182 | 722.2151 | 0.213 | 12000 |
| median_wage | starting_salary_usd | mother-minus-father gap x Z (H3/H4) | -419.8703 | 719.1934 | 0.559 | 12000 |
| median_wage | starting_salary_usd | parent_gap gender gap @ mean Z | -1271.2500 | 511.3420 | 0.013 | 12000 |
| median_wage | starting_salary_usd | parent_gap gender gap x Z | -1005.9627 | 606.8790 | 0.097 | 12000 |
| median_wage | commitment | fatherhood effect @ mean Z | -0.0467 | 0.0314 | 0.138 | 12000 |
| median_wage | commitment | parent_gap (men) @ mean Z | -0.3017 | 0.0310 | 0.000 | 12000 |
| median_wage | commitment | parent_committed (men) @ mean Z | +0.0550 | 0.0340 | 0.106 | 12000 |
| median_wage | commitment | married (men) @ mean Z | -0.6633 | 0.0364 | 0.000 | 12000 |
| median_wage | commitment | mother-minus-father gap @ mean Z | -0.0900 | 0.0290 | 0.002 | 12000 |
| median_wage | commitment | fatherhood x Z | -0.0142 | 0.0332 | 0.669 | 12000 |
| median_wage | commitment | mother-minus-father gap x Z (H3/H4) | -0.0083 | 0.0301 | 0.782 | 12000 |
| median_wage | commitment | parent_gap gender gap @ mean Z | -0.1233 | 0.0325 | 0.000 | 12000 |
| median_wage | commitment | parent_gap gender gap x Z | -0.0014 | 0.0311 | 0.963 | 12000 |
| median_wage | competence | fatherhood effect @ mean Z | -0.0500 | 0.0191 | 0.009 | 12000 |
| median_wage | competence | parent_gap (men) @ mean Z | -0.0917 | 0.0217 | 0.000 | 12000 |
| median_wage | competence | parent_committed (men) @ mean Z | -0.0292 | 0.0234 | 0.212 | 12000 |
| median_wage | competence | married (men) @ mean Z | -0.0333 | 0.0195 | 0.087 | 12000 |
| median_wage | competence | mother-minus-father gap @ mean Z | +0.0242 | 0.0212 | 0.254 | 12000 |
| median_wage | competence | fatherhood x Z | -0.0012 | 0.0142 | 0.932 | 12000 |
| median_wage | competence | mother-minus-father gap x Z (H3/H4) | +0.0072 | 0.0149 | 0.628 | 12000 |
| median_wage | competence | parent_gap gender gap @ mean Z | -0.0175 | 0.0236 | 0.459 | 12000 |
| median_wage | competence | parent_gap gender gap x Z | +0.0184 | 0.0197 | 0.350 | 12000 |
| median_wage | overall_fit | fatherhood effect @ mean Z | -0.1117 | 0.0443 | 0.012 | 12000 |
| median_wage | overall_fit | parent_gap (men) @ mean Z | -0.2617 | 0.0402 | 0.000 | 12000 |
| median_wage | overall_fit | parent_committed (men) @ mean Z | -0.0725 | 0.0460 | 0.115 | 12000 |
| median_wage | overall_fit | married (men) @ mean Z | -0.1250 | 0.0398 | 0.002 | 12000 |
| median_wage | overall_fit | mother-minus-father gap @ mean Z | -0.0167 | 0.0370 | 0.652 | 12000 |
| median_wage | overall_fit | fatherhood x Z | -0.0287 | 0.0291 | 0.324 | 12000 |
| median_wage | overall_fit | mother-minus-father gap x Z (H3/H4) | +0.0344 | 0.0340 | 0.312 | 12000 |
| median_wage | overall_fit | parent_gap gender gap @ mean Z | -0.0867 | 0.0341 | 0.011 | 12000 |
| median_wage | overall_fit | parent_gap gender gap x Z | +0.0047 | 0.0342 | 0.890 | 12000 |
| time_demands | interview | fatherhood effect @ mean Z | +0.0167 | 0.0114 | 0.143 | 12000 |
| time_demands | interview | parent_gap (men) @ mean Z | -0.0017 | 0.0069 | 0.810 | 12000 |
| time_demands | interview | parent_committed (men) @ mean Z | +0.0167 | 0.0120 | 0.164 | 12000 |
| time_demands | interview | married (men) @ mean Z | +0.0125 | 0.0101 | 0.216 | 12000 |
| time_demands | interview | mother-minus-father gap @ mean Z | -0.0058 | 0.0094 | 0.537 | 12000 |
| time_demands | interview | fatherhood x Z | -0.0040 | 0.0063 | 0.525 | 12000 |
| time_demands | interview | mother-minus-father gap x Z (H3/H4) | +0.0053 | 0.0065 | 0.418 | 12000 |
| time_demands | interview | parent_gap gender gap @ mean Z | -0.0133 | 0.0102 | 0.191 | 12000 |
| time_demands | interview | parent_gap gender gap x Z | -0.0049 | 0.0065 | 0.453 | 12000 |
| time_demands | starting_salary_usd | fatherhood effect @ mean Z | -1157.0833 | 661.4871 | 0.080 | 12000 |
| time_demands | starting_salary_usd | parent_gap (men) @ mean Z | +61.2500 | 586.1531 | 0.917 | 12000 |
| time_demands | starting_salary_usd | parent_committed (men) @ mean Z | -358.7500 | 541.8707 | 0.508 | 12000 |
| time_demands | starting_salary_usd | married (men) @ mean Z | -1045.4167 | 424.2483 | 0.014 | 12000 |
| time_demands | starting_salary_usd | mother-minus-father gap @ mean Z | -182.9167 | 709.1282 | 0.796 | 12000 |
| time_demands | starting_salary_usd | fatherhood x Z | -382.5465 | 408.4137 | 0.349 | 12000 |
| time_demands | starting_salary_usd | mother-minus-father gap x Z (H3/H4) | +606.7173 | 583.2115 | 0.298 | 12000 |
| time_demands | starting_salary_usd | parent_gap gender gap @ mean Z | -1271.2500 | 523.8120 | 0.015 | 12000 |
| time_demands | starting_salary_usd | parent_gap gender gap x Z | -24.8673 | 284.0273 | 0.930 | 12000 |
| time_demands | commitment | fatherhood effect @ mean Z | -0.0467 | 0.0315 | 0.138 | 12000 |
| time_demands | commitment | parent_gap (men) @ mean Z | -0.3017 | 0.0313 | 0.000 | 12000 |
| time_demands | commitment | parent_committed (men) @ mean Z | +0.0550 | 0.0343 | 0.109 | 12000 |
| time_demands | commitment | married (men) @ mean Z | -0.6633 | 0.0357 | 0.000 | 12000 |
| time_demands | commitment | mother-minus-father gap @ mean Z | -0.0900 | 0.0290 | 0.002 | 12000 |
| time_demands | commitment | fatherhood x Z | +0.0075 | 0.0257 | 0.769 | 12000 |
| time_demands | commitment | mother-minus-father gap x Z (H3/H4) | -0.0135 | 0.0240 | 0.575 | 12000 |
| time_demands | commitment | parent_gap gender gap @ mean Z | -0.1233 | 0.0325 | 0.000 | 12000 |
| time_demands | commitment | parent_gap gender gap x Z | -0.0078 | 0.0300 | 0.794 | 12000 |
| time_demands | competence | fatherhood effect @ mean Z | -0.0500 | 0.0191 | 0.009 | 12000 |
| time_demands | competence | parent_gap (men) @ mean Z | -0.0917 | 0.0211 | 0.000 | 12000 |
| time_demands | competence | parent_committed (men) @ mean Z | -0.0292 | 0.0235 | 0.214 | 12000 |
| time_demands | competence | married (men) @ mean Z | -0.0333 | 0.0195 | 0.087 | 12000 |
| time_demands | competence | mother-minus-father gap @ mean Z | +0.0242 | 0.0208 | 0.246 | 12000 |
| time_demands | competence | fatherhood x Z | +0.0075 | 0.0144 | 0.603 | 12000 |
| time_demands | competence | mother-minus-father gap x Z (H3/H4) | -0.0349 | 0.0141 | 0.013 | 12000 |
| time_demands | competence | parent_gap gender gap @ mean Z | -0.0175 | 0.0237 | 0.460 | 12000 |
| time_demands | competence | parent_gap gender gap x Z | +0.0074 | 0.0247 | 0.765 | 12000 |
| time_demands | overall_fit | fatherhood effect @ mean Z | -0.1117 | 0.0443 | 0.012 | 12000 |
| time_demands | overall_fit | parent_gap (men) @ mean Z | -0.2617 | 0.0408 | 0.000 | 12000 |
| time_demands | overall_fit | parent_committed (men) @ mean Z | -0.0725 | 0.0462 | 0.116 | 12000 |
| time_demands | overall_fit | married (men) @ mean Z | -0.1250 | 0.0394 | 0.002 | 12000 |
| time_demands | overall_fit | mother-minus-father gap @ mean Z | -0.0167 | 0.0369 | 0.652 | 12000 |
| time_demands | overall_fit | fatherhood x Z | +0.0214 | 0.0346 | 0.536 | 12000 |
| time_demands | overall_fit | mother-minus-father gap x Z (H3/H4) | -0.0354 | 0.0251 | 0.159 | 12000 |
| time_demands | overall_fit | parent_gap gender gap @ mean Z | -0.0867 | 0.0342 | 0.011 | 12000 |
| time_demands | overall_fit | parent_gap gender gap x Z | +0.0025 | 0.0290 | 0.933 | 12000 |

## 3. E2 — paired comparison

Parent-candidate share chosen (0.5 = no bias):

| contrast | gender | P(parent chosen) | n |
| --- | --- | --- | --- |
| parent | female | 0.356 | 2393 |
| parent | male | 0.349 | 2395 |
| parent_committed | female | 0.419 | 2394 |
| parent_committed | male | 0.411 | 2397 |
| parent_gap | female | 0.310 | 2393 |
| parent_gap | male | 0.307 | 2387 |

Position bias — P(chosen = A) = 0.682 (0.5 = none).

Paired differences (parent − childless):

| metric | contrast | gender | mean diff | t | n |
| --- | --- | --- | --- | --- | --- |
| diff_starting_salary_usd | parent | female | -1854.37 | -7.54 | 2393 |
| diff_starting_salary_usd | parent | male | -1975.99 | -8.06 | 2395 |
| diff_starting_salary_usd | parent_committed | female | -891.81 | -3.38 | 2394 |
| diff_starting_salary_usd | parent_committed | male | -900.50 | -3.56 | 2397 |
| diff_starting_salary_usd | parent_gap | female | -2463.95 | -9.03 | 2393 |
| diff_starting_salary_usd | parent_gap | male | -2541.68 | -9.46 | 2387 |
| diff_overall_fit | parent | female | -0.50 | -11.97 | 2393 |
| diff_overall_fit | parent | male | -0.53 | -12.75 | 2395 |
| diff_overall_fit | parent_committed | female | -0.31 | -7.31 | 2394 |
| diff_overall_fit | parent_committed | male | -0.33 | -7.81 | 2397 |
| diff_overall_fit | parent_gap | female | -0.76 | -17.19 | 2393 |
| diff_overall_fit | parent_gap | male | -0.83 | -18.52 | 2387 |
| diff_commitment | parent | female | -0.23 | -10.18 | 2393 |
| diff_commitment | parent | male | -0.25 | -11.20 | 2395 |
| diff_commitment | parent_committed | female | +0.06 | +2.31 | 2394 |
| diff_commitment | parent_committed | male | +0.04 | +1.86 | 2397 |
| diff_commitment | parent_gap | female | -0.86 | -33.72 | 2393 |
| diff_commitment | parent_gap | male | -0.90 | -35.02 | 2387 |
| diff_competence | parent | female | -0.25 | -11.24 | 2393 |
| diff_competence | parent | male | -0.30 | -13.41 | 2395 |
| diff_competence | parent_committed | female | -0.13 | -5.84 | 2394 |
| diff_competence | parent_committed | male | -0.15 | -6.50 | 2397 |
| diff_competence | parent_gap | female | -0.30 | -13.16 | 2393 |
| diff_competence | parent_gap | male | -0.34 | -14.48 | 2387 |

![E2 choice](figures/e2_choice.png)

## 4. E3 — ranking pools

Top-1 / Top-3 rates by candidate type:

| composition | gender | family | top1 | top3 |
| --- | --- | --- | --- | --- |
| a | female | none | 0.229 | 0.612 |
| a | female | parent | 0.105 | 0.341 |
| a | male | none | 0.146 | 0.478 |
| b | female | none | 0.171 | 0.494 |
| b | male | none | 0.200 | 0.599 |
| b | male | parent | 0.089 | 0.320 |
| c | female | none | 0.165 | 0.476 |
| c | female | parent | 0.180 | 0.536 |
| c | male | none | 0.154 | 0.447 |
| c | male | parent | 0.168 | 0.558 |
| d | female | parent | 0.231 | 0.560 |
| d | male | parent | 0.103 | 0.440 |

Four-fifths (adverse impact) check:

| group | top3 rate | childless ref | impact ratio |
| --- | --- | --- | --- |
| parent female (comp a) | 0.341 | 0.612 | 0.56 |
| parent male (comp b) | 0.320 | 0.599 | 0.53 |

Position bias (top-1 rate by screen label C1..C6): C1=0.40, C2=0.20, C3=0.17, C4=0.09, C5=0.07, C6=0.06

![E3 top3](figures/e3_top3.png)

## 5. E4 — JD context

| JD variant | gender | family | interview | salary | commitment |
| --- | --- | --- | --- | --- | --- |
| base | female | none | 95.2% | $69,585 | 6.40 |
| base | female | parent | 96.7% | $69,131 | 6.27 |
| base | female | parent_gap | 94.6% | $69,069 | 6.09 |
| base | male | none | 95.0% | $69,467 | 6.36 |
| base | male | parent | 96.5% | $68,833 | 6.25 |
| base | male | parent_gap | 95.2% | $70,067 | 5.94 |
| eeo | female | none | 95.4% | $69,278 | 6.40 |
| eeo | female | parent | 96.7% | $69,229 | 6.32 |
| eeo | female | parent_gap | 96.2% | $69,562 | 6.01 |
| eeo | male | none | 94.8% | $68,677 | 6.33 |
| eeo | male | parent | 97.1% | $69,462 | 6.23 |
| eeo | male | parent_gap | 95.0% | $70,496 | 5.97 |
| family_friendly | female | none | 95.8% | $70,731 | 6.41 |
| family_friendly | female | parent | 96.5% | $69,983 | 6.18 |
| family_friendly | female | parent_gap | 94.4% | $70,104 | 6.02 |
| family_friendly | male | none | 95.6% | $70,465 | 6.34 |
| family_friendly | male | parent | 97.7% | $69,608 | 6.11 |
| family_friendly | male | parent_gap | 94.4% | $70,140 | 5.94 |
| greedy | female | none | 92.3% | $67,760 | 5.77 |
| greedy | female | parent | 91.0% | $67,322 | 5.33 |
| greedy | female | parent_gap | 89.0% | $65,821 | 5.26 |
| greedy | male | none | 91.7% | $67,952 | 5.75 |
| greedy | male | parent | 91.7% | $67,285 | 5.29 |
| greedy | male | parent_gap | 90.0% | $66,398 | 5.21 |
| greedy_ff | female | none | 94.8% | $68,942 | 5.96 |
| greedy_ff | female | parent | 93.1% | $68,456 | 5.50 |
| greedy_ff | female | parent_gap | 89.0% | $67,965 | 5.43 |
| greedy_ff | male | none | 94.4% | $69,015 | 5.93 |
| greedy_ff | male | parent | 92.9% | $67,704 | 5.48 |
| greedy_ff | male | parent_gap | 88.5% | $67,681 | 5.48 |

![E4 gap](figures/e4_gap.png)

## 6. Rationale mentions of family cues

| exp | family | share of rationales mentioning family |
| --- | --- | --- |
| e1 | married | 5.6% |
| e1 | none | 6.7% |
| e1 | parent | 8.3% |
| e1 | parent_committed | 9.3% |
| e1 | parent_gap | 54.5% |
| e1 | pregnant | 98.3% |
| e2 | parent | 13.5% |
| e2 | parent_committed | 13.0% |
| e2 | parent_gap | 43.1% |
| e4 | none | 7.1% |
| e4 | parent | 47.4% |
| e4 | parent_gap | 77.5% |

Within-cell SD (overall_fit): median 1.58, min 1.47, max 1.75.

## 7. Measured tokens & Phase 1 cost estimate

- e1: mean input 896, mean output 110 (n=13200)
- e2: mean input 1501, mean output 200 (n=14400)
- e3: mean input 3763, mean output 83 (n=5760)
- e4: mean input 948, mean output 112 (n=14400)
