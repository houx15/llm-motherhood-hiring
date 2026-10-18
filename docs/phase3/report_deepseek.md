# Phase-3 report — deepseek_v41_flash

## Cue-level parent penalties (E2 P(parent chosen))

| level            | contrast          |    n |   P(parent) | gender   |
|:-----------------|:------------------|-----:|------------:|:---------|
| L0 name          | gap_parental_only | 1389 |       0.395 | female   |
| L0 name          | gap_parental_only | 1389 |       0.41  | male     |
| L0 name          | gap_travel        | 1389 |       0.384 | female   |
| L0 name          | gap_travel        | 1389 |       0.386 | male     |
| L0 name          | parent            |  936 |       0.357 | female   |
| L0 name          | parent            |  935 |       0.35  | male     |
| L0 name          | parent_committed  |  432 |       0.414 | female   |
| L0 name          | parent_committed  |  432 |       0.396 | male     |
| L0 name          | parent_gap        |  432 |       0.238 | female   |
| L0 name          | parent_gap        |  430 |       0.244 | male     |
| L0 name          | personal          | 1387 |       0.464 | female   |
| L0 name          | personal          | 1383 |       0.452 | male     |
| L1 name+field    | gap_parental_only | 1392 |       0.393 | female   |
| L1 name+field    | gap_parental_only | 1388 |       0.4   | male     |
| L1 name+field    | gap_travel        | 1386 |       0.371 | female   |
| L1 name+field    | gap_travel        | 1391 |       0.373 | male     |
| L1 name+field    | parent            | 1388 |       0.355 | female   |
| L1 name+field    | parent            | 1390 |       0.359 | male     |
| L1 name+field    | parent_committed  | 1391 |       0.428 | female   |
| L1 name+field    | parent_committed  | 1389 |       0.449 | male     |
| L1 name+field    | parent_gap        | 1383 |       0.293 | female   |
| L1 name+field    | parent_gap        | 1384 |       0.301 | male     |
| L1 name+field    | personal          | 1391 |       0.47  | female   |
| L1 name+field    | personal          | 1387 |       0.461 | male     |
| L2 initial+field | gap_parental_only | 1386 |       0.403 | female   |
| L2 initial+field | gap_parental_only | 1390 |       0.391 | male     |
| L2 initial+field | gap_travel        | 1389 |       0.386 | female   |
| L2 initial+field | gap_travel        | 1390 |       0.394 | male     |
| L2 initial+field | parent            | 1388 |       0.367 | female   |
| L2 initial+field | parent            | 1389 |       0.361 | male     |
| L2 initial+field | parent_committed  | 1389 |       0.429 | female   |
| L2 initial+field | parent_committed  | 1391 |       0.436 | male     |
| L2 initial+field | parent_gap        | 1389 |       0.284 | female   |
| L2 initial+field | parent_gap        | 1388 |       0.28  | male     |
| L2 initial+field | personal          | 1390 |       0.473 | female   |
| L2 initial+field | personal          | 1387 |       0.465 | male     |
| L3 blind         | gap_parental_only | 1389 |       0.405 | nan      |
| L3 blind         | gap_travel        | 1390 |       0.388 | nan      |
| L3 blind         | parent            | 1390 |       0.354 | nan      |
| L3 blind         | parent_committed  | 1386 |       0.423 | nan      |
| L3 blind         | parent_gap        | 1386 |       0.295 | nan      |
| L3 blind         | personal          | 1390 |       0.463 | nan      |

## Gender preference by cue level (§8.1)

| source           | level            | stat                          |    value |    n |
|:-----------------|:-----------------|:------------------------------|---------:|-----:|
| E2 gender_none   | L0 name          | P(woman chosen)               |    0.515 | 1391 |
| E2 gender_none   | L0 name          | salary W-M ($, excl withheld) |  271     | 1382 |
| E2 gender_parent | L0 name          | P(woman chosen)               |    0.536 | 1386 |
| E2 gender_parent | L0 name          | salary W-M ($, excl withheld) |  491     | 1365 |
| E2 gender_none   | L1 name+field    | P(woman chosen)               |    0.54  | 1389 |
| E2 gender_none   | L1 name+field    | salary W-M ($, excl withheld) |  237     | 1378 |
| E2 gender_parent | L1 name+field    | P(woman chosen)               |    0.54  | 1391 |
| E2 gender_parent | L1 name+field    | salary W-M ($, excl withheld) |  449     | 1359 |
| E2 gender_none   | L2 initial+field | P(woman chosen)               |    0.538 | 1389 |
| E2 gender_none   | L2 initial+field | salary W-M ($, excl withheld) |  136     | 1379 |
| E2 gender_parent | L2 initial+field | P(woman chosen)               |    0.547 | 1391 |
| E2 gender_parent | L2 initial+field | salary W-M ($, excl withheld) |  577     | 1367 |
| E1 childless     | L0 name          | fit W-M                       |    0.16  |  780 |
| E1 childless     | L0 name          | salary W-M ($)                |  285     |  778 |
| E1 childless     | L1 name+field    | fit W-M                       |    0.08  | 1360 |
| E1 childless     | L1 name+field    | salary W-M ($)                | -191     | 1357 |
| E1 childless     | L2 initial+field | fit W-M                       |    0.08  | 1360 |
| E1 childless     | L2 initial+field | salary W-M ($)                |  425     | 1357 |

## Placebo decomposition (§8.3, E2)

| level            | group   |   parenthood (parent-personal) |   caregiving (gap_par-gap_travel) |   bundle (parent_gap-gap_par) |   se parent cell |
|:-----------------|:--------|-------------------------------:|----------------------------------:|------------------------------:|-----------------:|
| L0 name          | mothers |                         -0.107 |                             0.01  |                        -0.156 |            0.031 |
| L0 name          | fathers |                         -0.102 |                             0.024 |                        -0.166 |            0.033 |
| L0 name          | all     |                         -0.105 |                             0.017 |                        -0.161 |            0.031 |
| L1 name+field    | mothers |                         -0.115 |                             0.022 |                        -0.1   |            0.03  |
| L1 name+field    | fathers |                         -0.102 |                             0.027 |                        -0.099 |            0.031 |
| L1 name+field    | all     |                         -0.108 |                             0.024 |                        -0.1   |            0.03  |
| L2 initial+field | mothers |                         -0.106 |                             0.017 |                        -0.118 |            0.031 |
| L2 initial+field | fathers |                         -0.104 |                            -0.003 |                        -0.112 |            0.032 |
| L2 initial+field | all     |                         -0.105 |                             0.007 |                        -0.115 |            0.031 |
| L3 blind         | all     |                         -0.109 |                             0.017 |                        -0.11  |            0.03  |

## Mother vs father by outcome (§8.4, L0)

| contrast         | outcome          |   fathers |   mothers |      M-F |
|:-----------------|:-----------------|----------:|----------:|---------:|
| parent           | P(parent chosen) |     0.35  |     0.357 |    0.007 |
| parent           | commitment       |    -0.255 |    -0.225 |    0.03  |
| parent           | competence       |    -0.248 |    -0.231 |    0.017 |
| parent           | fit              |    -0.46  |    -0.464 |   -0.004 |
| parent           | likability       |    -0.368 |    -0.418 |   -0.05  |
| parent           | salary           | -1850.54  | -1649.67  |  200.868 |
| parent_committed | P(parent chosen) |     0.396 |     0.414 |    0.018 |
| parent_committed | commitment       |    -0.044 |    -0.049 |   -0.005 |
| parent_committed | competence       |    -0.125 |    -0.049 |    0.076 |
| parent_committed | fit              |    -0.275 |    -0.25  |    0.025 |
| parent_committed | likability       |    -0.264 |    -0.282 |   -0.018 |
| parent_committed | salary           | -1045.12  |  -630.541 |  414.578 |
| parent_gap       | P(parent chosen) |     0.244 |     0.238 |   -0.006 |
| parent_gap       | commitment       |    -0.972 |    -1.021 |   -0.049 |
| parent_gap       | competence       |    -0.335 |    -0.368 |   -0.033 |
| parent_gap       | fit              |    -0.879 |    -0.873 |    0.006 |
| parent_gap       | likability       |    -0.551 |    -0.63  |   -0.079 |
| parent_gap       | salary           | -2370.89  | -2530.37  | -159.482 |

## Abstention: salary withholding by cue level (E1 women, §8.6)

| family_code      |   initial_field |   name |   name_field |
|:-----------------|----------------:|-------:|-------------:|
| gap_travel       |           0.004 |  0.001 |        0.003 |
| married          |         nan     |  0     |      nan     |
| none             |           0.003 |  0.003 |        0.001 |
| parent           |           0.001 |  0.005 |        0.009 |
| parent_committed |         nan     |  0     |      nan     |
| parent_gap       |           0.013 |  0     |        0.004 |
| personal         |           0.004 |  0.001 |        0.004 |
| pregnant         |           0.012 |  0.013 |        0.007 |

## Drift anchors vs main run (§8.7)

| gender   | family   |   main P(interview) |   phase3 anchor |   delta |
|:---------|:---------|--------------------:|----------------:|--------:|
| female   | none     |               0.92  |           0.944 |   0.024 |
| female   | parent   |               0.931 |           0.956 |   0.025 |
| male     | none     |               0.909 |           0.944 |   0.035 |
| male     | parent   |               0.926 |           0.956 |   0.03  |

## Occupation-level regressions (§8.5, joint z-scores)

| dependent      | term           |   coef |    se |     p |   n |
|:---------------|:---------------|-------:|------:|------:|----:|
| p_parent_gap_F | z_female_share |  0.057 | 0.024 | 0.025 |  28 |
| p_parent_gap_F | z_median_wage  | -0.018 | 0.023 | 0.443 |  28 |
| p_parent_gap_F | z_physical     |  0.005 | 0.029 | 0.86  |  28 |
| p_parent_gap_F | z_care         | -0.029 | 0.021 | 0.185 |  28 |
| p_parent_gap_F | z_analytic     |  0.019 | 0.019 | 0.344 |  28 |
| p_parent_gap_F | z_manage       |  0.009 | 0.017 | 0.6   |  28 |
| p_parent_gap_M | z_female_share |  0.044 | 0.022 | 0.058 |  28 |
| p_parent_gap_M | z_median_wage  | -0.011 | 0.021 | 0.594 |  28 |
| p_parent_gap_M | z_physical     |  0.003 | 0.027 | 0.924 |  28 |
| p_parent_gap_M | z_care         | -0.025 | 0.019 | 0.203 |  28 |
| p_parent_gap_M | z_analytic     |  0.022 | 0.018 | 0.238 |  28 |
| p_parent_gap_M | z_manage       |  0.004 | 0.016 | 0.799 |  28 |
| parent_gap_MF  | z_female_share |  0.014 | 0.015 | 0.377 |  28 |
| parent_gap_MF  | z_median_wage  | -0.006 | 0.014 | 0.656 |  28 |
| parent_gap_MF  | z_physical     |  0.003 | 0.018 | 0.888 |  28 |
| parent_gap_MF  | z_care         | -0.004 | 0.013 | 0.794 |  28 |
| parent_gap_MF  | z_analytic     | -0.003 | 0.012 | 0.82  |  28 |
| parent_gap_MF  | z_manage       |  0.005 | 0.011 | 0.645 |  28 |
| p_woman_none   | z_female_share | -0.012 | 0.007 | 0.13  |  28 |
| p_woman_none   | z_median_wage  |  0.005 | 0.007 | 0.443 |  28 |
| p_woman_none   | z_physical     | -0.016 | 0.009 | 0.094 |  28 |
| p_woman_none   | z_care         |  0.007 | 0.007 | 0.284 |  28 |
| p_woman_none   | z_analytic     | -0.019 | 0.006 | 0.004 |  28 |
| p_woman_none   | z_manage       | -0.004 | 0.005 | 0.429 |  28 |