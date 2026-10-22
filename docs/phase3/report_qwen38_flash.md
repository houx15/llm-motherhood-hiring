# Phase-3 report — qwen38_flash

## Cue-level parent penalties (E2 P(parent chosen))

| level            | contrast          |    n |   P(parent) | gender   |
|:-----------------|:------------------|-----:|------------:|:---------|
| L0 name          | gap_parental_only | 1241 |       0.351 | female   |
| L0 name          | gap_parental_only | 1266 |       0.356 | male     |
| L0 name          | gap_travel        | 1247 |       0.277 | female   |
| L0 name          | gap_travel        | 1257 |       0.278 | male     |
| L0 name          | parent            |  780 |       0.362 | female   |
| L0 name          | parent            |  789 |       0.404 | male     |
| L0 name          | parent_committed  |  351 |       0.422 | female   |
| L0 name          | parent_committed  |  376 |       0.418 | male     |
| L0 name          | parent_gap        |  349 |       0.244 | female   |
| L0 name          | parent_gap        |  348 |       0.264 | male     |
| L0 name          | personal          | 1146 |       0.456 | female   |
| L0 name          | personal          | 1192 |       0.471 | male     |
| L1 name+field    | gap_parental_only | 1229 |       0.338 | female   |
| L1 name+field    | gap_parental_only | 1272 |       0.361 | male     |
| L1 name+field    | gap_travel        | 1240 |       0.279 | female   |
| L1 name+field    | gap_travel        | 1285 |       0.294 | male     |
| L1 name+field    | parent            | 1169 |       0.383 | female   |
| L1 name+field    | parent            | 1181 |       0.409 | male     |
| L1 name+field    | parent_committed  | 1149 |       0.419 | female   |
| L1 name+field    | parent_committed  | 1204 |       0.444 | male     |
| L1 name+field    | parent_gap        | 1121 |       0.227 | female   |
| L1 name+field    | parent_gap        | 1141 |       0.262 | male     |
| L1 name+field    | personal          | 1162 |       0.461 | female   |
| L1 name+field    | personal          | 1198 |       0.482 | male     |
| L2 initial+field | gap_parental_only | 1263 |       0.346 | female   |
| L2 initial+field | gap_parental_only | 1252 |       0.335 | male     |
| L2 initial+field | gap_travel        | 1248 |       0.28  | female   |
| L2 initial+field | gap_travel        | 1288 |       0.283 | male     |
| L2 initial+field | parent            | 1176 |       0.388 | female   |
| L2 initial+field | parent            | 1220 |       0.395 | male     |
| L2 initial+field | parent_committed  | 1174 |       0.417 | female   |
| L2 initial+field | parent_committed  | 1199 |       0.425 | male     |
| L2 initial+field | parent_gap        | 1121 |       0.204 | female   |
| L2 initial+field | parent_gap        | 1162 |       0.245 | male     |
| L2 initial+field | personal          | 1197 |       0.465 | female   |
| L2 initial+field | personal          | 1215 |       0.467 | male     |
| L3 blind         | gap_parental_only | 1257 |       0.332 | nan      |
| L3 blind         | gap_travel        | 1250 |       0.273 | nan      |
| L3 blind         | parent            | 1170 |       0.372 | nan      |
| L3 blind         | parent_committed  | 1180 |       0.397 | nan      |
| L3 blind         | parent_gap        | 1148 |       0.223 | nan      |
| L3 blind         | personal          | 1181 |       0.476 | nan      |

## Gender preference by cue level (§8.1)

| source           | level            | stat                          |     value |    n |
|:-----------------|:-----------------|:------------------------------|----------:|-----:|
| E2 gender_none   | L0 name          | P(woman chosen)               |     0.497 | 1287 |
| E2 gender_none   | L0 name          | salary W-M ($, excl withheld) |   -41     | 1282 |
| E2 gender_parent | L0 name          | P(woman chosen)               |     0.503 | 1291 |
| E2 gender_parent | L0 name          | salary W-M ($, excl withheld) |    38     | 1279 |
| E2 gender_none   | L1 name+field    | P(woman chosen)               |     0.492 | 1301 |
| E2 gender_none   | L1 name+field    | salary W-M ($, excl withheld) |  -143     | 1290 |
| E2 gender_parent | L1 name+field    | P(woman chosen)               |     0.514 | 1279 |
| E2 gender_parent | L1 name+field    | salary W-M ($, excl withheld) |    41     | 1253 |
| E2 gender_none   | L2 initial+field | P(woman chosen)               |     0.514 | 1279 |
| E2 gender_none   | L2 initial+field | salary W-M ($, excl withheld) |  -170     | 1264 |
| E2 gender_parent | L2 initial+field | P(woman chosen)               |     0.488 | 1265 |
| E2 gender_parent | L2 initial+field | salary W-M ($, excl withheld) |   -80     | 1240 |
| E1 childless     | L0 name          | fit W-M                       |     0.05  |  761 |
| E1 childless     | L0 name          | salary W-M ($)                | -1422     |  752 |
| E1 childless     | L1 name+field    | fit W-M                       |     0.03  | 1341 |
| E1 childless     | L1 name+field    | salary W-M ($)                |  -536     | 1317 |
| E1 childless     | L2 initial+field | fit W-M                       |     0.03  | 1343 |
| E1 childless     | L2 initial+field | salary W-M ($)                |   215     | 1320 |

## Placebo decomposition (§8.3, E2)

| level            | group   |   parenthood (parent-personal) |   caregiving (gap_par-gap_travel) |   bundle (parent_gap-gap_par) |   se parent cell |
|:-----------------|:--------|-------------------------------:|----------------------------------:|------------------------------:|-----------------:|
| L0 name          | mothers |                         -0.095 |                             0.074 |                        -0.108 |            0.038 |
| L0 name          | fathers |                         -0.066 |                             0.078 |                        -0.092 |            0.039 |
| L0 name          | all     |                         -0.081 |                             0.076 |                        -0.1   |            0.038 |
| L1 name+field    | mothers |                         -0.078 |                             0.059 |                        -0.11  |            0.039 |
| L1 name+field    | fathers |                         -0.073 |                             0.067 |                        -0.099 |            0.039 |
| L1 name+field    | all     |                         -0.075 |                             0.063 |                        -0.105 |            0.038 |
| L2 initial+field | mothers |                         -0.078 |                             0.066 |                        -0.142 |            0.039 |
| L2 initial+field | fathers |                         -0.072 |                             0.052 |                        -0.09  |            0.04  |
| L2 initial+field | all     |                         -0.075 |                             0.059 |                        -0.116 |            0.039 |
| L3 blind         | all     |                         -0.104 |                             0.059 |                        -0.109 |            0.037 |

## Mother vs father by outcome (§8.4, L0)

| contrast         | outcome          |   fathers |   mothers |      M-F |
|:-----------------|:-----------------|----------:|----------:|---------:|
| parent           | P(parent chosen) |     0.404 |     0.362 |   -0.042 |
| parent           | commitment       |    -1.053 |    -1.135 |   -0.082 |
| parent           | competence       |    -0.204 |    -0.224 |   -0.02  |
| parent           | fit              |    -0.52  |    -0.594 |   -0.074 |
| parent           | likability       |    -1.624 |    -1.688 |   -0.064 |
| parent           | salary           | -1466.32  | -1860.68  | -394.356 |
| parent_committed | P(parent chosen) |     0.418 |     0.422 |    0.004 |
| parent_committed | commitment       |    -0.596 |    -0.575 |    0.021 |
| parent_committed | competence       |    -0.178 |    -0.14  |    0.038 |
| parent_committed | fit              |    -0.468 |    -0.462 |    0.006 |
| parent_committed | likability       |    -1.471 |    -1.405 |    0.066 |
| parent_committed | salary           | -1222.83  | -1170.52  |   52.306 |
| parent_gap       | P(parent chosen) |     0.264 |     0.244 |   -0.02  |
| parent_gap       | commitment       |    -1.532 |    -1.645 |   -0.113 |
| parent_gap       | competence       |    -0.463 |    -0.527 |   -0.064 |
| parent_gap       | fit              |    -0.897 |    -0.98  |   -0.083 |
| parent_gap       | likability       |    -1.793 |    -1.897 |   -0.104 |
| parent_gap       | salary           | -1971.01  | -2498.53  | -527.52  |

## Abstention: salary withholding by cue level (E1 women, §8.6)

| family_code      |   initial_field |   name |   name_field |
|:-----------------|----------------:|-------:|-------------:|
| gap_travel       |           0.021 |  0.016 |        0.021 |
| married          |         nan     |  0     |      nan     |
| none             |           0.016 |  0.008 |        0.019 |
| parent           |           0.028 |  0.016 |        0.022 |
| parent_committed |         nan     |  0     |      nan     |
| parent_gap       |           0.024 |  0.005 |        0.023 |
| personal         |           0.013 |  0.016 |        0.018 |
| pregnant         |           0.029 |  0     |        0.026 |

## Drift anchors vs main run (§8.7)

| gender   | family   |   main P(interview) |   phase3 anchor |   delta |
|:---------|:---------|--------------------:|----------------:|--------:|
| female   | none     |               0.907 |           0.924 |   0.017 |
| female   | parent   |               0.914 |           0.925 |   0.011 |
| male     | none     |               0.899 |           0.912 |   0.013 |
| male     | parent   |               0.923 |           0.938 |   0.014 |

## Occupation-level regressions (§8.5, joint z-scores)

| dependent      | term           |   coef |    se |     p |   n |
|:---------------|:---------------|-------:|------:|------:|----:|
| p_parent_gap_F | z_female_share |  0.026 | 0.029 | 0.374 |  28 |
| p_parent_gap_F | z_median_wage  | -0.017 | 0.027 | 0.545 |  28 |
| p_parent_gap_F | z_physical     |  0.044 | 0.035 | 0.224 |  28 |
| p_parent_gap_F | z_care         |  0.007 | 0.026 | 0.783 |  28 |
| p_parent_gap_F | z_analytic     |  0.035 | 0.024 | 0.149 |  28 |
| p_parent_gap_F | z_manage       | -0.002 | 0.021 | 0.923 |  28 |
| p_parent_gap_M | z_female_share |  0.033 | 0.024 | 0.188 |  28 |
| p_parent_gap_M | z_median_wage  | -0.017 | 0.023 | 0.468 |  28 |
| p_parent_gap_M | z_physical     |  0.055 | 0.03  | 0.082 |  28 |
| p_parent_gap_M | z_care         |  0.009 | 0.022 | 0.687 |  28 |
| p_parent_gap_M | z_analytic     |  0.056 | 0.02  | 0.01  |  28 |
| p_parent_gap_M | z_manage       | -0.019 | 0.018 | 0.29  |  28 |
| parent_gap_MF  | z_female_share | -0.007 | 0.015 | 0.648 |  28 |
| parent_gap_MF  | z_median_wage  |  0     | 0.014 | 0.983 |  28 |
| parent_gap_MF  | z_physical     | -0.01  | 0.019 | 0.581 |  28 |
| parent_gap_MF  | z_care         | -0.002 | 0.013 | 0.899 |  28 |
| parent_gap_MF  | z_analytic     | -0.021 | 0.012 | 0.108 |  28 |
| parent_gap_MF  | z_manage       |  0.017 | 0.011 | 0.134 |  28 |
| p_woman_none   | z_female_share |  0.003 | 0.005 | 0.597 |  28 |
| p_woman_none   | z_median_wage  | -0.003 | 0.004 | 0.455 |  28 |
| p_woman_none   | z_physical     | -0.006 | 0.006 | 0.3   |  28 |
| p_woman_none   | z_care         |  0.005 | 0.004 | 0.206 |  28 |
| p_woman_none   | z_analytic     | -0.003 | 0.004 | 0.485 |  28 |
| p_woman_none   | z_manage       | -0.002 | 0.003 | 0.509 |  28 |