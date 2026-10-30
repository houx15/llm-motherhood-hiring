### Table 1. E2 probability the parent candidate is chosen (mean of 40 résumé-pair cluster means; t vs 0.5, df 39)

| Contrast | DeepSeek F / M | Haiku F / M | Luna F / M | Qwen F / M |
| --- | --- | --- | --- | --- |
| Parent (PTA) | .357 (-11) / .349 (-10) | .233 (-12) / .277 (-10) | .297 (-8) / .294 (-8) | .391 (-3) / .395 (-4) |
| Parent + committed | .419 (-8) / .411 (-8) | .266 (-10) / .323 (-8) | .228 (-9) / .246 (-8) | .344 (-6) / .450 (-2) |
| Parent + leave gap | .310 (-12) / .308 (-13) | .111 (-19) / .152 (-12) | .186 (-8) / .184 (-8) | .248 (-8) / .216 (-13) |

### Table 2. E2 mother-minus-father differences (pair-matched t-tests; Holm over 12 tests)

| Contrast | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| Parent (PTA) | +0.008 (t 0.8) | -0.044 (t -3.2; Holm p=0.030)** | -0.004 (t -0.6) | -0.005 (t -0.1) |
| Parent + committed | +0.008 (t 1.2) | -0.065 (t -4.6; Holm p=0.000)** | -0.018 (t -1.8) | -0.085 (t -2.9; Holm p=0.064)* |
| Parent + leave gap | +0.002 (t 0.2) | -0.019 (t -2.0; Holm p=0.442)* | +0.002 (t 0.3) | +0.024 (t 0.8) |

### Table 3. E3 top-3 impact ratios for token parents (naïve → résumé-FE adjusted; FE t)

| | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| Mothers | .463 → **.633** (-5.9) | .463 → **.633** (-5.9) | .463 → **.633** (-5.9) | .463 → **.633** (-5.9) |
| Fathers | .476 → **.653** (-7.3) | .476 → **.653** (-7.3) | .476 → **.653** (-7.3) | .476 → **.653** (-7.3) |

### Table 4. E4 leave-gap interview penalty (pp; résumé-FE DiD vs base, 32 résumé clusters)

| | DeepSeek F / M | Haiku F / M | Luna F / M | Qwen F / M |
| --- | --- | --- | --- | --- |
| Base (gap) | -0.6 (t -1.4) / +0.2 (t 0.3) | +0.8 (t 1.0) / +0.2 (t 0.2) | -0.0 (t -0.0) / -0.0 (t nan) | +0.4 (t 1.4) / -0.0 (t -0.0) |
| EEO (DiD) | +1.5 (t 1.5) / -0.0 (t -0.0) | -1.3 (t -1.7) / +0.8 (t 1.0) | -0.4 (t -0.6) / -0.0 (t nan) | -1.0 (t -0.7) / -0.4 (t -0.6) |
| Family-friendly (DiD) | -0.8 (t -0.6) / -1.5 (t -1.2) | -2.1 (t -1.4) / -1.1 (t -0.6) | -1.0 (t -1.0) / -0.6 (t -1.0) | -1.9 (t -1.5) / -0.4 (t -1.0) |
| Greedy (DiD) | -2.7 (t -2.3)* / -1.9 (t -1.1) | -4.0 (t -1.9) / -2.9 (t -1.1) | -0.8 (t -1.0) / -0.8 (t -1.0) | -2.1 (t -2.1)* / -1.0 (t -0.5) |
| Greedy+FF (DiD) | -5.2 (t -2.9)** / -6.0 (t -2.2)* | -8.0 (t -2.8)** / -6.2 (t -1.7) | -0.2 (t -1.0) / -0.8 (t -1.0) | -1.2 (t -1.4) / -3.1 (t -2.0) |

### Table 5. Pregnancy within-résumé gaps (résumé FE, clustered SE)

| Outcome | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| Interview (pp) | +1.9 (t 1.8) | -9.4 (t -4.8)*** | +0.8 (t 1.5) | +0.7 (t 0.9) |
| Fit (points) | -0.1 (t -2.2)* | -0.1 (t -0.7) | +0.0 (t 1.0) | +0.1 (t 2.6)* |
| Competence | +0.0 (t 0.9) | +0.0 (t 0.1) | +0.1 (t 3.6)*** | +0.1 (t 4.4)*** |
| Commitment | -0.4 (t -12.4)*** | -0.2 (t -2.7)** | +0.0 (t 1.2) | +0.4 (t 6.2)*** |

### Table 6. Salary withholding ($0) and interview denial, E1 women

| Model | withheld: none | pregnant | married | interview: pregnant|withheld | pregnant|offered |
| --- | --- | --- | --- | --- | --- |
| DeepSeek | 1.6% | 2.0% | 2.2% | 0.000 (n=24) | 0.958 (n=1176) |
| Haiku | 3.1% | 19.9% | 7.3% | 0.302 (n=235) | 1.000 (n=947) |
| Luna | 0.9% | 3.1% | 1.3% | 0.000 (n=37) | 0.953 (n=1163) |
| Qwen | 4.2% | 5.8% | 4.2% | 0.000 (n=70) | 0.970 (n=1133) |
