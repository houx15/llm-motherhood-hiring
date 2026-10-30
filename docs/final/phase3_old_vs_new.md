# Phase-3 stats: old (fea0faf) vs new (repair-exclusion + e3 model_key fix)

| stat                                  |    old |    new |   delta |
|:--------------------------------------|-------:|-------:|--------:|
| decomposition deepseek parenthood     | -0.104 | -0.104 |   0     |
| decomposition deepseek label          |  0.017 |  0.017 |   0     |
| decomposition deepseek bundle         | -0.105 | -0.106 |  -0.001 |
| decomposition haiku parenthood        | -0.192 | -0.192 |   0     |
| decomposition haiku label             | -0.011 | -0.011 |   0     |
| decomposition haiku bundle            | -0.174 | -0.174 |   0     |
| decomposition luna parenthood         | -0.121 | -0.121 |   0     |
| decomposition luna label              |  0.065 |  0.065 |   0     |
| decomposition luna bundle             | -0.115 | -0.115 |   0     |
| decomposition qwen parenthood         | -0.068 | -0.073 |  -0.005 |
| decomposition qwen label              |  0.067 |  0.067 |   0     |
| decomposition qwen bundle             | -0.122 | -0.121 |   0.001 |
| e3v3 deepseek name                    |  0.639 |  0.639 |   0     |
| e3v3 deepseek blind                   |  0.65  |  0.653 |   0.003 |
| e3v3 haiku name                       |  0.148 |  0.148 |   0     |
| e3v3 haiku blind                      |  0.16  |  0.16  |   0     |
| e3v3 luna name                        |  0.695 |  0.695 |   0     |
| e3v3 luna blind                       |  0.705 |  0.705 |   0     |
| e3v3 qwen name                        |  0.681 |  0.683 |   0.002 |
| e3v3 qwen blind                       |  0.705 |  0.705 |   0     |
| direct luna gender_parent@name_field  |  0.646 |  0.647 |   0.001 |
| direct luna gender_none@name          |  0.522 |  0.522 |   0     |
| direct haiku gender_parent@name_field |  0.498 |  0.498 |   0     |
| direct haiku gender_none@name         |  0.528 |  0.528 |   0     |
| invariance haiku parent L1-L0         |  0.074 |  0.074 |   0     |
| invariance luna parent L1-L0          |  0.034 |  0.034 |   0     |

0/26 entries moved by >= .01; max |delta| = 0.005.
