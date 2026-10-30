# CLAIMS.md — every registered number, its source, and its status

| id | section | rendered | source | expected | in report | matches | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abs_calls | abstract | `602,093 logged calls` | `docs/final/study_totals.json::grand_total.calls` | 616,419 | ✓ | | MISMATCH |
| abs_fit_max | abstract | `at most 0.35 points` | `docs/report/stats.json::models.*.e1_gaps_women.overall_fit.parent_gap_minus_none` | 0.35 | ✓ | | OK |
| abs_interview_max | abstract | `at most 1.5pp` | `docs/report/stats.json::models.*.e1_gaps_women.interview.parent_gap_minus_none` | 1.5 | ✓ | | OK |
| abs_share_min | abstract | `only 11–31% of the time` | `docs/report/stats.json::models.*.e2_clustered.cells.parent_gap|*.p` | 11 | ✓ | | OK |
| abs_share_max | abstract | `up to 77% of shortlist probability` | `docs/report/stats.json::models.*.e3_fe.*.adjusted_ratio` | 37% | ✓ | | MISMATCH |
| abs_amplification | abstract | `4× to 31×` | `docs/phase3/round6_stats.json::amplification.*.parent*.amplification_ratio` | 4× to 38× | ✓ | | MISMATCH |
| abs_haiku_fit | abstract | `*scores* parents higher (+0.34) yet chooses them 23% of the time` | `docs/report/stats.json::models.claude_haiku_55.e1_gaps_women.overall_fit.parent_minus_none` | +0.34 | ✓ | | OK |
| abs_haiku_choice | abstract | `chooses them 23% of the time` | `docs/report/stats.json::models.claude_haiku_55.e2_clustered.cells.parent|female.p` | 23% | ✓ | | OK |
| f2_interruption | extended summary, finding 2 | `costs 10.6–26.0pp` | `docs/phase3/round5_stats.json::primary_decomposition.*.cell_gap_travel.P` | 10.5–26.0pp | ✓ | | MISMATCH |
| f2_bundle | extended summary, finding 2 | `family bundle adds 10.5–17.6pp` | `docs/phase3/round5_stats.json::primary_decomposition.*.bundle.diff` | 10.6–17.4pp | ✓ | | MISMATCH |
| f2_parenthood | extended summary, finding 2 | `parenthood net of a disclosure placebo 6.8–19.2pp` | `docs/phase3/round5_stats.json::primary_decomposition.*.parenthood.diff` | 7.3–19.2pp | ✓ | | MISMATCH |
| f2_tost | extended summary, finding 2 | `7 of 8 model×cue` | `docs/phase3/round6_stats.json::equivalence.*` | 7 of 8 | ✓ | | OK |
| f5_withhold_main | finding 5 | `19.8% of pregnant applicants` | `docs/report/stats.json::models.claude_haiku_55.withheld.rates.female|pregnant` | 19.9% | ✓ | | MISMATCH |
| f5_interview_gap | finding 5 | `a −9.4pp interview penalty` | `docs/report/stats.json::models.claude_haiku_55.pregnancy_full.interview.t` | −9.4pp | ✓ | | OK |
| p4_haiku_gap_none | §4.10 | `**.074` | `docs/phase4/phase4_stats.json::levels_women.haiku.parent_gap|sp_none` | .074 | ✓ | | OK |
| p4_haiku_gap_fair | §4.10 | `.195` | `docs/phase4/phase4_stats.json::levels_women.haiku.parent_gap|sp_fair` | .195 | ✓ | | OK |
| p4_qwen_gap_fair | §4.10 | `.181` | `docs/phase4/phase4_stats.json::levels_women.qwen.parent_gap|sp_fair` | .181 | ✓ | | OK |
| p4_ds_gap_gap_arm | §4.10 | `.386` | `docs/phase4/phase4_stats.json::levels_women.deepseek.parent_gap|sp_gap` | .386 | ✓ | | OK |
| p4_luna_direct_none | §4.10 (H-B2) | `replicates (.640` | `docs/phase4/phase4_stats.json::hb2.luna.gender_parent|sp_none.p_woman` | .640 | ✓ | | OK |
| p4_luna_direct_fair | §4.10 (H-B2) | `falls to .557` | `docs/phase4/phase4_stats.json::hb2.luna.gender_parent|sp_fair.p_woman` | .557 | ✓ | | OK |
| p4_sp_gap_range | §4.10 (H-B3) | `cuts the interruption penalty by 4–14pp` | `docs/phase4/phase4_stats.json::hb1_hb3.*.parent_gap|*|sp_gap.mean` | 4–14pp | ✓ | | OK |
| di_haiku_cross | §4.11 | `exceeds **31%**` | `docs/final/disparate_impact_stats.json::Haiku.crossing_womens_prevalence` | 59% | ✓ | | MISMATCH |
| di_scenario_low | §4.11 | `.88–.96` | `docs/final/disparate_impact_stats.json::*.scenario_20_5` | .94–.94 | ✓ | | MISMATCH |

**14/23 claims verified.**

## Mismatches (for Part 2; report.md NOT edited)
- `abs_calls`: rendered `602,093 logged calls` (present; source says 616,419)
- `abs_share_max`: rendered `up to 77% of shortlist probability` (present; source says 37%)
- `abs_amplification`: rendered `4× to 31×` (present; source says 4× to 38×)
- `f2_interruption`: rendered `costs 10.6–26.0pp` (present; source says 10.5–26.0pp)
- `f2_bundle`: rendered `family bundle adds 10.5–17.6pp` (present; source says 10.6–17.4pp)
- `f2_parenthood`: rendered `parenthood net of a disclosure placebo 6.8–19.2pp` (present; source says 7.3–19.2pp)
- `f5_withhold_main`: rendered `19.8% of pregnant applicants` (present; source says 19.9%)
- `di_haiku_cross`: rendered `exceeds **31%**` (present; source says 59%)
- `di_scenario_low`: rendered `.88–.96` (present; source says .94–.94)
