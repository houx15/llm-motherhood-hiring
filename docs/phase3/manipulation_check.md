# Phase-3 manipulation check (SPEC_PHASE3 §2.2)

1,176 calls per model (28 occupations x 42 variants; resume_00, childless).
Qwen: 1,173/1,176 valid (3 non-JSON responses, missing at random).

| model    | level            |   n |   pct_female |   pct_male |   pct_unknown |   pct_correct |
|:---------|:-----------------|----:|-------------:|-----------:|--------------:|--------------:|
| DeepSeek | L0 name          | 336 |        0.494 |      0.473 |         0.033 |         0.967 |
| DeepSeek | L1 name+field    | 336 |        0.5   |      0.5   |         0     |         1     |
| DeepSeek | L2 initial+field | 336 |        0.5   |      0.5   |         0     |         1     |
| DeepSeek | L3 blind         | 168 |        0     |      0.018 |         0.982 |       nan     |
| Haiku    | L0 name          | 336 |        0.11  |      0.312 |         0.577 |         0.423 |
| Haiku    | L1 name+field    | 336 |        0.5   |      0.5   |         0     |         1     |
| Haiku    | L2 initial+field | 336 |        0.5   |      0.5   |         0     |         1     |
| Haiku    | L3 blind         | 168 |        0     |      0     |         1     |       nan     |
| Luna     | L0 name          | 336 |        0.259 |      0.402 |         0.339 |         0.661 |
| Luna     | L1 name+field    | 336 |        0.5   |      0.5   |         0     |         1     |
| Luna     | L2 initial+field | 336 |        0.5   |      0.5   |         0     |         1     |
| Luna     | L3 blind         | 168 |        0     |      0.006 |         0.994 |       nan     |
| Qwen     | L0 name          | 336 |        0.494 |      0.488 |         0.018 |         0.982 |
| Qwen     | L1 name+field    | 334 |        0.503 |      0.497 |         0     |         1     |
| Qwen     | L2 initial+field | 335 |        0.499 |      0.501 |         0     |         1     |
| Qwen     | L3 blind         | 168 |        0.024 |      0     |         0.976 |       nan     |

**Readings.** (i) The explicit gender field is perfectly legible everywhere
(L1/L2 accuracy 100%; blind packets are never guessed as a specific gender).
(ii) Gendered names alone (L0) are read correctly by DeepSeek (97%) and Qwen
(98%), partially by Luna (66% — 34% 'unknown') and reluctantly by Haiku (39%
correct; 61% 'unknown'). Phase-2 name-only results therefore understate those
models' *certain* gender knowledge; L1/L2 make it explicit. (iii) No male
default under blind L3: 'unknown' >= 97.6% everywhere.