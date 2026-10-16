# Review notes on docs/report/report.md (2026-10-16)

Fix in priority order. "MUST" items change headline claims; re-run the analysis in the uv
environment and regenerate report.md, stats.json, and figures afterwards.

## MUST 1 — Haiku's pregnancy "salary cut" (−$18,713) is an artifact of salary withholding

- In E1, Claude Haiku 5.5 often returns `starting_salary_usd: 0` while all other fields are
  normal (fit 7–8, interview true). The rationale says salary is withheld because pregnancy /
  marital status is a protected characteristic. These rows have `refusal_flag = false`.
- Zero-salary rate (E1, female): none 3.1%, married 7.3%, **pregnant 19.8%**.
- Within-résumé pregnant − none salary, **excluding zeros**: −$692 (−1.0%) — in line with the
  other models (DeepSeek −$688, Luna +$514, Qwen −$97).
- Fix:
  1. Treat `starting_salary_usd == 0` as missing for salary analyses in all models
     (other models also have 1–6% zeros).
  2. Add a new outcome `salary_withheld` (= salary 0 or null) and report it by condition and
     model. Haiku's withholding concentrated on pregnancy/marriage cues is a finding in itself
     ("abstention as a response to protected cues").
  3. Extend refusal detection: a response is an *abstention* if the rationale declines to
     score/rank because of a protected characteristic, even with valid JSON. Report abstention
     rates per experiment × condition; check whether `interview = false` in pregnant cells is
     driven by abstentions.
  4. Remove the −$18.7k / "24% cut" claim from abstract, §5.2, §5.8, §7.

## MUST 2 — E3 compositions are confounded with résumé identity

From `_e3_pool` in `src/audit/plan.py`:
- Composition **d** (all parents): gender is fixed by résumé index (0, 2, 4 always female;
  1, 3, 5 always male). "Mothers outrank fathers in all-parent pools" is fully confounded
  with résumé quality. Delete this claim or redesign (rotate genders across résumés).
- Compositions **a/b** (token parent): the parent rotates only over résumés 0–3; résumés 4–5
  (the ranking-pool extras) are always childless, and in comp a résumé 4 is *always* a
  childless woman. The childless-women reference rate is therefore dominated by one extra
  résumé. The naïve impact ratio compares different résumés.
- Fix: estimate the token-parent effect with résumé fixed effects (and pool/rotation FE):
  `top3 ~ parent × female + C(resume_id) + C(position)`, SE clustered by occupation, and
  compute impact ratios from adjusted rates. Report the naïve and adjusted ratios side by side.
  Also report the childless top-3 rate of résumés 4–5 vs 0–3 to show whether extras are stronger.
- If adjusted ratios stay < 0.80 the headline survives; otherwise soften it.
- The "penalty attaches to being the caregiving outlier" interpretation (§5.4) depends on comp
  c/d comparisons and must be rechecked after the fix.

## MUST 3 — Standard errors ignore clustering; z-values and I² are inflated

- E2 binomial tests treat ~2,400 calls per cell as independent, but they come from
  20 occupations × 2 résumé pairs × 3 name pairs × 5 near-identical samples.
- Re-estimate E2 with cluster-robust SEs (cluster = résumé pair or occupation), e.g. a linear
  probability model or GEE logit of `parent_chosen` on contrast × gender, and use those SEs in
  the meta-analysis. Recompute I²; the current 98% is inflated by too-small within-model SEs.
- Remove "p < 10⁻³⁰ (z > 10)" (§4.3) and the inconsistent sentence in §6 ("smallest z is 6.1
  … ≈ −11"). Report clustered z / CIs instead.

## MUST 4 — "Fathers penalized at rates indistinguishable from mothers" is false for Haiku

Using stats.json (naïve SEs; recheck with clustering):
- Haiku parent: .232 (F) vs .275 (M), z ≈ 3.4; parent_committed: .266 vs .331, z ≈ 4.9;
  parent_gap: .111 vs .131, z ≈ 2.1.
- Qwen parent_gap: .229 vs .256, z ≈ 2.2.
- Correct statement: *no model shows a fatherhood bonus (fathers are always below parity), but
  Haiku penalizes mothers more than fathers.* Test the gender difference formally (contrast ×
  female interaction, clustered SE) for every model and report it in a table. Update abstract
  point (2) and §5.3(b), §7.

## MUST 5 — Numbers in the report do not match stats.json

- §5.3 table, Qwen "parent + high commitment": report says .434 / .421; stats.json has
  **.407 (F) / .430 (M)**. Regenerate every table from stats.json, not by hand.
- §8(4) says "32% of base résumés are synthetic"; §3.1 says 92 of 120 are synthetic (77%).
- §2.4 says Qwen validity 99.8% "after repair" while §4.4 says primary estimates use strict
  validity. State which data each estimate uses.

## MUST 6 — Human benchmark comparison (§5.7) is wrong in two ways

1. Correll, Benard & Paik (2007) report very large human hiring gaps (from memory — verify
   against the paper: mothers recommended for hire ~47% vs ~84% for childless women in the
   lab; childless women received ~2× the callbacks of mothers in the employer audit). So
   "shortlisting penalties … have no counterpart in the human literature at this magnitude"
   is incorrect. Rewrite: LLM hiring penalties are *smaller* than or comparable to the human
   benchmark, not larger.
2. The LLM commitment effect is a paired d_z (mean / SD of within-pair differences); Correll's
   is a between-subjects d. These are not comparable. Either convert (d_av using the pooled SD
   of the two candidates' ratings) or drop the d comparison.

## SHOULD 7 — Materials: some base résumés are not qualified for the job

Mean overall_fit (E1, all models): lawyer_00 1.7–2.7, lawyer_01 2.0–3.7 (rationales: no law
degree / bar admission — the résumé is a legal assistant), registered_nurse_01 3.7–5.0,
medical_assistant_01 3.0–5.7. These candidates are rejected regardless of family status, which
compresses effects for those occupations and contaminates the moderator analysis.
- Run a sensitivity analysis excluding résumés with mean fit < 4 (or the lawyer occupation).
- Document this in limitations; for future runs, fix the licensed-occupation résumés.

## SHOULD 8 — Moderator section (§5.6) explanation is incorrect

Résumé fixed effects absorb occupation *main* effects, not `Z × family × female` interactions,
so "the occupation gradient is mostly absorbed by résumé fixed effects" is wrong. The honest
statement: the moderator interactions are small and not significant; occupational moderation
is not supported in scoring tasks. Also: the DeepSeek competence × female-share result cited
in §5.6 is not in stats.json — add it or remove it. Consider estimating moderation in E2/E3
(where the variance is) rather than only in E1.

## SHOULD 9 — Preregistration claim

§1 says hypotheses were "preregistered". If no OSF registration exists, change to "specified
in advance in the project proposal" and do not use the word preregistered.

## SHOULD 10 — E1 ceiling

Interview rates are 95–100%. Also report `overall_fit` (1–10) and the mechanism ratings as
primary E1 outcomes, since interview yes/no has no variance.

## NICE 11 — Smaller fixes

- §5.3 table header typo "w / men".
- §5.2 "relocation… a useful placebo": fine, but `married` also raises Haiku's salary
  withholding (7.3%) — mention after MUST 1.
- Position bias: DeepSeek P(A) = 0.83 means most of its choices are position-driven; add a
  robustness check restricted to pairs where the model's choice differs across the two
  position orders (or a model with position FE).
- Abstract/title "191,000 decisions": keep, but state that effective sample size is
  much smaller due to clustering.

---

# Round 2 review (rev. 2 report, 2026-10-16)

Most round-1 items are fixed well (withholding separated, E2 clustered at résumé pair,
E3 résumé-FE ratios, benchmark direction corrected, composition d dropped). Remaining:

## R2-MUST 1 — Haiku's pregnancy abstentions also deny interviews (report says the opposite)

§5.2 says withheld pregnant applicants are still rated normally ("interview ≈ true"). The logs
show otherwise (Haiku, E1, women):

| family_code | withheld? | n | interview rate |
| --- | --- | --- | --- |
| none | no / yes | 1163 / 37 | .985 / .000 |
| pregnant | no / yes | 947 / 234 | 1.000 / **.299** |
| married | no / yes | 1110 / 88 | .998 / .261 |

Overall interview rate ≈ 86% for pregnant vs ≈ 96% for childless women (≈ −9 to −10pp).
So abstention coincides with interview denial: this is a substantive pregnancy penalty in
Haiku, not just a missing salary. Fix: estimate pregnant − none interview (and fit) gaps
with résumé FE and résumé-clustered SEs for all models; update abstract item (5), §5.2,
§5.8, §7. Frame withholding honestly: the rationale shows protective intent, but the
downstream result is fewer interviews.

## R2-MUST 2 — Table 1 still disagrees with stats.json

- Qwen "parent + committed": report .368 / .391; stats.json `e2_clustered` **.407 / .430**
  (t −6.0 / −5.4).
- Committed row lacks t-values for Haiku (−10.1 / −8.6), Luna (−9.0 / −8.5), Qwen.
- Generate Tables 1–3 programmatically from stats.json (no hand-typed numbers).

## R2-MUST 3 — E4 has no inference, and several claims don't match its own numbers

`e4_gaps_pp` has point estimates only. Cells have ~480 calls from 32 résumés; the naïve SE of a
pp difference near a 97% base rate is ~1.1pp before clustering.
- Estimate `interview ~ jd_variant × parent_gap × female + C(resume_id) + C(name)`,
  SE clustered by résumé (32 clusters); report CIs for each cell and the DiD vs base.
- Claims to recheck after that:
  - "family-friendly alone penalizes leave-gap mothers in all four models" (−1.0 to −1.5pp ≈ 1 naïve SE)
  - "greedy + family-friendly makes matters worse for both" — DeepSeek greedy_ff is −5.83 for
    **both** mothers and fathers; Qwen greedy_ff is −0.83 (F) vs −3.12 (M).
  - "mothers pay about double" holds only in the greedy-only cell.
- Soften the §5.5 title ("is causal") to what survives the tests.

## R2-MUST 4 — Moderator regressions were not re-run with withheld salaries excluded

`e1_moderator_regressions(tables[m]["e1"])` in `scratch/report_stats_v2.py` uses the raw
table; DeepSeek's "parent_gap gender gap @ mean Z" is still −1,271.25, identical to rev. 1.
Set salary 0 → NaN before calling it. Also §5.6 calls a "gap @ mean Z" an *interaction* —
it is not; say the interactions are all n.s.

## R2-SHOULD

- Abstract: "token mother's adjusted top-3 rate falls to 25–81%" — mothers' ratios are
  .25–.78 (.81 is Luna's fathers).
- §5.4: "four-fifths violation … on the mothers' margin, for DeepSeek and Qwen" — DeepSeek
  fathers (.70) also violate; Qwen fathers .798 is at the line.
- Benchmark: rev. 1 used −7.4% for Correll's salary gap, rev. 2 uses ≈ −9%. Compute it from
  the paper's table (I recall the commonly cited figure is $11,000 ≈ 7.4%); then fix
  "one-fifth" vs "one-quarter".
- §5.3 calls heterogeneity "modest" with I² = 91–95%; §6.1 says model identity matters.
  Make consistent ("every model penalizes; magnitude varies substantially by model").
- Table 2: Qwen committed t = −2.6 is significant (df 39) — bold it.
- Qwen repair counts: §4.4 says 2,902 recovered; §6.3 says 2,621 dropped. Reconcile.
- §6.4 low-quality résumés: also `registered_nurse_01` (mean fit 3.7–5.0) and
  `medical_assistant_01` (3.0–5.7) are weak; mention, and include them in the sensitivity run.
- Reproducibility: move `scratch/report_stats_v2.py` into `src/audit/analysis/` and add a CLI
  entry; scratch/ is not a durable home for the code behind every reported number.
- Multiple comparisons: Table 2 runs 12 tests; note that Haiku's three survive Holm
  correction (check), Qwen's may not.
