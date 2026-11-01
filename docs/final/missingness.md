# R15: refusals and missing choices as outcomes

## 1. Missingness per model × contrast × phase (first attempts; repairs excluded)

| model | phase | contrast | n | refusal% | parse-fail% | no-valid-choice% [95% CI] |
| --- | --- | --- | --- | --- | --- | --- |
| claude | phase3 | gap_parental_only | 9408 | 0.14 | 0.68 | 0.82 [0.61, 1.02] |
| claude | phase3 | gap_travel | 9408 | 0.05 | 0.58 | 0.64 [0.47, 0.81] |
| claude | phase4 | gap_travel | 2880 | 2.19 | 0.42 | 2.6 [1.89, 3.32] |
| claude | phase3 | gender_none | 4032 | 0.27 | 0.45 | 0.72 [0.45, 0.99] |
| claude | phase3 | gender_parent | 4032 | 5.41 | 0.42 | 5.83 [4.88, 6.77] |
| claude | phase4 | gender_parent | 1440 | 4.31 | 0.21 | 4.51 [3.42, 5.61] |
| claude | main | parent | 4800 | 0.77 | 0.35 | 1.12 [0.63, 1.62] |
| claude | phase3 | parent | 8496 | 2.7 | 0.29 | 2.99 [2.39, 3.59] |
| claude | phase4 | parent | 2880 | 2.15 | 0.45 | 2.6 [1.85, 3.36] |
| claude | main | parent_committed | 4800 | 1.15 | 0.56 | 1.71 [1.1, 2.31] |
| claude | phase3 | parent_committed | 7536 | 3.41 | 0.44 | 3.85 [3.13, 4.57] |
| claude | main | parent_gap | 4800 | 1.48 | 0.4 | 1.88 [1.2, 2.55] |
| claude | phase3 | parent_gap | 7536 | 4.9 | 0.28 | 5.18 [4.33, 6.02] |
| claude | phase4 | parent_gap | 2880 | 4.58 | 0.35 | 4.93 [3.92, 5.94] |
| claude | phase3 | personal | 9408 | 0.07 | 0.5 | 0.57 [0.43, 0.72] |
| gpt6 | phase3 | parent_gap | 7536 | 0.0 | 2.06 | 2.06 [1.21, 2.91] |
| qwen38 | phase4 | gap_cert | 960 | 0.0 | 9.9 | 9.9 [7.46, 12.33] |
| qwen38 | phase4 | gap_closure | 960 | 0.0 | 8.23 | 8.23 [6.24, 10.22] |
| qwen38 | phase3 | gap_parental_only | 9408 | 0.0 | 7.72 | 7.72 [6.44, 9.0] |
| qwen38 | phase3 | gap_travel | 9408 | 0.0 | 7.53 | 7.53 [6.37, 8.68] |
| qwen38 | phase4 | gap_travel | 2880 | 0.0 | 5.62 | 5.62 [4.17, 7.08] |
| qwen38 | phase3 | gender_none | 4032 | 0.0 | 5.03 | 5.03 [3.48, 6.59] |
| qwen38 | phase3 | gender_parent | 4032 | 0.0 | 6.18 | 6.18 [4.64, 7.72] |
| qwen38 | phase4 | gender_parent | 1440 | 0.0 | 4.86 | 4.86 [3.16, 6.56] |
| qwen38 | main | parent | 4652 | 0.0 | 14.32 | 14.32 [12.21, 16.43] |
| qwen38 | phase3 | parent | 8496 | 0.0 | 13.72 | 13.72 [12.11, 15.33] |
| qwen38 | phase4 | parent | 2880 | 0.0 | 10.03 | 10.03 [8.31, 11.76] |
| qwen38 | main | parent_committed | 4650 | 0.0 | 14.62 | 14.62 [12.26, 16.98] |
| qwen38 | phase3 | parent_committed | 7536 | 0.0 | 13.73 | 13.73 [12.21, 15.26] |
| qwen38 | main | parent_gap | 4650 | 0.0 | 18.22 | 18.22 [15.75, 20.68] |
| qwen38 | phase3 | parent_gap | 7536 | 0.0 | 16.84 | 16.84 [15.05, 18.63] |
| qwen38 | phase4 | parent_gap | 2880 | 0.0 | 10.62 | 10.62 [9.11, 12.14] |
| qwen38 | phase3 | personal | 9408 | 0.0 | 13.2 | 13.2 [11.44, 14.97] |

### Cued vs placebo missing-rate tests (pair-matched)

| model | phase | cued − placebo (pp) | t | p | n pairs |
| --- | --- | --- | --- | --- | --- |
| deepseek | phase3 | +0.12 | 1.5 | 0.1326 | 112 |
| claude | phase3 | +3.39 | 11.7 | 0.0 | 112 |
| gpt6 | phase3 | +0.74 | 5.5 | 0.0 | 112 |
| qwen38 | phase3 | +5.47 | 13.0 | 0.0 | 112 |

## 2. Manski bounds (headline E2 cells)

P_lo = P·(1−m), P_hi = P·(1−m)+m.

| model | phase | contrast | gender | P | missing | [P_lo, P_hi] | crosses .50 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek | main | parent | female | 0.357 | 0.006 | [0.355, 0.36] |  |
| deepseek | main | parent | male | 0.349 | 0.005 | [0.348, 0.353] |  |
| deepseek | main | parent_gap | female | 0.311 | 0.01 | [0.308, 0.318] |  |
| deepseek | main | parent_gap | male | 0.307 | 0.008 | [0.305, 0.313] |  |
| deepseek | phase3 | parent | female | 0.36 | 0.005 | [0.358, 0.363] |  |
| deepseek | phase3 | parent_gap | female | 0.281 | 0.006 | [0.28, 0.286] |  |
| deepseek | phase3 | parent_gap | male | 0.284 | 0.01 | [0.281, 0.291] |  |
| claude | main | parent | female | 0.233 | 0.012 | [0.23, 0.242] |  |
| claude | main | parent | male | 0.276 | 0.011 | [0.273, 0.284] |  |
| claude | main | parent_gap | female | 0.111 | 0.021 | [0.109, 0.13] |  |
| claude | main | parent_gap | male | 0.131 | 0.017 | [0.129, 0.145] |  |
| claude | phase3 | parent | female | 0.31 | 0.036 | [0.298, 0.335] |  |
| claude | phase3 | parent | male | 0.353 | 0.032 | [0.342, 0.373] |  |
| claude | phase3 | parent_gap | female | 0.117 | 0.067 | [0.109, 0.175] |  |
| claude | phase3 | parent_gap | male | 0.134 | 0.052 | [0.127, 0.178] |  |
| gpt6 | main | parent | female | 0.298 | 0.011 | [0.294, 0.306] |  |
| gpt6 | main | parent | male | 0.304 | 0.008 | [0.301, 0.309] |  |
| gpt6 | main | parent_gap | female | 0.194 | 0.012 | [0.192, 0.204] |  |
| gpt6 | main | parent_gap | male | 0.19 | 0.005 | [0.189, 0.194] |  |
| gpt6 | phase3 | parent | female | 0.348 | 0.009 | [0.345, 0.354] |  |
| gpt6 | phase3 | parent | male | 0.349 | 0.007 | [0.347, 0.354] |  |
| gpt6 | phase3 | parent_gap | female | 0.148 | 0.017 | [0.146, 0.163] |  |
| gpt6 | phase3 | parent_gap | male | 0.154 | 0.023 | [0.151, 0.174] |  |
| qwen38 | main | parent | female | 0.391 | 0.147 | [0.333, 0.48] |  |
| qwen38 | main | parent | male | 0.398 | 0.139 | [0.343, 0.482] |  |
| qwen38 | main | parent_gap | female | 0.214 | 0.197 | [0.172, 0.369] |  |
| qwen38 | main | parent_gap | male | 0.24 | 0.167 | [0.2, 0.367] |  |
| qwen38 | phase3 | parent | female | 0.382 | 0.145 | [0.327, 0.471] |  |
| qwen38 | phase3 | parent | male | 0.401 | 0.124 | [0.351, 0.475] |  |
| qwen38 | phase3 | parent_gap | female | 0.22 | 0.177 | [0.181, 0.358] |  |
| qwen38 | phase3 | parent_gap | male | 0.254 | 0.161 | [0.213, 0.374] |  |

**Cells whose bounds span .50: 0** — none.


## 3. Haiku refusal rate by cue and gender (E2)

### main

- `parent_gap`: 1.48% (n=4800) by gender: {'female': 1.88, 'male': 1.08}
- `parent_committed`: 1.15% (n=4800) by gender: {'female': 1.21, 'male': 1.08}
- `parent`: 0.77% (n=4800) by gender: {'female': 0.83, 'male': 0.71}

### phase3

- `gender_parent`: 5.41% (n=4032) by gender: {}
- `parent_gap`: 4.9% (n=7536) by gender: {'female': 6.33, 'male': 4.88}
- `parent_committed`: 3.41% (n=7536) by gender: {'female': 4.62, 'male': 3.29}
- `parent`: 2.7% (n=8496) by gender: {'female': 3.36, 'male': 2.82}
- `gender_none`: 0.27% (n=4032) by gender: {}
- `gap_parental_only`: 0.14% (n=9408) by gender: {'female': 0.25, 'male': 0.07}
- `personal`: 0.07% (n=9408) by gender: {'female': 0.15, 'male': 0.02}
- `gap_travel`: 0.05% (n=9408) by gender: {'female': 0.1, 'male': 0.02}

## 4. Pooled mothers' choice shares, Haiku excluded

All models: {'parent': 0.318, 'parent_gap': 0.209}
Excl. Haiku: {'parent': 0.35, 'parent_gap': 0.245}
