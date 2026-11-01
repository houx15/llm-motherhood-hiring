# R15: refusals and missing choices as outcomes

## 1. Missingness per model × contrast × phase (first attempts; repairs excluded)

| model | phase | contrast | n | refusal% | parse-fail% | no-valid-choice% [95% CI] |
| --- | --- | --- | --- | --- | --- | --- |
| claude | phase4 | gap_cert | 960 | 0.0 | 99.69 | 99.69 [99.07, 100.31] |
| claude | phase4 | gap_closure | 960 | 0.0 | 99.69 | 99.69 [99.07, 100.31] |
| claude | phase3 | gap_parental_only | 9408 | 0.14 | 0.68 | 0.82 [0.61, 1.02] |
| claude | phase3 | gap_travel | 9408 | 0.05 | 0.58 | 0.64 [0.47, 0.81] |
| claude | phase4 | gap_travel | 2880 | 0.0 | 99.79 | 99.79 [99.38, 100.21] |
| claude | phase3 | gender_none | 4032 | 0.27 | 0.45 | 0.72 [0.45, 0.99] |
| claude | phase3 | gender_parent | 4032 | 5.41 | 0.42 | 5.83 [4.88, 6.77] |
| claude | phase4 | gender_parent | 1440 | 0.0 | 100.0 | 100.0 [100.0, 100.0] |
| claude | main | parent | 4800 | 0.77 | 0.35 | 1.12 [0.63, 1.62] |
| claude | phase3 | parent | 8496 | 2.7 | 0.29 | 2.99 [2.39, 3.59] |
| claude | phase4 | parent | 2880 | 0.0 | 99.79 | 99.79 [99.38, 100.21] |
| claude | main | parent_committed | 4800 | 1.15 | 0.56 | 1.71 [1.1, 2.31] |
| claude | phase3 | parent_committed | 7536 | 3.41 | 0.44 | 3.85 [3.13, 4.57] |
| claude | main | parent_gap | 4800 | 1.48 | 0.4 | 1.88 [1.2, 2.55] |
| claude | phase3 | parent_gap | 7536 | 4.9 | 0.28 | 5.18 [4.33, 6.02] |
| claude | phase4 | parent_gap | 2880 | 0.0 | 99.79 | 99.79 [99.38, 100.21] |
| claude | phase3 | personal | 9408 | 0.07 | 0.5 | 0.57 [0.43, 0.72] |
| deepseek | phase4 | gap_cert | 960 | 0.0 | 98.12 | 98.12 [95.36, 100.89] |
| deepseek | phase4 | gap_closure | 960 | 0.0 | 98.12 | 98.12 [95.36, 100.89] |
| deepseek | phase4 | gap_travel | 2880 | 0.0 | 99.38 | 99.38 [98.45, 100.3] |
| deepseek | phase4 | gender_parent | 1440 | 0.0 | 99.44 | 99.44 [98.57, 100.32] |
| deepseek | phase4 | parent | 2880 | 0.0 | 99.38 | 99.38 [98.45, 100.3] |
| deepseek | phase4 | parent_gap | 2880 | 0.0 | 99.38 | 99.38 [98.45, 100.3] |
| gpt6 | phase4 | gap_cert | 960 | 0.0 | 99.69 | 99.69 [99.07, 100.31] |
| gpt6 | phase4 | gap_closure | 960 | 0.0 | 99.69 | 99.69 [99.07, 100.31] |
| gpt6 | phase4 | gap_travel | 2880 | 0.0 | 99.79 | 99.79 [99.38, 100.21] |
| gpt6 | phase4 | gender_parent | 1440 | 0.0 | 100.0 | 100.0 [100.0, 100.0] |
| gpt6 | main | parent | 4800 | 0.0 | 4.29 | 4.29 [0.39, 8.19] |
| gpt6 | phase4 | parent | 2880 | 0.0 | 99.79 | 99.79 [99.38, 100.21] |
| gpt6 | main | parent_committed | 4800 | 0.0 | 4.79 | 4.79 [1.06, 8.52] |
| gpt6 | main | parent_gap | 4800 | 0.0 | 4.02 | 4.02 [0.3, 7.75] |
| gpt6 | phase3 | parent_gap | 7536 | 0.0 | 2.06 | 2.06 [1.21, 2.91] |
| gpt6 | phase4 | parent_gap | 2880 | 0.0 | 99.79 | 99.79 [99.38, 100.21] |
| qwen38 | phase4 | gap_cert | 960 | 0.0 | 99.79 | 99.79 [99.38, 100.21] |
| qwen38 | phase4 | gap_closure | 960 | 0.0 | 99.79 | 99.79 [99.38, 100.21] |
| qwen38 | phase3 | gap_parental_only | 9408 | 0.0 | 7.76 | 7.76 [6.48, 9.04] |
| qwen38 | phase3 | gap_travel | 9408 | 0.0 | 7.58 | 7.58 [6.42, 8.74] |
| qwen38 | phase4 | gap_travel | 2880 | 0.0 | 99.9 | 99.9 [99.69, 100.1] |
| qwen38 | phase3 | gender_none | 4032 | 0.0 | 5.06 | 5.06 [3.51, 6.61] |
| qwen38 | phase3 | gender_parent | 4032 | 0.0 | 6.2 | 6.2 [4.66, 7.74] |
| qwen38 | phase4 | gender_parent | 1440 | 0.0 | 100.0 | 100.0 [100.0, 100.0] |
| qwen38 | main | parent | 4800 | 0.0 | 16.96 | 16.96 [13.19, 20.72] |
| qwen38 | phase3 | parent | 8496 | 0.0 | 13.81 | 13.81 [12.19, 15.42] |
| qwen38 | phase4 | parent | 2880 | 0.0 | 99.83 | 99.83 [99.48, 100.17] |
| qwen38 | main | parent_committed | 4800 | 0.0 | 17.29 | 17.29 [13.5, 21.08] |
| qwen38 | phase3 | parent_committed | 7536 | 0.0 | 13.81 | 13.81 [12.29, 15.34] |
| qwen38 | main | parent_gap | 4800 | 0.0 | 20.77 | 20.77 [16.99, 24.55] |
| qwen38 | phase3 | parent_gap | 7536 | 0.0 | 16.92 | 16.92 [15.13, 18.71] |
| qwen38 | phase4 | parent_gap | 2880 | 0.0 | 99.79 | 99.79 [99.38, 100.21] |
| qwen38 | phase3 | personal | 9408 | 0.0 | 13.34 | 13.34 [11.58, 15.1] |

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
| gpt6 | main | parent | female | 0.298 | 0.047 | [0.284, 0.33] |  |
| gpt6 | main | parent | male | 0.304 | 0.039 | [0.292, 0.331] |  |
| gpt6 | main | parent_gap | female | 0.194 | 0.044 | [0.185, 0.23] |  |
| gpt6 | main | parent_gap | male | 0.19 | 0.036 | [0.183, 0.22] |  |
| gpt6 | phase3 | parent | female | 0.348 | 0.009 | [0.345, 0.354] |  |
| gpt6 | phase3 | parent | male | 0.349 | 0.007 | [0.347, 0.354] |  |
| gpt6 | phase3 | parent_gap | female | 0.148 | 0.017 | [0.146, 0.163] |  |
| gpt6 | phase3 | parent_gap | male | 0.154 | 0.023 | [0.151, 0.174] |  |
| qwen38 | main | parent | female | 0.391 | 0.174 | [0.323, 0.497] |  |
| qwen38 | main | parent | male | 0.398 | 0.165 | [0.333, 0.498] |  |
| qwen38 | main | parent_gap | female | 0.214 | 0.223 | [0.167, 0.389] |  |
| qwen38 | main | parent_gap | male | 0.24 | 0.193 | [0.194, 0.387] |  |
| qwen38 | phase3 | parent | female | 0.382 | 0.145 | [0.327, 0.472] |  |
| qwen38 | phase3 | parent | male | 0.401 | 0.125 | [0.351, 0.476] |  |
| qwen38 | phase3 | parent_gap | female | 0.22 | 0.177 | [0.181, 0.358] |  |
| qwen38 | phase3 | parent_gap | male | 0.254 | 0.162 | [0.213, 0.375] |  |

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
