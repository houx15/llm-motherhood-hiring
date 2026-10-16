# Pooled report — pooled_claude_haiku_55

- Model-scoped pool: `claude_haiku_55` — all its runs, deduped by call_id

## 1. Parse & refusal rates

| exp | calls | parse ok | refusal |
| --- | --- | --- | --- |
| e1 | 13200 | 99.8% | 0.2% |
| e2 | 14400 | 98.8% | 1.2% |
| e3 | 5760 | 91.7% | 0.0% |
| e4 | 14400 | 99.7% | 0.2% |

Highest-refusal cells:

| exp | gender | family | refusal |
| --- | --- | --- | --- |
| e2 | female | parent_gap | 1.9% |
| e1 | female | pregnant | 1.5% |
| e2 | female | parent_committed | 1.2% |
| e2 | male | parent_gap | 1.2% |
| e2 | male | parent_committed | 1.2% |

## 2. E1 — independent scoring

### Cell means (pilot occupations pooled)

| gender | family | n | fit | interview | salary | commitment | SD(fit) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| female | none | 1200 | 7.89 | 95.5% | $80,651 | 5.63 | 1.34 |
| female | married | 1198 | 8.09 | 94.4% | $76,413 | 5.39 | 1.32 |
| female | parent | 1200 | 8.23 | 96.7% | $80,199 | 5.85 | 1.23 |
| female | parent_gap | 1200 | 8.04 | 95.5% | $82,298 | 5.80 | 1.22 |
| female | parent_committed | 1200 | 8.15 | 96.1% | $80,318 | 5.88 | 1.24 |
| female | pregnant | 1181 | 7.82 | 86.1% | $61,938 | 5.39 | 1.94 |
| male | none | 1200 | 7.80 | 95.7% | $80,904 | 5.55 | 1.36 |
| male | married | 1199 | 8.01 | 93.6% | $76,435 | 5.41 | 1.37 |
| male | parent | 1200 | 8.11 | 95.9% | $80,354 | 5.83 | 1.27 |
| male | parent_gap | 1197 | 7.94 | 96.7% | $82,826 | 5.77 | 1.20 |
| male | parent_committed | 1200 | 8.03 | 96.3% | $80,512 | 5.84 | 1.32 |

Ceiling check: share of responses at scale maximum.

- overall_fit: 0.0% at max
- interview: 94.8% at max
- commitment: 0.1% at max
- likability: 0.0% at max

### E1 regression: Y ~ family * female + resume FE (+ occupation FE), cluster SE

| outcome | term | coef | SE | p | n |
| --- | --- | --- | --- | --- | --- |
| overall_fit | married (men) | +0.202 | 0.033 | 0.000 | 13175 |
| overall_fit | parent (men) = fatherhood effect | +0.310 | 0.039 | 0.000 | 13175 |
| overall_fit | parent_gap (men) | +0.135 | 0.044 | 0.002 | 13175 |
| overall_fit | parent_committed (men) | +0.226 | 0.039 | 0.000 | 13175 |
| overall_fit | pregnant (women vs childless women) | -0.072 | 0.103 | 0.484 | 13175 |
| overall_fit | parent (women) = motherhood effect | +0.337 | 0.038 | 0.000 | 13175 |
| interview | married (men) | -0.021 | 0.010 | 0.039 | 13175 |
| interview | parent (men) = fatherhood effect | +0.002 | 0.008 | 0.744 | 13175 |
| interview | parent_gap (men) | +0.010 | 0.007 | 0.143 | 13175 |
| interview | parent_committed (men) | +0.007 | 0.006 | 0.277 | 13175 |
| interview | pregnant (women vs childless women) | -0.094 | 0.019 | 0.000 | 13175 |
| interview | parent (women) = motherhood effect | +0.012 | 0.007 | 0.092 | 13175 |
| starting_salary_usd | married (men) | -4493.468 | 1190.280 | 0.000 | 13175 |
| starting_salary_usd | parent (men) = fatherhood effect | -550.000 | 329.173 | 0.095 | 13175 |
| starting_salary_usd | parent_gap (men) | +1895.949 | 607.902 | 0.002 | 13175 |
| starting_salary_usd | parent_committed (men) | -392.500 | 344.780 | 0.255 | 13175 |
| starting_salary_usd | pregnant (women vs childless women) | -18834.399 | 3749.333 | 0.000 | 13175 |
| starting_salary_usd | parent (women) = motherhood effect | -451.667 | 341.052 | 0.185 | 13175 |
| competence | married (men) | +0.096 | 0.025 | 0.000 | 13175 |
| competence | parent (men) = fatherhood effect | +0.121 | 0.025 | 0.000 | 13175 |
| competence | parent_gap (men) | +0.094 | 0.026 | 0.000 | 13175 |
| competence | parent_committed (men) | +0.096 | 0.026 | 0.000 | 13175 |
| competence | pregnant (women vs childless women) | +0.011 | 0.072 | 0.874 | 13175 |
| competence | parent (women) = motherhood effect | +0.124 | 0.024 | 0.000 | 13175 |
| commitment | married (men) | -0.138 | 0.055 | 0.012 | 13175 |
| commitment | parent (men) = fatherhood effect | +0.279 | 0.046 | 0.000 | 13175 |
| commitment | parent_gap (men) | +0.223 | 0.044 | 0.000 | 13175 |
| commitment | parent_committed (men) | +0.293 | 0.051 | 0.000 | 13175 |
| commitment | pregnant (women vs childless women) | -0.242 | 0.091 | 0.008 | 13175 |
| commitment | parent (women) = motherhood effect | +0.218 | 0.041 | 0.000 | 13175 |
| promotability | married (men) | +0.100 | 0.038 | 0.008 | 13175 |
| promotability | parent (men) = fatherhood effect | +0.150 | 0.033 | 0.000 | 13175 |
| promotability | parent_gap (men) | +0.117 | 0.030 | 0.000 | 13175 |
| promotability | parent_committed (men) | +0.179 | 0.039 | 0.000 | 13175 |
| promotability | pregnant (women vs childless women) | +0.012 | 0.079 | 0.877 | 13175 |
| promotability | parent (women) = motherhood effect | +0.143 | 0.031 | 0.000 | 13175 |
| likability | married (men) | +0.304 | 0.041 | 0.000 | 13175 |
| likability | parent (men) = fatherhood effect | +0.327 | 0.034 | 0.000 | 13175 |
| likability | parent_gap (men) | +0.426 | 0.035 | 0.000 | 13175 |
| likability | parent_committed (men) | +0.333 | 0.033 | 0.000 | 13175 |
| likability | pregnant (women vs childless women) | +0.233 | 0.081 | 0.004 | 13175 |
| likability | parent (women) = motherhood effect | +0.374 | 0.032 | 0.000 | 13175 |

![E1 outcomes](figures/e1_outcomes.png)

![E1 distributions](figures/e1_distributions.png)

### Occupation-moderator regressions (H3/H4):
Y ~ family * female * Z + resume FE, cluster SE; Z standardized (female_share / median_wage / time_demands)

| Z | outcome | term | coef | SE | p | n |
| --- | --- | --- | --- | --- | --- | --- |
| female_share | interview | fatherhood effect @ mean Z | +0.0025 | 0.0076 | 0.743 | 11994 |
| female_share | interview | parent_gap (men) @ mean Z | +0.0100 | 0.0067 | 0.136 | 11994 |
| female_share | interview | parent_committed (men) @ mean Z | +0.0067 | 0.0060 | 0.270 | 11994 |
| female_share | interview | married (men) @ mean Z | -0.0211 | 0.0102 | 0.039 | 11994 |
| female_share | interview | mother-minus-father gap @ mean Z | +0.0092 | 0.0054 | 0.090 | 11994 |
| female_share | interview | fatherhood x Z | +0.0072 | 0.0063 | 0.253 | 11994 |
| female_share | interview | mother-minus-father gap x Z (H3/H4) | +0.0044 | 0.0051 | 0.386 | 11994 |
| female_share | interview | parent_gap gender gap @ mean Z | -0.0100 | 0.0067 | 0.137 | 11994 |
| female_share | interview | parent_gap gender gap x Z | -0.0040 | 0.0061 | 0.512 | 11994 |
| female_share | starting_salary_usd | fatherhood effect @ mean Z | -549.9867 | 328.1976 | 0.094 | 11994 |
| female_share | starting_salary_usd | parent_gap (men) @ mean Z | +1893.0867 | 596.6469 | 0.002 | 11994 |
| female_share | starting_salary_usd | parent_committed (men) @ mean Z | -392.4904 | 344.4040 | 0.254 | 11994 |
| female_share | starting_salary_usd | married (men) @ mean Z | -4492.9198 | 1190.6519 | 0.000 | 11994 |
| female_share | starting_salary_usd | mother-minus-father gap @ mean Z | +98.3103 | 321.0255 | 0.759 | 11994 |
| female_share | starting_salary_usd | fatherhood x Z | -245.8617 | 259.1227 | 0.343 | 11994 |
| female_share | starting_salary_usd | mother-minus-father gap x Z (H3/H4) | +424.7626 | 262.2318 | 0.105 | 11994 |
| female_share | starting_salary_usd | parent_gap gender gap @ mean Z | -246.3936 | 446.6833 | 0.581 | 11994 |
| female_share | starting_salary_usd | parent_gap gender gap x Z | +544.2816 | 347.5260 | 0.117 | 11994 |
| female_share | commitment | fatherhood effect @ mean Z | +0.2792 | 0.0457 | 0.000 | 11994 |
| female_share | commitment | parent_gap (men) @ mean Z | +0.2227 | 0.0429 | 0.000 | 11994 |
| female_share | commitment | parent_committed (men) @ mean Z | +0.2933 | 0.0505 | 0.000 | 11994 |
| female_share | commitment | married (men) @ mean Z | -0.1381 | 0.0548 | 0.012 | 11994 |
| female_share | commitment | mother-minus-father gap @ mean Z | -0.0608 | 0.0162 | 0.000 | 11994 |
| female_share | commitment | fatherhood x Z | -0.0406 | 0.0419 | 0.332 | 11994 |
| female_share | commitment | mother-minus-father gap x Z (H3/H4) | -0.0103 | 0.0164 | 0.529 | 11994 |
| female_share | commitment | parent_gap gender gap @ mean Z | -0.0502 | 0.0224 | 0.025 | 11994 |
| female_share | commitment | parent_gap gender gap x Z | +0.0018 | 0.0240 | 0.941 | 11994 |
| female_share | competence | fatherhood effect @ mean Z | +0.1208 | 0.0253 | 0.000 | 11994 |
| female_share | competence | parent_gap (men) @ mean Z | +0.0944 | 0.0263 | 0.000 | 11994 |
| female_share | competence | parent_committed (men) @ mean Z | +0.0958 | 0.0256 | 0.000 | 11994 |
| female_share | competence | married (men) @ mean Z | +0.0963 | 0.0252 | 0.000 | 11994 |
| female_share | competence | mother-minus-father gap @ mean Z | +0.0033 | 0.0145 | 0.819 | 11994 |
| female_share | competence | fatherhood x Z | -0.0095 | 0.0233 | 0.682 | 11994 |
| female_share | competence | mother-minus-father gap x Z (H3/H4) | -0.0025 | 0.0127 | 0.845 | 11994 |
| female_share | competence | parent_gap gender gap @ mean Z | +0.0315 | 0.0186 | 0.091 | 11994 |
| female_share | competence | parent_gap gender gap x Z | -0.0001 | 0.0178 | 0.994 | 11994 |
| female_share | overall_fit | fatherhood effect @ mean Z | +0.3100 | 0.0386 | 0.000 | 11994 |
| female_share | overall_fit | parent_gap (men) @ mean Z | +0.1347 | 0.0436 | 0.002 | 11994 |
| female_share | overall_fit | parent_committed (men) @ mean Z | +0.2258 | 0.0380 | 0.000 | 11994 |
| female_share | overall_fit | married (men) @ mean Z | +0.2020 | 0.0334 | 0.000 | 11994 |
| female_share | overall_fit | mother-minus-father gap @ mean Z | +0.0267 | 0.0221 | 0.227 | 11994 |
| female_share | overall_fit | fatherhood x Z | -0.0665 | 0.0388 | 0.087 | 11994 |
| female_share | overall_fit | mother-minus-father gap x Z (H3/H4) | -0.0014 | 0.0205 | 0.947 | 11994 |
| female_share | overall_fit | parent_gap gender gap @ mean Z | +0.0103 | 0.0303 | 0.733 | 11994 |
| female_share | overall_fit | parent_gap gender gap x Z | +0.0023 | 0.0268 | 0.931 | 11994 |
| median_wage | interview | fatherhood effect @ mean Z | +0.0025 | 0.0077 | 0.744 | 11994 |
| median_wage | interview | parent_gap (men) @ mean Z | +0.0100 | 0.0069 | 0.144 | 11994 |
| median_wage | interview | parent_committed (men) @ mean Z | +0.0067 | 0.0061 | 0.278 | 11994 |
| median_wage | interview | married (men) @ mean Z | -0.0211 | 0.0101 | 0.037 | 11994 |
| median_wage | interview | mother-minus-father gap @ mean Z | +0.0092 | 0.0054 | 0.091 | 11994 |
| median_wage | interview | fatherhood x Z | +0.0033 | 0.0057 | 0.566 | 11994 |
| median_wage | interview | mother-minus-father gap x Z (H3/H4) | +0.0009 | 0.0017 | 0.595 | 11994 |
| median_wage | interview | parent_gap gender gap @ mean Z | -0.0100 | 0.0068 | 0.138 | 11994 |
| median_wage | interview | parent_gap gender gap x Z | +0.0020 | 0.0039 | 0.615 | 11994 |
| median_wage | starting_salary_usd | fatherhood effect @ mean Z | -549.9900 | 329.0863 | 0.095 | 11994 |
| median_wage | starting_salary_usd | parent_gap (men) @ mean Z | +1892.8972 | 603.1074 | 0.002 | 11994 |
| median_wage | starting_salary_usd | parent_committed (men) @ mean Z | -392.5333 | 341.7216 | 0.251 | 11994 |
| median_wage | starting_salary_usd | married (men) @ mean Z | -4493.3173 | 1138.2062 | 0.000 | 11994 |
| median_wage | starting_salary_usd | mother-minus-father gap @ mean Z | +98.3520 | 323.5210 | 0.761 | 11994 |
| median_wage | starting_salary_usd | fatherhood x Z | +125.8235 | 442.0210 | 0.776 | 11994 |
| median_wage | starting_salary_usd | mother-minus-father gap x Z (H3/H4) | +235.0054 | 382.5419 | 0.539 | 11994 |
| median_wage | starting_salary_usd | parent_gap gender gap @ mean Z | -246.1356 | 447.2263 | 0.582 | 11994 |
| median_wage | starting_salary_usd | parent_gap gender gap x Z | +521.3756 | 465.0981 | 0.262 | 11994 |
| median_wage | commitment | fatherhood effect @ mean Z | +0.2792 | 0.0451 | 0.000 | 11994 |
| median_wage | commitment | parent_gap (men) @ mean Z | +0.2227 | 0.0428 | 0.000 | 11994 |
| median_wage | commitment | parent_committed (men) @ mean Z | +0.2933 | 0.0505 | 0.000 | 11994 |
| median_wage | commitment | married (men) @ mean Z | -0.1381 | 0.0550 | 0.012 | 11994 |
| median_wage | commitment | mother-minus-father gap @ mean Z | -0.0608 | 0.0161 | 0.000 | 11994 |
| median_wage | commitment | fatherhood x Z | +0.0793 | 0.0483 | 0.101 | 11994 |
| median_wage | commitment | mother-minus-father gap x Z (H3/H4) | -0.0185 | 0.0116 | 0.111 | 11994 |
| median_wage | commitment | parent_gap gender gap @ mean Z | -0.0502 | 0.0224 | 0.025 | 11994 |
| median_wage | commitment | parent_gap gender gap x Z | -0.0188 | 0.0160 | 0.242 | 11994 |
| median_wage | competence | fatherhood effect @ mean Z | +0.1208 | 0.0240 | 0.000 | 11994 |
| median_wage | competence | parent_gap (men) @ mean Z | +0.0944 | 0.0261 | 0.000 | 11994 |
| median_wage | competence | parent_committed (men) @ mean Z | +0.0958 | 0.0256 | 0.000 | 11994 |
| median_wage | competence | married (men) @ mean Z | +0.0963 | 0.0252 | 0.000 | 11994 |
| median_wage | competence | mother-minus-father gap @ mean Z | +0.0033 | 0.0145 | 0.818 | 11994 |
| median_wage | competence | fatherhood x Z | +0.0717 | 0.0284 | 0.012 | 11994 |
| median_wage | competence | mother-minus-father gap x Z (H3/H4) | -0.0073 | 0.0113 | 0.517 | 11994 |
| median_wage | competence | parent_gap gender gap @ mean Z | +0.0315 | 0.0181 | 0.082 | 11994 |
| median_wage | competence | parent_gap gender gap x Z | +0.0391 | 0.0174 | 0.024 | 11994 |
| median_wage | overall_fit | fatherhood effect @ mean Z | +0.3100 | 0.0387 | 0.000 | 11994 |
| median_wage | overall_fit | parent_gap (men) @ mean Z | +0.1347 | 0.0438 | 0.002 | 11994 |
| median_wage | overall_fit | parent_committed (men) @ mean Z | +0.2258 | 0.0394 | 0.000 | 11994 |
| median_wage | overall_fit | married (men) @ mean Z | +0.2021 | 0.0327 | 0.000 | 11994 |
| median_wage | overall_fit | mother-minus-father gap @ mean Z | +0.0267 | 0.0218 | 0.220 | 11994 |
| median_wage | overall_fit | fatherhood x Z | +0.0625 | 0.0428 | 0.144 | 11994 |
| median_wage | overall_fit | mother-minus-father gap x Z (H3/H4) | -0.0330 | 0.0170 | 0.052 | 11994 |
| median_wage | overall_fit | parent_gap gender gap @ mean Z | +0.0103 | 0.0299 | 0.730 | 11994 |
| median_wage | overall_fit | parent_gap gender gap x Z | +0.0423 | 0.0259 | 0.102 | 11994 |
| time_demands | interview | fatherhood effect @ mean Z | +0.0025 | 0.0077 | 0.744 | 11994 |
| time_demands | interview | parent_gap (men) @ mean Z | +0.0100 | 0.0069 | 0.144 | 11994 |
| time_demands | interview | parent_committed (men) @ mean Z | +0.0067 | 0.0061 | 0.277 | 11994 |
| time_demands | interview | married (men) @ mean Z | -0.0211 | 0.0102 | 0.039 | 11994 |
| time_demands | interview | mother-minus-father gap @ mean Z | +0.0092 | 0.0054 | 0.091 | 11994 |
| time_demands | interview | fatherhood x Z | -0.0004 | 0.0035 | 0.906 | 11994 |
| time_demands | interview | mother-minus-father gap x Z (H3/H4) | -0.0011 | 0.0020 | 0.586 | 11994 |
| time_demands | interview | parent_gap gender gap @ mean Z | -0.0100 | 0.0068 | 0.138 | 11994 |
| time_demands | interview | parent_gap gender gap x Z | +0.0008 | 0.0041 | 0.856 | 11994 |
| time_demands | starting_salary_usd | fatherhood effect @ mean Z | -550.0238 | 328.4251 | 0.094 | 11994 |
| time_demands | starting_salary_usd | parent_gap (men) @ mean Z | +1894.2488 | 606.9268 | 0.002 | 11994 |
| time_demands | starting_salary_usd | parent_committed (men) @ mean Z | -392.5343 | 343.1029 | 0.253 | 11994 |
| time_demands | starting_salary_usd | married (men) @ mean Z | -4492.7612 | 1190.0299 | 0.000 | 11994 |
| time_demands | starting_salary_usd | mother-minus-father gap @ mean Z | +98.3521 | 323.9955 | 0.761 | 11994 |
| time_demands | starting_salary_usd | fatherhood x Z | -221.3604 | 187.7357 | 0.238 | 11994 |
| time_demands | starting_salary_usd | mother-minus-father gap x Z (H3/H4) | +174.6042 | 147.4153 | 0.236 | 11994 |
| time_demands | starting_salary_usd | parent_gap gender gap @ mean Z | -247.6149 | 450.8227 | 0.583 | 11994 |
| time_demands | starting_salary_usd | parent_gap gender gap x Z | +60.5920 | 249.2674 | 0.808 | 11994 |
| time_demands | commitment | fatherhood effect @ mean Z | +0.2792 | 0.0459 | 0.000 | 11994 |
| time_demands | commitment | parent_gap (men) @ mean Z | +0.2227 | 0.0436 | 0.000 | 11994 |
| time_demands | commitment | parent_committed (men) @ mean Z | +0.2933 | 0.0509 | 0.000 | 11994 |
| time_demands | commitment | married (men) @ mean Z | -0.1381 | 0.0551 | 0.012 | 11994 |
| time_demands | commitment | mother-minus-father gap @ mean Z | -0.0608 | 0.0161 | 0.000 | 11994 |
| time_demands | commitment | fatherhood x Z | -0.0158 | 0.0358 | 0.659 | 11994 |
| time_demands | commitment | mother-minus-father gap x Z (H3/H4) | +0.0164 | 0.0109 | 0.131 | 11994 |
| time_demands | commitment | parent_gap gender gap @ mean Z | -0.0502 | 0.0224 | 0.025 | 11994 |
| time_demands | commitment | parent_gap gender gap x Z | -0.0073 | 0.0172 | 0.671 | 11994 |
| time_demands | competence | fatherhood effect @ mean Z | +0.1208 | 0.0253 | 0.000 | 11994 |
| time_demands | competence | parent_gap (men) @ mean Z | +0.0943 | 0.0263 | 0.000 | 11994 |
| time_demands | competence | parent_committed (men) @ mean Z | +0.0958 | 0.0255 | 0.000 | 11994 |
| time_demands | competence | married (men) @ mean Z | +0.0963 | 0.0251 | 0.000 | 11994 |
| time_demands | competence | mother-minus-father gap @ mean Z | +0.0033 | 0.0145 | 0.818 | 11994 |
| time_demands | competence | fatherhood x Z | -0.0079 | 0.0182 | 0.665 | 11994 |
| time_demands | competence | mother-minus-father gap x Z (H3/H4) | +0.0094 | 0.0100 | 0.347 | 11994 |
| time_demands | competence | parent_gap gender gap @ mean Z | +0.0315 | 0.0186 | 0.091 | 11994 |
| time_demands | competence | parent_gap gender gap x Z | -0.0048 | 0.0129 | 0.708 | 11994 |
| time_demands | overall_fit | fatherhood effect @ mean Z | +0.3100 | 0.0393 | 0.000 | 11994 |
| time_demands | overall_fit | parent_gap (men) @ mean Z | +0.1346 | 0.0438 | 0.002 | 11994 |
| time_demands | overall_fit | parent_committed (men) @ mean Z | +0.2258 | 0.0394 | 0.000 | 11994 |
| time_demands | overall_fit | married (men) @ mean Z | +0.2021 | 0.0332 | 0.000 | 11994 |
| time_demands | overall_fit | mother-minus-father gap @ mean Z | +0.0267 | 0.0218 | 0.222 | 11994 |
| time_demands | overall_fit | fatherhood x Z | -0.0014 | 0.0461 | 0.976 | 11994 |
| time_demands | overall_fit | mother-minus-father gap x Z (H3/H4) | +0.0290 | 0.0193 | 0.133 | 11994 |
| time_demands | overall_fit | parent_gap gender gap @ mean Z | +0.0104 | 0.0301 | 0.730 | 11994 |
| time_demands | overall_fit | parent_gap gender gap x Z | +0.0347 | 0.0242 | 0.151 | 11994 |

## 3. E2 — paired comparison

Parent-candidate share chosen (0.5 = no bias):

| contrast | gender | P(parent chosen) | n |
| --- | --- | --- | --- |
| parent | female | 0.232 | 2379 |
| parent | male | 0.275 | 2382 |
| parent_committed | female | 0.266 | 2371 |
| parent_committed | male | 0.331 | 2371 |
| parent_gap | female | 0.111 | 2355 |
| parent_gap | male | 0.131 | 2372 |

Position bias — P(chosen = A) = 0.390 (0.5 = none).

Paired differences (parent − childless):

| metric | contrast | gender | mean diff | t | n |
| --- | --- | --- | --- | --- | --- |
| diff_starting_salary_usd | parent | female | -1331.65 | -7.46 | 2379 |
| diff_starting_salary_usd | parent | male | -1194.16 | -6.53 | 2382 |
| diff_starting_salary_usd | parent_committed | female | -901.73 | -5.06 | 2371 |
| diff_starting_salary_usd | parent_committed | male | -816.32 | -4.42 | 2371 |
| diff_starting_salary_usd | parent_gap | female | -942.25 | -5.51 | 2355 |
| diff_starting_salary_usd | parent_gap | male | -607.08 | -3.43 | 2372 |
| diff_overall_fit | parent | female | -0.59 | -18.26 | 2379 |
| diff_overall_fit | parent | male | -0.51 | -15.23 | 2382 |
| diff_overall_fit | parent_committed | female | -0.54 | -15.83 | 2371 |
| diff_overall_fit | parent_committed | male | -0.40 | -11.48 | 2371 |
| diff_overall_fit | parent_gap | female | -0.87 | -29.97 | 2355 |
| diff_overall_fit | parent_gap | male | -0.80 | -26.96 | 2372 |
| diff_commitment | parent | female | -0.32 | -16.81 | 2379 |
| diff_commitment | parent | male | -0.19 | -8.93 | 2382 |
| diff_commitment | parent_committed | female | -0.08 | -4.00 | 2371 |
| diff_commitment | parent_committed | male | +0.10 | +4.32 | 2371 |
| diff_commitment | parent_gap | female | -1.00 | -47.46 | 2355 |
| diff_commitment | parent_gap | male | -0.90 | -39.44 | 2372 |
| diff_competence | parent | female | -0.17 | -8.41 | 2379 |
| diff_competence | parent | male | -0.16 | -7.82 | 2382 |
| diff_competence | parent_committed | female | -0.12 | -5.79 | 2371 |
| diff_competence | parent_committed | male | -0.10 | -4.65 | 2371 |
| diff_competence | parent_gap | female | -0.15 | -8.30 | 2355 |
| diff_competence | parent_gap | male | -0.13 | -6.91 | 2372 |

![E2 choice](figures/e2_choice.png)

## 4. E3 — ranking pools

Top-1 / Top-3 rates by candidate type:

| composition | gender | family | top1 | top3 |
| --- | --- | --- | --- | --- |
| a | female | none | 0.243 | 0.647 |
| a | female | parent | 0.028 | 0.089 |
| a | male | none | 0.162 | 0.539 |
| b | female | none | 0.226 | 0.571 |
| b | male | none | 0.153 | 0.598 |
| b | male | parent | 0.017 | 0.092 |
| c | female | none | 0.176 | 0.541 |
| c | female | parent | 0.152 | 0.451 |
| c | male | none | 0.217 | 0.538 |
| c | male | parent | 0.086 | 0.480 |
| d | female | parent | 0.205 | 0.534 |
| d | male | parent | 0.128 | 0.466 |

Four-fifths (adverse impact) check:

| group | top3 rate | childless ref | impact ratio |
| --- | --- | --- | --- |
| parent female (comp a) | 0.089 | 0.647 | 0.14 |
| parent male (comp b) | 0.092 | 0.598 | 0.15 |

Position bias (top-1 rate by screen label C1..C6): C1=0.19, C2=0.22, C3=0.21, C4=0.11, C5=0.13, C6=0.14

![E3 top3](figures/e3_top3.png)

## 5. E4 — JD context

| JD variant | gender | family | interview | salary | commitment |
| --- | --- | --- | --- | --- | --- |
| base | female | none | 99.2% | $67,342 | 5.77 |
| base | female | parent | 100.0% | $66,860 | 5.95 |
| base | female | parent_gap | 100.0% | $68,681 | 5.92 |
| base | male | none | 99.0% | $67,554 | 5.72 |
| base | male | parent | 99.4% | $65,475 | 5.95 |
| base | male | parent_gap | 99.2% | $68,177 | 5.90 |
| eeo | female | none | 99.6% | $67,088 | 5.83 |
| eeo | female | parent | 98.5% | $64,094 | 5.95 |
| eeo | female | parent_gap | 99.2% | $64,270 | 5.89 |
| eeo | male | none | 99.0% | $67,254 | 5.76 |
| eeo | male | parent | 99.4% | $66,398 | 5.96 |
| eeo | male | parent_gap | 100.0% | $65,590 | 5.92 |
| family_friendly | female | none | 99.8% | $67,994 | 5.79 |
| family_friendly | female | parent | 98.3% | $67,240 | 5.95 |
| family_friendly | female | parent_gap | 98.5% | $66,092 | 5.91 |
| family_friendly | male | none | 99.2% | $68,450 | 5.71 |
| family_friendly | male | parent | 99.6% | $67,942 | 5.95 |
| family_friendly | male | parent_gap | 98.3% | $68,025 | 5.90 |
| greedy | female | none | 99.8% | $67,825 | 5.59 |
| greedy | female | parent | 99.2% | $66,510 | 5.81 |
| greedy | female | parent_gap | 96.7% | $63,916 | 5.75 |
| greedy | male | none | 99.0% | $67,781 | 5.58 |
| greedy | male | parent | 98.8% | $67,254 | 5.81 |
| greedy | male | parent_gap | 96.2% | $66,560 | 5.72 |
| greedy_ff | female | none | 99.0% | $68,588 | 5.71 |
| greedy_ff | female | parent | 93.5% | $59,649 | 5.75 |
| greedy_ff | female | parent_gap | 91.9% | $60,712 | 5.75 |
| greedy_ff | male | none | 99.2% | $68,740 | 5.61 |
| greedy_ff | male | parent | 94.3% | $64,962 | 5.74 |
| greedy_ff | male | parent_gap | 93.2% | $64,406 | 5.77 |

![E4 gap](figures/e4_gap.png)

## 6. Rationale mentions of family cues

| exp | family | share of rationales mentioning family |
| --- | --- | --- |
| e1 | married | 4.7% |
| e1 | none | 6.7% |
| e1 | parent | 92.2% |
| e1 | parent_committed | 91.6% |
| e1 | parent_gap | 96.6% |
| e1 | pregnant | 96.8% |
| e2 | parent | 44.4% |
| e2 | parent_committed | 42.5% |
| e2 | parent_gap | 57.7% |
| e4 | none | 7.5% |
| e4 | parent | 96.1% |
| e4 | parent_gap | 98.0% |

Within-cell SD (overall_fit): median 1.32, min 1.20, max 1.94.

## 7. Measured tokens & Phase 1 cost estimate

- e1: mean input 1565, mean output 170 (n=13200)
- e2: mean input 2646, mean output 311 (n=14400)
- e3: mean input 6864, mean output 144 (n=5290)
- e4: mean input 1629, mean output 169 (n=14400)
