# Phase-3 occupational design (SPEC_PHASE3.md §5)

All values computed from the files in `data/raw` (O*NET 31.0 Work Activities
importance scale, z-scored across all O*NET occupations; CPS Table 11 2025
female share, count-weighted where two CPS rows are combined; OEWS May 2025
median wage). SOC vintage fixes, verified against O*NET titles:
- `warehouse_supervisor`: ['53-1042', '53-1043'] (53-1042 + 53-1043)
- `financial_analyst`: ['13-2099.01'] (13-2099.01)
- `pharmacist`: ['29-1051'] (29-1051)

## Confound reduction

| correlation with female share | O20 only (n=20) | O20+O8 (n=28) |
| --- | --- | --- |
| care | +0.531 | +0.322 |
| physical | -0.257 | -0.389 |
| analytic | -0.165 | -0.303 |
| manage | +0.123 | -0.046 |

Selection objective (|corr(female, care)| + |corr(female, physical)|) = 0.711; 24 quota-feasible combinations of C(13,8) searched exhaustively.

**Honest limitation:** every quota-feasible combination *deepens* the female-share–
physical correlation (best achievable ≈ −0.32 vs −0.26 at baseline), because the
quota occupations that are male-dominated and care-oriented (police, EMT, security)
and the skilled trade (electrician) are all above-average physical, while the
female-dominated additions (housekeeper, childcare) are only mildly physical. The
design's real achievement is **separability**: O20 had *no* male-dominated care or
female-dominated physical occupation (a perfect confound); O28 contains both, so
care and female share can be entered jointly in occupation-level regressions
(§8.5) even though the bivariate correlations remain nonzero.

## Selection frontier (top 5 of the quota-feasible combinations)

| objective | corr(female, care) | corr(female, physical) | combination |
| --- | --- | --- | --- |
| 0.711 | +0.322 | -0.389 | childcare_worker, electrician, emt_paramedic, health_services_manager, housekeeper, police_officer, security_guard, veterinarian **(selected)** |
| 0.715 | +0.350 | -0.365 | childcare_worker, electrician, emt_paramedic, health_services_manager, home_health_aide, police_officer, security_guard, veterinarian |
| 0.716 | +0.399 | -0.317 | childcare_worker, electrician, emt_paramedic, health_services_manager, home_health_aide, housekeeper, police_officer, veterinarian |
| 0.723 | +0.346 | -0.378 | electrician, emt_paramedic, health_services_manager, home_health_aide, housekeeper, police_officer, security_guard, veterinarian |
| 0.750 | +0.336 | -0.414 | childcare_worker, electrician, emt_paramedic, firefighter, health_services_manager, housekeeper, security_guard, veterinarian |

## Selected occupations (O8)

| id | title | female share | median wage | physical z | care z | analytic z | manage z | quota | license shown on résumé |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| childcare_worker | Childcare Worker | 0.932 | $34,980 | +0.26 | +0.64 | -0.94 | -0.08 | female_physical | — |
| electrician | Electrician | 0.035 | $63,190 | +1.63 | -0.11 | +0.19 | +1.64 | male_trade | Journeyman electrician license |
| emt_paramedic | EMT / Paramedic | 0.351 | $48,150 | +1.39 | +1.96 | -0.10 | +0.41 | male_care | National Registry EMT / paramedic certification |
| health_services_manager | Medical and Health Services Manager | 0.753 | $123,860 | -0.78 | +0.53 | +0.97 | +2.16 | female_analytic | — |
| housekeeper | Housekeeper (Maids and Housekeeping Cleaners) | 0.864 | $35,510 | +0.15 | +0.48 | -1.80 | -1.05 | female_physical | — |
| police_officer | Police Officer (Patrol) | 0.164 | $76,210 | +0.90 | +1.31 | +0.66 | -0.05 | male_care | POST law-enforcement certification |
| security_guard | Security Guard | 0.229 | $38,020 | +0.78 | +1.48 | +0.67 | +1.59 | optional | State guard card |
| veterinarian | Veterinarian | 0.709 | $130,100 | -0.22 | +1.14 | -0.21 | +0.15 | female_analytic | DVM and state veterinary license |

## Full correlation matrices

### O20 only

|              |   female_share |   median_wage |   physical |   care |   analytic |   manage |
|:-------------|---------------:|--------------:|-----------:|-------:|-----------:|---------:|
| female_share |           1    |         -0.17 |      -0.26 |   0.53 |      -0.16 |     0.12 |
| median_wage  |          -0.17 |          1    |      -0.52 |   0.08 |       0.38 |    -0.09 |
| physical     |          -0.26 |         -0.52 |       1    |   0.22 |      -0.35 |     0.22 |
| care         |           0.53 |          0.08 |       0.22 |   1    |      -0.38 |     0.21 |
| analytic     |          -0.16 |          0.38 |      -0.35 |  -0.38 |       1    |     0.22 |
| manage       |           0.12 |         -0.09 |       0.22 |   0.21 |       0.22 |     1    |

### O20 + O8

|              |   female_share |   median_wage |   physical |   care |   analytic |   manage |
|:-------------|---------------:|--------------:|-----------:|-------:|-----------:|---------:|
| female_share |           1    |         -0.09 |      -0.39 |   0.32 |      -0.3  |    -0.05 |
| median_wage  |          -0.09 |          1    |      -0.56 |  -0.02 |       0.39 |    -0.05 |
| physical     |          -0.39 |         -0.56 |       1    |   0.33 |      -0.23 |     0.23 |
| care         |           0.32 |         -0.02 |       0.33 |   1    |      -0.25 |     0.19 |
| analytic     |          -0.3  |          0.39 |      -0.23 |  -0.25 |       1    |     0.37 |
| manage       |          -0.05 |         -0.05 |       0.23 |   0.19 |       0.37 |     1    |

## Candidates not selected

- home_health_aide (female_physical)
- firefighter (male_care)
- clinical_psychologist (female_analytic)
- janitor (optional)

## Data misses (not filled)

- clinical_psychologist: CPS female share not found for ['Clinical and counseling psychologists']
