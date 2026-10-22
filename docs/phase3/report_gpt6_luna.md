# Phase-3 report — gpt6_luna

## Cue-level parent penalties (E2 P(parent chosen))

| level            | contrast          |    n |   P(parent) | gender   |
|:-----------------|:------------------|-----:|------------:|:---------|
| L0 name          | gap_parental_only | 1343 |       0.27  | female   |
| L0 name          | gap_parental_only | 1343 |       0.271 | male     |
| L0 name          | gap_travel        | 1344 |       0.229 | female   |
| L0 name          | gap_travel        | 1342 |       0.227 | male     |
| L0 name          | parent            |  888 |       0.33  | female   |
| L0 name          | parent            |  888 |       0.327 | male     |
| L0 name          | parent_committed  |  408 |       0.255 | female   |
| L0 name          | parent_committed  |  408 |       0.26  | male     |
| L0 name          | parent_gap        |  408 |       0.093 | female   |
| L0 name          | parent_gap        |  407 |       0.098 | male     |
| L0 name          | personal          | 1343 |       0.454 | female   |
| L0 name          | personal          | 1344 |       0.464 | male     |
| L1 name+field    | gap_parental_only | 1344 |       0.289 | female   |
| L1 name+field    | gap_parental_only | 1344 |       0.29  | male     |
| L1 name+field    | gap_travel        | 1344 |       0.219 | female   |
| L1 name+field    | gap_travel        | 1343 |       0.226 | male     |
| L1 name+field    | parent            | 1343 |       0.352 | female   |
| L1 name+field    | parent            | 1344 |       0.352 | male     |
| L1 name+field    | parent_committed  | 1340 |       0.292 | female   |
| L1 name+field    | parent_committed  | 1341 |       0.277 | male     |
| L1 name+field    | parent_gap        | 1343 |       0.171 | female   |
| L1 name+field    | parent_gap        | 1341 |       0.169 | male     |
| L1 name+field    | personal          | 1343 |       0.465 | female   |
| L1 name+field    | personal          | 1344 |       0.467 | male     |
| L2 initial+field | gap_parental_only | 1344 |       0.279 | female   |
| L2 initial+field | gap_parental_only | 1342 |       0.292 | male     |
| L2 initial+field | gap_travel        | 1342 |       0.227 | female   |
| L2 initial+field | gap_travel        | 1342 |       0.227 | male     |
| L2 initial+field | parent            | 1341 |       0.358 | female   |
| L2 initial+field | parent            | 1342 |       0.359 | male     |
| L2 initial+field | parent_committed  | 1342 |       0.296 | female   |
| L2 initial+field | parent_committed  | 1341 |       0.291 | male     |
| L2 initial+field | parent_gap        | 1342 |       0.148 | female   |
| L2 initial+field | parent_gap        | 1343 |       0.161 | male     |
| L2 initial+field | personal          | 1344 |       0.466 | female   |
| L2 initial+field | personal          | 1342 |       0.463 | male     |
| L3 blind         | gap_parental_only | 1340 |       0.269 | nan      |
| L3 blind         | gap_travel        | 1344 |       0.226 | nan      |
| L3 blind         | parent            | 1343 |       0.326 | nan      |
| L3 blind         | parent_committed  | 1338 |       0.275 | nan      |
| L3 blind         | parent_gap        | 1344 |       0.163 | nan      |
| L3 blind         | personal          | 1344 |       0.456 | nan      |

## Gender preference by cue level (§8.1)

| source           | level            | stat                          |    value |    n |
|:-----------------|:-----------------|:------------------------------|---------:|-----:|
| E2 gender_none   | L0 name          | P(woman chosen)               |    0.522 | 1344 |
| E2 gender_none   | L0 name          | salary W-M ($, excl withheld) |  128     | 1298 |
| E2 gender_parent | L0 name          | P(woman chosen)               |    0.578 | 1343 |
| E2 gender_parent | L0 name          | salary W-M ($, excl withheld) |  497     | 1193 |
| E2 gender_none   | L1 name+field    | P(woman chosen)               |    0.587 | 1343 |
| E2 gender_none   | L1 name+field    | salary W-M ($, excl withheld) |  520     | 1234 |
| E2 gender_parent | L1 name+field    | P(woman chosen)               |    0.647 | 1341 |
| E2 gender_parent | L1 name+field    | salary W-M ($, excl withheld) | 1045     | 1102 |
| E2 gender_none   | L2 initial+field | P(woman chosen)               |    0.575 | 1343 |
| E2 gender_none   | L2 initial+field | salary W-M ($, excl withheld) |  284     | 1202 |
| E2 gender_parent | L2 initial+field | P(woman chosen)               |    0.634 | 1343 |
| E2 gender_parent | L2 initial+field | salary W-M ($, excl withheld) | 1020     | 1040 |
| E1 childless     | L0 name          | fit W-M                       |    0.06  |  764 |
| E1 childless     | L0 name          | salary W-M ($)                |  520     |  764 |
| E1 childless     | L1 name+field    | fit W-M                       |    0.13  | 1344 |
| E1 childless     | L1 name+field    | salary W-M ($)                |  -53     | 1343 |
| E1 childless     | L2 initial+field | fit W-M                       |    0.1   | 1344 |
| E1 childless     | L2 initial+field | salary W-M ($)                |  -17     | 1343 |

## Placebo decomposition (§8.3, E2)

| level            | group   |   parenthood (parent-personal) |   caregiving (gap_par-gap_travel) |   bundle (parent_gap-gap_par) |   se parent cell |
|:-----------------|:--------|-------------------------------:|----------------------------------:|------------------------------:|-----------------:|
| L0 name          | mothers |                         -0.124 |                             0.041 |                        -0.177 |            0.036 |
| L0 name          | fathers |                         -0.137 |                             0.045 |                        -0.173 |            0.037 |
| L0 name          | all     |                         -0.131 |                             0.043 |                        -0.175 |            0.036 |
| L1 name+field    | mothers |                         -0.113 |                             0.069 |                        -0.117 |            0.037 |
| L1 name+field    | fathers |                         -0.115 |                             0.064 |                        -0.121 |            0.038 |
| L1 name+field    | all     |                         -0.114 |                             0.067 |                        -0.119 |            0.037 |
| L2 initial+field | mothers |                         -0.108 |                             0.052 |                        -0.131 |            0.038 |
| L2 initial+field | fathers |                         -0.104 |                             0.066 |                        -0.131 |            0.038 |
| L2 initial+field | all     |                         -0.106 |                             0.059 |                        -0.131 |            0.037 |
| L3 blind         | all     |                         -0.13  |                             0.043 |                        -0.106 |            0.037 |

## Mother vs father by outcome (§8.4, L0)

| contrast         | outcome          |   fathers |   mothers |     M-F |
|:-----------------|:-----------------|----------:|----------:|--------:|
| parent           | P(parent chosen) |     0.327 |     0.33  |   0.003 |
| parent           | commitment       |    -0.468 |    -0.455 |   0.013 |
| parent           | competence       |    -0.168 |    -0.145 |   0.023 |
| parent           | fit              |    -0.329 |    -0.31  |   0.019 |
| parent           | likability       |    -0.848 |    -0.771 |   0.077 |
| parent           | salary           | -1222.91  | -1186.05  |  36.867 |
| parent_committed | P(parent chosen) |     0.26  |     0.255 |  -0.005 |
| parent_committed | commitment       |    -0.311 |    -0.309 |   0.002 |
| parent_committed | competence       |    -0.235 |    -0.228 |   0.007 |
| parent_committed | fit              |    -0.488 |    -0.453 |   0.035 |
| parent_committed | likability       |    -0.828 |    -0.782 |   0.046 |
| parent_committed | salary           | -1509.54  | -1341.88  | 167.657 |
| parent_gap       | P(parent chosen) |     0.098 |     0.093 |  -0.005 |
| parent_gap       | commitment       |    -0.759 |    -0.718 |   0.041 |
| parent_gap       | competence       |    -0.479 |    -0.417 |   0.062 |
| parent_gap       | fit              |    -0.862 |    -0.843 |   0.019 |
| parent_gap       | likability       |    -0.919 |    -0.904 |   0.015 |
| parent_gap       | salary           | -2760     | -2765.67  |  -5.668 |

## Abstention: salary withholding by cue level (E1 women, §8.6)

| family_code      |   initial_field |   name |   name_field |
|:-----------------|----------------:|-------:|-------------:|
| gap_travel       |           0     |  0.001 |        0     |
| married          |         nan     |  0     |      nan     |
| none             |           0.001 |  0     |        0.001 |
| parent           |           0     |  0     |        0.003 |
| parent_committed |         nan     |  0     |      nan     |
| parent_gap       |           0.001 |  0     |        0.001 |
| personal         |           0.001 |  0.001 |        0.001 |
| pregnant         |           0.004 |  0     |        0.003 |

## Drift anchors vs main run (§8.7)

| gender   | family   |   main P(interview) |   phase3 anchor |   delta |
|:---------|:---------|--------------------:|----------------:|--------:|
| female   | none     |               0.915 |           0.944 |   0.029 |
| female   | parent   |               0.918 |           0.95  |   0.032 |
| male     | none     |               0.913 |           0.944 |   0.03  |
| male     | parent   |               0.913 |           0.944 |   0.03  |

## Occupation-level regressions (§8.5, joint z-scores)

| dependent      | term           |   coef |    se |     p |   n |
|:---------------|:---------------|-------:|------:|------:|----:|
| p_parent_gap_F | z_female_share |  0.047 | 0.032 | 0.149 |  28 |
| p_parent_gap_F | z_median_wage  | -0.021 | 0.03  | 0.492 |  28 |
| p_parent_gap_F | z_physical     | -0.004 | 0.038 | 0.919 |  28 |
| p_parent_gap_F | z_care         | -0.058 | 0.028 | 0.05  |  28 |
| p_parent_gap_F | z_analytic     |  0.031 | 0.026 | 0.247 |  28 |
| p_parent_gap_F | z_manage       |  0.012 | 0.023 | 0.601 |  28 |
| p_parent_gap_M | z_female_share |  0.047 | 0.034 | 0.178 |  28 |
| p_parent_gap_M | z_median_wage  | -0.016 | 0.032 | 0.62  |  28 |
| p_parent_gap_M | z_physical     | -0.007 | 0.041 | 0.872 |  28 |
| p_parent_gap_M | z_care         | -0.044 | 0.03  | 0.155 |  28 |
| p_parent_gap_M | z_analytic     |  0.033 | 0.028 | 0.248 |  28 |
| p_parent_gap_M | z_manage       |  0.019 | 0.025 | 0.445 |  28 |
| parent_gap_MF  | z_female_share |  0     | 0.011 | 0.992 |  28 |
| parent_gap_MF  | z_median_wage  | -0.005 | 0.01  | 0.65  |  28 |
| parent_gap_MF  | z_physical     |  0.003 | 0.013 | 0.838 |  28 |
| parent_gap_MF  | z_care         | -0.014 | 0.01  | 0.164 |  28 |
| parent_gap_MF  | z_analytic     | -0.002 | 0.009 | 0.812 |  28 |
| parent_gap_MF  | z_manage       | -0.007 | 0.008 | 0.39  |  28 |
| p_woman_none   | z_female_share | -0.004 | 0.015 | 0.779 |  28 |
| p_woman_none   | z_median_wage  |  0.03  | 0.015 | 0.052 |  28 |
| p_woman_none   | z_physical     |  0.016 | 0.019 | 0.416 |  28 |
| p_woman_none   | z_care         | -0.009 | 0.014 | 0.537 |  28 |
| p_woman_none   | z_analytic     | -0.021 | 0.013 | 0.106 |  28 |
| p_woman_none   | z_manage       | -0.006 | 0.011 | 0.606 |  28 |