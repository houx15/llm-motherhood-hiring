# Phase-3 report — claude_haiku_55

## Cue-level parent penalties (E2 P(parent chosen))

| level            | contrast          |    n |   P(parent) | gender   |
|:-----------------|:------------------|-----:|------------:|:---------|
| L0 name          | gap_parental_only | 1343 |       0.31  | female   |
| L0 name          | gap_parental_only | 1344 |       0.327 | male     |
| L0 name          | gap_travel        | 1343 |       0.298 | female   |
| L0 name          | gap_travel        | 1343 |       0.313 | male     |
| L0 name          | parent            |  874 |       0.253 | female   |
| L0 name          | parent            |  883 |       0.297 | male     |
| L0 name          | parent_committed  |  404 |       0.314 | female   |
| L0 name          | parent_committed  |  406 |       0.352 | male     |
| L0 name          | parent_gap        |  400 |       0.072 | female   |
| L0 name          | parent_gap        |  400 |       0.1   | male     |
| L0 name          | personal          | 1344 |       0.522 | female   |
| L0 name          | personal          | 1344 |       0.539 | male     |
| L1 name+field    | gap_parental_only | 1338 |       0.298 | female   |
| L1 name+field    | gap_parental_only | 1343 |       0.301 | male     |
| L1 name+field    | gap_travel        | 1341 |       0.313 | female   |
| L1 name+field    | gap_travel        | 1344 |       0.318 | male     |
| L1 name+field    | parent            | 1291 |       0.307 | female   |
| L1 name+field    | parent            | 1298 |       0.363 | male     |
| L1 name+field    | parent_committed  | 1281 |       0.357 | female   |
| L1 name+field    | parent_committed  | 1294 |       0.413 | male     |
| L1 name+field    | parent_gap        | 1248 |       0.111 | female   |
| L1 name+field    | parent_gap        | 1284 |       0.132 | male     |
| L1 name+field    | personal          | 1339 |       0.506 | female   |
| L1 name+field    | personal          | 1344 |       0.534 | male     |
| L2 initial+field | gap_parental_only | 1339 |       0.317 | female   |
| L2 initial+field | gap_parental_only | 1342 |       0.324 | male     |
| L2 initial+field | gap_travel        | 1343 |       0.319 | female   |
| L2 initial+field | gap_travel        | 1341 |       0.313 | male     |
| L2 initial+field | parent            | 1287 |       0.35  | female   |
| L2 initial+field | parent            | 1292 |       0.381 | male     |
| L2 initial+field | parent_committed  | 1266 |       0.419 | female   |
| L2 initial+field | parent_committed  | 1291 |       0.438 | male     |
| L2 initial+field | parent_gap        | 1251 |       0.137 | female   |
| L2 initial+field | parent_gap        | 1260 |       0.145 | male     |
| L2 initial+field | personal          | 1341 |       0.549 | female   |
| L2 initial+field | personal          | 1341 |       0.548 | male     |
| L3 blind         | gap_parental_only | 1343 |       0.327 | nan      |
| L3 blind         | gap_travel        | 1343 |       0.32  | nan      |
| L3 blind         | parent            | 1336 |       0.281 | nan      |
| L3 blind         | parent_committed  | 1332 |       0.321 | nan      |
| L3 blind         | parent_gap        | 1321 |       0.112 | nan      |
| L3 blind         | personal          | 1344 |       0.521 | nan      |

## Gender preference by cue level (§8.1)

| source           | level            | stat                          |    value |    n |
|:-----------------|:-----------------|:------------------------------|---------:|-----:|
| E2 gender_none   | L0 name          | P(woman chosen)               |    0.528 | 1344 |
| E2 gender_none   | L0 name          | salary W-M ($, excl withheld) |  -64     | 1255 |
| E2 gender_parent | L0 name          | P(woman chosen)               |    0.544 | 1326 |
| E2 gender_parent | L0 name          | salary W-M ($, excl withheld) |    7     | 1143 |
| E2 gender_none   | L1 name+field    | P(woman chosen)               |    0.526 | 1342 |
| E2 gender_none   | L1 name+field    | salary W-M ($, excl withheld) | -299     | 1048 |
| E2 gender_parent | L1 name+field    | P(woman chosen)               |    0.498 | 1266 |
| E2 gender_parent | L1 name+field    | salary W-M ($, excl withheld) | -502     |  910 |
| E2 gender_none   | L2 initial+field | P(woman chosen)               |    0.513 | 1333 |
| E2 gender_none   | L2 initial+field | salary W-M ($, excl withheld) | -587     |  839 |
| E2 gender_parent | L2 initial+field | P(woman chosen)               |    0.47  | 1220 |
| E2 gender_parent | L2 initial+field | salary W-M ($, excl withheld) | -867     |  756 |
| E1 childless     | L0 name          | fit W-M                       |    0.09  |  764 |
| E1 childless     | L0 name          | salary W-M ($)                |  375     |  762 |
| E1 childless     | L1 name+field    | fit W-M                       |    0.13  | 1344 |
| E1 childless     | L1 name+field    | salary W-M ($)                |  -16     | 1340 |
| E1 childless     | L2 initial+field | fit W-M                       |    0.06  | 1344 |
| E1 childless     | L2 initial+field | salary W-M ($)                | -647     | 1340 |

## Placebo decomposition (§8.3, E2)

| level            | group   |   parenthood (parent-personal) |   caregiving (gap_par-gap_travel) |   bundle (parent_gap-gap_par) |   se parent cell |
|:-----------------|:--------|-------------------------------:|----------------------------------:|------------------------------:|-----------------:|
| L0 name          | mothers |                         -0.269 |                             0.013 |                        -0.238 |            0.029 |
| L0 name          | fathers |                         -0.242 |                             0.015 |                        -0.227 |            0.028 |
| L0 name          | all     |                         -0.256 |                             0.014 |                        -0.233 |            0.028 |
| L1 name+field    | mothers |                         -0.199 |                            -0.015 |                        -0.188 |            0.032 |
| L1 name+field    | fathers |                         -0.171 |                            -0.017 |                        -0.168 |            0.033 |
| L1 name+field    | all     |                         -0.185 |                            -0.016 |                        -0.178 |            0.032 |
| L2 initial+field | mothers |                         -0.198 |                            -0.001 |                        -0.181 |            0.032 |
| L2 initial+field | fathers |                         -0.167 |                             0.011 |                        -0.179 |            0.032 |
| L2 initial+field | all     |                         -0.183 |                             0.005 |                        -0.18  |            0.032 |
| L3 blind         | all     |                         -0.24  |                             0.007 |                        -0.215 |            0.029 |

## Mother vs father by outcome (§8.4, L0)

| contrast         | outcome          |   fathers |   mothers |      M-F |
|:-----------------|:-----------------|----------:|----------:|---------:|
| parent           | P(parent chosen) |     0.297 |     0.253 |   -0.044 |
| parent           | commitment       |    -0.165 |    -0.294 |   -0.129 |
| parent           | competence       |    -0.112 |    -0.132 |   -0.02  |
| parent           | fit              |    -0.441 |    -0.518 |   -0.077 |
| parent           | likability       |    -0.071 |    -0.118 |   -0.047 |
| parent           | salary           | -1060.52  | -1273.35  | -212.835 |
| parent_committed | P(parent chosen) |     0.352 |     0.314 |   -0.038 |
| parent_committed | commitment       |     0.084 |    -0.062 |   -0.146 |
| parent_committed | competence       |    -0.022 |    -0.069 |   -0.047 |
| parent_committed | fit              |    -0.273 |    -0.453 |   -0.18  |
| parent_committed | likability       |    -0.017 |    -0.094 |   -0.077 |
| parent_committed | salary           |  -577.67  | -1075.76  | -498.088 |
| parent_gap       | P(parent chosen) |     0.1   |     0.072 |   -0.028 |
| parent_gap       | commitment       |    -0.993 |    -1.135 |   -0.142 |
| parent_gap       | competence       |    -0.133 |    -0.17  |   -0.037 |
| parent_gap       | fit              |    -0.835 |    -0.993 |   -0.158 |
| parent_gap       | likability       |    -0.135 |    -0.16  |   -0.025 |
| parent_gap       | salary           | -1407.56  | -1850.68  | -443.116 |

## Abstention: salary withholding by cue level (E1 women, §8.6)

| family_code      |   initial_field |   name |   name_field |
|:-----------------|----------------:|-------:|-------------:|
| gap_travel       |           0.004 |  0.001 |        0.001 |
| married          |         nan     |  0.1   |      nan     |
| none             |           0.003 |  0.003 |        0.003 |
| parent           |           0.009 |  0.005 |        0.006 |
| parent_committed |         nan     |  0     |      nan     |
| parent_gap       |           0.018 |  0     |        0.016 |
| personal         |           0.004 |  0.004 |        0.007 |
| pregnant         |           0.257 |  0.182 |        0.275 |

## Drift anchors vs main run (§8.7)

| gender   | family   |   main P(interview) |   phase3 anchor |   delta |
|:---------|:---------|--------------------:|----------------:|--------:|
| female   | none     |               0.955 |           0.988 |   0.033 |
| female   | parent   |               0.967 |           0.988 |   0.021 |
| male     | none     |               0.957 |           0.981 |   0.025 |
| male     | parent   |               0.959 |           0.981 |   0.022 |

## Occupation-level regressions (§8.5, joint z-scores)

| dependent      | term           |   coef |    se |     p |   n |
|:---------------|:---------------|-------:|------:|------:|----:|
| p_parent_gap_F | z_female_share |  0.018 | 0.025 | 0.467 |  28 |
| p_parent_gap_F | z_median_wage  | -0.006 | 0.023 | 0.789 |  28 |
| p_parent_gap_F | z_physical     |  0.007 | 0.03  | 0.82  |  28 |
| p_parent_gap_F | z_care         | -0.027 | 0.022 | 0.233 |  28 |
| p_parent_gap_F | z_analytic     |  0.041 | 0.02  | 0.053 |  28 |
| p_parent_gap_F | z_manage       | -0.001 | 0.018 | 0.972 |  28 |
| p_parent_gap_M | z_female_share |  0.026 | 0.025 | 0.318 |  28 |
| p_parent_gap_M | z_median_wage  | -0.017 | 0.024 | 0.483 |  28 |
| p_parent_gap_M | z_physical     |  0.007 | 0.031 | 0.822 |  28 |
| p_parent_gap_M | z_care         | -0.018 | 0.022 | 0.424 |  28 |
| p_parent_gap_M | z_analytic     |  0.038 | 0.021 | 0.081 |  28 |
| p_parent_gap_M | z_manage       | -0     | 0.019 | 0.982 |  28 |
| parent_gap_MF  | z_female_share | -0.008 | 0.008 | 0.345 |  28 |
| parent_gap_MF  | z_median_wage  |  0.011 | 0.008 | 0.168 |  28 |
| parent_gap_MF  | z_physical     | -0     | 0.01  | 0.988 |  28 |
| parent_gap_MF  | z_care         | -0.008 | 0.007 | 0.252 |  28 |
| parent_gap_MF  | z_analytic     |  0.003 | 0.007 | 0.647 |  28 |
| parent_gap_MF  | z_manage       | -0     | 0.006 | 0.971 |  28 |
| p_woman_none   | z_female_share |  0.01  | 0.014 | 0.491 |  28 |
| p_woman_none   | z_median_wage  | -0.016 | 0.014 | 0.244 |  28 |
| p_woman_none   | z_physical     | -0.025 | 0.018 | 0.177 |  28 |
| p_woman_none   | z_care         |  0.013 | 0.013 | 0.316 |  28 |
| p_woman_none   | z_analytic     | -0     | 0.012 | 0.972 |  28 |
| p_woman_none   | z_manage       | -0.014 | 0.01  | 0.193 |  28 |