# CLAIMS.md — every registered number, its source, and its status

| id | section | rendered | source | expected | in report | matches | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abs_calls | abstract | `616,419` | `docs/final/study_totals.json::grand_total.calls_excl_coding` | 616,419 | ✓ | | OK |
| abs_amplification | abstract | `3.5–38×` | `docs/phase3/round6_stats.json::amplification.*.parent*.amplification_ratio` | 3.5–38× | ✓ | | OK |
| abs_share_max | abstract | `up to 77% of shortlist probability` | `docs/report/stats.json::models.*.e3_fe.*.adjusted_ratio` | 77% | ✓ | | OK |
| abs_haiku_fit | abstract | `scoring parents *higher* yet choosing them 23% of the time` | `docs/report/stats.json::models.claude_haiku_55.e1_gaps_women.overall_fit.parent_minus_none` | None | ✓ | | OK |
| abs_haiku_choice | abstract | `scoring parents *higher* yet choosing them 23% of the time` | `docs/report/stats.json::models.claude_haiku_55.e2_clustered.cells.parent|female.p` | 23% | ✓ | | OK |
| f2_interruption | §4.2 | `costs 10.5–26.0pp` | `docs/phase3/round5_stats.json::primary_decomposition.*.cell_gap_travel.P` | 10.5–26.0pp | ✓ | | OK |
| f2_bundle | §4.2 | `adds a further 10.6–17.4pp` | `docs/phase3/round5_stats.json::primary_decomposition.*.bundle.diff` | 10.6–17.4pp | ✓ | | OK |
| f2_parenthood | §4.2 | `7.3–19.2` | `docs/phase3/round5_stats.json::primary_decomposition.*.parenthood.diff` | 7.3–19.2 | ✓ | | OK |
| f2_personal | §4.2 | `costs 2.9–3.5pp in DeepSeek, Luna, and Qwen` | `docs/phase3/round5_stats.json::primary_decomposition.*.cell_personal.P` | 2.9–3.5pp | ✓ | | OK |
| f2_personal_haiku | §4.2 | `raises Haiku's choice share by 3.7pp` | `docs/phase3/round5_stats.json::primary_decomposition.haiku.cell_personal.P` | 3.7pp | ✓ | | OK |
| f2_tost | §4.2 | `7 of 8 model×cue` | `docs/phase3/round6_stats.json::equivalence.*` | 7 of 8 | ✓ | | OK |
| dec_int_ds | §4.2 table | `−10.5pp (t −8.0)` | `docs/phase3/round5_stats.json::primary_decomposition.deepseek.cell_gap_travel` | −10.5pp (t −8.0) | ✓ | | OK |
| dec_int_haiku | §4.2 table | `−18.4pp (t −8.5)` | `docs/phase3/round5_stats.json::primary_decomposition.haiku.cell_gap_travel` | −18.4pp (t −8.5) | ✓ | | OK |
| dec_int_luna | §4.2 table | `−26.0pp (t −7.3)` | `docs/phase3/round5_stats.json::primary_decomposition.luna.cell_gap_travel` | −26.0pp (t −7.3) | ✓ | | OK |
| dec_int_qwen | §4.2 table | `−22.4pp (t −8.9)` | `docs/phase3/round5_stats.json::primary_decomposition.qwen.cell_gap_travel` | −22.4pp (t −8.9) | ✓ | | OK |
| dec_par_ds | §4.2 table | `−10.4pp [−12.8, −8.0] (t −8.5)` | `docs/phase3/round5_stats.json::primary_decomposition.deepseek.parenthood` | −10.4pp [−12.8, −8.0] (t −8.5) | ✓ | | OK |
| dec_par_haiku | §4.2 table | `−19.2pp [−23.4, −15.0] (t −8.9)` | `docs/phase3/round5_stats.json::primary_decomposition.haiku.parenthood` | −19.2pp [−23.4, −15.0] (t −8.9) | ✓ | | OK |
| dec_par_luna | §4.2 table | `−12.1pp [−16.3, −7.9] (t −5.6)` | `docs/phase3/round5_stats.json::primary_decomposition.luna.parenthood` | −12.1pp [−16.3, −7.9] (t −5.6) | ✓ | | OK |
| dec_par_qwen | §4.2 table | `−7.3pp [−10.3, −4.3] (t −4.7)` | `docs/phase3/round5_stats.json::primary_decomposition.qwen.parenthood` | −7.3pp [−10.3, −4.3] (t −4.7) | ✓ | | OK |
| dec_lab_ds | §4.2 table | `+1.7pp [+0.5, +2.9] (t 2.7)` | `docs/phase3/round5_stats.json::primary_decomposition.deepseek.label` | +1.7pp [+0.5, +2.9] (t 2.7) | ✓ | | OK |
| dec_lab_haiku | §4.2 table | `−1.1pp [−3.2, +0.9] (t −1.1)` | `docs/phase3/round5_stats.json::primary_decomposition.haiku.label` | −1.1pp [−3.2, +0.9] (t −1.1) | ✓ | | OK |
| dec_lab_luna | §4.2 table | `+6.5pp [+3.7, +9.2] (t 4.6)` | `docs/phase3/round5_stats.json::primary_decomposition.luna.label` | +6.5pp [+3.7, +9.2] (t 4.6) | ✓ | | OK |
| dec_lab_qwen | §4.2 table | `+6.7pp [+4.9, +8.5] (t 7.3)` | `docs/phase3/round5_stats.json::primary_decomposition.qwen.label` | +6.7pp [+4.9, +8.5] (t 7.3) | ✓ | | OK |
| dec_bun_ds | §4.2 table | `−10.6pp [−12.7, −8.6] (t −10.0)` | `docs/phase3/round5_stats.json::primary_decomposition.deepseek.bundle` | −10.6pp [−12.7, −8.6] (t −10.0) | ✓ | | OK |
| dec_bun_haiku | §4.2 table | `−17.4pp [−20.2, −14.5] (t −11.8)` | `docs/phase3/round5_stats.json::primary_decomposition.haiku.bundle` | −17.4pp [−20.2, −14.5] (t −11.8) | ✓ | | OK |
| dec_bun_luna | §4.2 table | `−11.5pp [−15.4, −7.5] (t −5.7)` | `docs/phase3/round5_stats.json::primary_decomposition.luna.bundle` | −11.5pp [−15.4, −7.5] (t −5.7) | ✓ | | OK |
| dec_bun_qwen | §4.2 table | `−12.1pp [−14.7, −9.5] (t −9.2)` | `docs/phase3/round5_stats.json::primary_decomposition.qwen.bundle` | −12.1pp [−14.7, −9.5] (t −9.2) | ✓ | | OK |
| e2_pm_ds | §4.1 table | `| .357 | .233 | .297 | .387 |` | `docs/report/stats.json::models.*.e2_clustered.cells.parent|female.p` | | .357 | .233 | .297 | .387 | | ✓ | | OK |
| e2_pf_ds | §4.1 table | `| .349 | .276 | .294 | .398 |` | `docs/report/stats.json::models.*.e2_clustered.cells.parent|male.p` | | .349 | .276 | .294 | .398 | | ✓ | | OK |
| e2_cm_ds | §4.1 table | `| .419 | .266 | .228 | .407 |` | `docs/report/stats.json::models.*.e2_clustered.cells.parent_committed|female.p` | | .419 | .266 | .228 | .407 | | ✓ | | OK |
| e2_gm_ds | §4.1 table | `| .310 | **.110** | .186 | .230 |` | `docs/report/stats.json::models.*.e2_clustered.cells.parent_gap|female.p` | | .310 | .110 | .186 | .230 | | ✓ | | OK |
| e2_gf_ds | §4.1 table | `| .308 | .130 | .184 | .256 |` | `docs/report/stats.json::models.*.e2_clustered.cells.parent_gap|male.p` | | .308 | .130 | .184 | .256 | | ✓ | | OK |
| di_haiku_cross | §4.7 | `exceeds **31%**` | `docs/final/disparate_impact_stats.json::Haiku.crossing_womens_prevalence` | 31% | ✓ | | OK |
| di_scenario_low | §4.7 | `.88–.96` | `docs/final/disparate_impact_stats.json::*.scenario_20_5` | .88–.96 | ✓ | | OK |
| cod_kappa_retained | §4.2 mechanism | `Six codes reach κ ≥ .70 overall (.71–.93)` | `docs/final/coding_stats.json::report_summary` | (.71–.93) | ✓ | | OK |
| cod_kappa_dropped | §4.2 mechanism | `(qualifications, κ .02; gender, κ .31)` | `docs/final/coding_stats.json::report_summary` | qualifications, κ .02; gender, κ .31 | ✓ | | OK |
| cod_kappa_other | §4.2 mechanism | `availability (κ .68) and family (κ .63)` | `docs/final/coding_stats.json::report_summary` | availability (κ .68) and family (κ .63) | ✓ | | OK |
| cod_gap_int | §4.2 mechanism | `the employment gap is cited in 24–91% of losses for the three interruption cues` | `docs/final/coding_stats.json::report_summary` | 24–91% | ✓ | | OK |
| cod_gap_par | §4.2 mechanism | `in at most 4% for parent cues without a gap` | `docs/final/coding_stats.json::report_summary` | at most 4% | ✓ | | OK |
| cod_fam_fam | §4.2 mechanism | `family is cited in 12–64% of losses for parent cues` | `docs/final/coding_stats.json::report_summary` | 12–64% | ✓ | | OK |
| cod_fam_nonfam | §4.2 mechanism | `never for the travel gap or the disclosure placebo` | `docs/final/coding_stats.json::report_summary` | never | ✓ | | OK |
| cod_avail_dsq | §4.2 mechanism | `(39–52% of interruption losses)` | `docs/final/coding_stats.json::report_summary` | 39–52% | ✓ | | OK |
| cod_avail_hl | §4.2 mechanism | `(≤ 15%)` | `docs/final/coding_stats.json::report_summary` | ≤ 15% | ✓ | | OK |
| cod_irr_losing | §4.2 mechanism | `Qwen 90%, Haiku 69%, Luna 56%, DeepSeek 53%` | `docs/final/coding_stats.json::report_summary` | Qwen 90%, Haiku 69%, Luna 56%, DeepSeek 53% | ✓ | | OK |
| cod_irr_won_hl | §4.2 mechanism | `(64%, 50%)` | `docs/final/coding_stats.json::report_summary` | (64%, 50%) | ✓ | | OK |
| cod_irr_won_dsq | §4.2 mechanism | `(19% and 42% when the parent wins)` | `docs/final/coding_stats.json::report_summary` | (19% and 42% when the parent wins) | ✓ | | OK |
| cod_haiku_protected | §4.2 mechanism | `protected characteristics 12pp more often for mothers, Holm` | `docs/final/coding_stats.json::report_summary.haiku_protected_diff_pp` | 12pp more often for mothers, Holm | ✓ | | OK |
| spend_experiments | §2.1 | `$188.52` | `docs/final/study_totals.json::grand_total.cost_excl_coding` | $188.52 | ✓ | | OK |
| spend_coding | §2.1 | `$0.66 for rationale coding` | `docs/final/study_totals.json::grand_total.coding_cost` | $0.66 for rationale coding | ✓ | | OK |
| spend_total | Appendix E | `$189.18 incl. coding` | `docs/final/study_totals.json::grand_total.cost_usd` | $189.18 incl. coding | ✓ | | OK |

**50/50 claims verified.**
