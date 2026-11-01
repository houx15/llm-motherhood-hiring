# R14: substring selection -> call-id membership (key stats, old vs new)

| key                             |     old |     new |   delta | flag   |
|:--------------------------------|--------:|--------:|--------:|:-------|
| noise deepseek parent obs_P     |   0.354 |   0.357 |   0.003 |        |
| amplif deepseek parent          |   7.6   |   7.6   |   0     |        |
| noise deepseek parent_gap obs_P |   0.319 |   0.31  |  -0.009 |        |
| amplif deepseek parent_gap      |   3.5   |   3.6   |   0.1   | FLAG   |
| noise haiku parent obs_P        |   0.262 |   0.233 |  -0.029 | FLAG   |
| amplif haiku parent             | nan     | nan     |         |        |
| noise haiku parent_gap obs_P    |   0.13  |   0.11  |  -0.02  | FLAG   |
| amplif haiku parent_gap         | nan     | nan     |         |        |
| noise luna parent obs_P         |   0.319 |   0.297 |  -0.022 | FLAG   |
| amplif luna parent              |  12.4   |  13.6   |   1.2   | FLAG   |
| noise luna parent_gap obs_P     |   0.204 |   0.186 |  -0.018 | FLAG   |
| amplif luna parent_gap          |   6.7   |   7     |   0.3   | FLAG   |
| noise qwen parent obs_P         |   0.381 |   0.387 |   0.006 |        |
| amplif qwen parent              |  38.2   |  34.2   |  -4     | FLAG   |
| noise qwen parent_gap obs_P     |   0.248 |   0.23  |  -0.018 | FLAG   |
| amplif qwen parent_gap          |  14.7   |  14.2   |  -0.5   | FLAG   |
| MF deepseek parent choice       |   0.006 |   0.008 |   0.002 |        |
| MF deepseek parent_gap choice   |   0.01  |   0.002 |  -0.008 |        |
| drift deepseek parent|F         |   0.023 |   0.023 |   0     |        |
| MF haiku parent choice          |  -0.037 |  -0.043 |  -0.006 |        |
| MF haiku parent_gap choice      |  -0.01  |  -0.02  |  -0.01  | FLAG   |
| drift haiku parent|F            |  -0.011 |   0.018 |   0.029 | FLAG   |
| MF luna parent choice           |  -0.003 |  -0.004 |  -0.001 |        |
| MF luna parent_gap choice       |  -0.005 |   0.002 |   0.007 |        |
| drift luna parent|F             |  -0.008 |   0.009 |   0.017 | FLAG   |
| MF qwen parent choice           |  -0.005 |  -0.011 |  -0.006 |        |
| MF qwen parent_gap choice       |   0.028 |  -0.026 |  -0.054 | FLAG   |
| drift qwen parent|F             |  -0.002 |  -0.014 |  -0.012 | FLAG   |
| decomp deepseek parenthood      |  -0.104 |  -0.104 |   0     |        |
| decomp deepseek label           |   0.017 |   0.017 |   0     |        |
| decomp deepseek bundle          |  -0.106 |  -0.107 |  -0.001 |        |
| decomp haiku parenthood         |  -0.192 |  -0.192 |   0     |        |
| decomp haiku label              |  -0.011 |  -0.011 |   0     |        |
| decomp haiku bundle             |  -0.174 |  -0.174 |   0     |        |
| decomp luna parenthood          |  -0.121 |  -0.121 |   0     |        |
| decomp luna label               |   0.065 |   0.065 |   0     |        |
| decomp luna bundle              |  -0.115 |  -0.115 |   0     |        |
| decomp qwen parenthood          |  -0.073 |  -0.08  |  -0.007 |        |
| decomp qwen label               |   0.067 |   0.066 |  -0.001 |        |
| decomp qwen bundle              |  -0.121 |  -0.123 |  -0.002 |        |
| e3v3 deepseek L0 ratio          |   0.639 |   0.639 |   0     |        |
| occ deepseek femshare           |   0.057 |   0.057 |   0     |        |
| e3v3 haiku L0 ratio             |   0.148 |   0.148 |   0     |        |
| occ haiku femshare              |   0.018 |   0.018 |   0     |        |
| e3v3 luna L0 ratio              |   0.695 |   0.695 |   0     |        |
| occ luna femshare               |   0.048 |   0.048 |   0     |        |
| e3v3 qwen L0 ratio              |   0.683 |   0.683 |   0     |        |
| occ qwen femshare               |   0.027 |   0.028 |   0.001 |        |

15 of 48 entries moved by >= .01.
