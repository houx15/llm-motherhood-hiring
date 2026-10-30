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

---

# Round 3 review (Draft 4.0, 2026-10-22)

The integrated draft is a big step forward: a clear three-question structure, the cue-level
invariance result, and the placebo design. The items below change or weaken specific claims.

## R3-MUST 1 — Placebo decomposition compares different occupation sets

In phase-3 E2 at L0, the contrasts were run on different occupations (DeepSeek counts from logs):

| contrast at L0 | occupations | sampling |
| --- | --- | --- |
| `personal`, `gap_travel`, `gap_parental_only` | O20 + O8 | 2 samples |
| `parent` | O20 (drift anchor, 1 sample) + O8 | mixed |
| `parent_gap`, `parent_committed` | **O8 only** | 2 samples |

`placebo_decomposition()` takes plain means within a cue level, so e.g. "family bundle on top
of the gap" = mean(`parent_gap`, O8) − mean(`gap_parental_only`, O20+O8). The O8 occupations
have different baseline penalties (e.g. Luna's O8 leave-gap .095 vs .186 in the main run), so the
decomposition is confounded with occupation mix.

Fix:
- Compute every component on a **matched occupation set where all contrasts exist**:
  (a) O8 at each of L0–L3; (b) O20 at L1 and L2. Report both; (b) is the larger sample.
- Use pair-matched differences: for each résumé pair, difference of pair-cluster means between
  the two contrasts; t-test across pairs; Holm within the decomposition family.
- Report t / CI for every component. "Not significant for any model" (label effect) currently has
  no test behind it.
- Then re-check abstract point (3) and §4.3/§5.1 wording.

## R3-MUST 2 — The manipulation check measures willingness to state gender, not inference

Haiku answers "unknown" for 58% of name-only packets. But in the main-run E1 `none` condition,
whenever Haiku's rationale uses a gendered pronoun it **always** matches the name:
female names → "she/her" 103 times, "he" 0; male names → "he/his" 46 times, "she" 0.
So Haiku infers gender from names; it declines to *label* it when asked directly.

Fix:
- Reframe §4.1: the direct question measures willingness to attribute gender (itself an
  interesting alignment behavior), not legibility.
- Add an implicit check: pronoun congruence in rationales by model and cue level.
- Remove: "name-only audits under-treat the gender information actually available", the link
  "Luna — which reads names correctly only 66% of the time", and "Haiku recognizes male names
  better" (Haiku uses female pronouns more often than male ones).

## R3-MUST 3 — Direct gender preference (§4.5) has no inference

CROSS_MODEL.md gives point estimates only. With ~960 calls per cell over 40 pairs, an SE of
~.02 is plausible, so Haiku's ".544 → .470" may not differ from parity or from L0.
- Add pair-clustered t vs .50 for each cell, and level contrasts (L1 − L0, L2 − L1) with Holm.
- Keep "Luna surges" / "Haiku flips against mothers" only if they survive.
- Abstract point (5) mixes cells: ".52 → .65 for mother-vs-father" — .52 is Luna's *childless*
  L0, .65 is mother-vs-father L1 (mother-vs-father L0 is .578).

## R3-MUST 4 — Factual errors

- §4.8 quotes the greedy wording as "must be willing to work long hours and be fully committed".
  The actual text (config/jd_variants.yaml): "This is a fast-paced role. Candidates must be
  available after hours and on weekends as needed, and travel up to 40% of the time."
- §4.6 "No other model abstains … (≤ 1.8%)": phase-3 Qwen pregnant withholding is 2.9% (L2) and
  2.6% (L1); main-run Qwen 5.8%, Luna 3.1%. State the actual ranges.
- §4.6 "−9.4pp … consistent with 19.8% × 70% denial": 19.8% × 70% ≈ 13.9pp. The net gap reflects
  *excess* withholding over the childless baseline (19.8% − 3.1%) and baseline interview rates.
  Fix the arithmetic or drop the sentence.
- References: Gaddis (2017) is "How Black Are Lakisha and Jamal? Racial Perceptions from Names
  Used in Correspondence Audit Studies," *Sociological Science* 4: 469–489. The cited title and
  pages do not match.

## R3-MUST 5 — Missing prior literature; intro overclaims novelty

The reference list has no prior LLM hiring audits. The intro says existing audits "mostly
evaluate a single decision format", but pairwise choice (Rozado 2025) and ranking (Bloomberg /
Yin et al. 2024) already exist, and parental-leave / pregnancy cues were tested (Veldanda et al.
2023; Frermann et al. 2023). Add these plus An et al. (2025), Armstrong et al. (2024), Wilson &
Caliskan (2024), Benard & Correll (2010), Kleinberg & Raghavan (2021); position the contribution
as *crossing tasks, cues, and gender-information regimes on identical materials*, not as the
first comparative audit. (Full list in docs/proposal.md.)

## R3-SHOULD

1. **Occupational moderation (§4.9).** Only DeepSeek's female-share coefficient is nominally
   significant (p = .025, 24 tests across 4 models × 6 regressors, no correction); "for every
   model" refers only to sign. The statistical-discrimination interpretation is speculative and
   also applies to fathers, which does not fit a "where mothers are common" story. It also
   contradicts the main-run null. Keep as exploratory, drop it from §5.1 as supporting evidence.
2. **Theory (§5.1).** "Committability heuristic … closer to statistical discrimination" ignores
   that (a) the family bundle is penalized beyond the gap, and (b) commitment evidence only
   partly restores parity (and deepens the penalty for Luna). Present the gap component as
   consistent with availability inference and the bundle/commitment results as a normative
   component (Benard & Correll 2010).
3. **Mother vs father by outcome** (SPEC_PHASE3 §8.4) is missing: choice, salary, commitment,
   competence, likability, interview, withholding per model. From the main run, mothers' extra
   penalty shows up mainly in salary and perceived commitment for DeepSeek, Qwen, and Haiku —
   a "perception asymmetric, decision symmetric" result worth a table.
4. **Position bias numbers** changed vs rev. 3 (DeepSeek P(A) .83 → .68). Say which run each
   number comes from; delete "consistent with its opposite direction of asymmetry in other tasks".
5. **Drift.** The anchor was specified on E2 choice (flag |Δ| > .03); report E2 anchor deltas, not
   only interview. Note in §4 which tables are main-run vs phase-3, since prompt versions differ.
6. **Abstract (2)** "statistically indistinguishable for two models" — add the test (O8 L0 vs L3,
   pair-clustered) to the table.

---

# Round 4 review (Draft 4.1, 2026-10-22)

All round-3 items were addressed, and the framing (availability inference + normative bundle,
implicit pronoun check, matched-set decomposition) is much stronger. Remaining issues are in the
new `src/audit/analysis/round3.py` and the reference list.

## R4-MUST 1 — round3.py clusters on *ordered* résumé strings (2× pseudo-clusters)

`_pm`, `_wm`, `_pair_means`, and `direct_gender_inference` all use
`groupby("resume_ids")`. `resume_ids` is ordered by role (`a+b` vs `b+a`), so each résumé pair
becomes two clusters. Checked in the DeepSeek phase-3 logs: O8 `parent` has **32 ordered strings
but 16 unordered pairs**; `gender_parent` has **112 ordered vs 56 unordered**. The two role-halves
share résumés and are not independent.

Fix: use the existing `pair_cluster()` from `report_stats.py` (sorted indices + occupation) in
every round-3 function; rerun decomposition, invariance, direct-gender, and drift tests; update
the report's n's ("32 pairs" for O8 → 16; "n = 112" → 56; §5.3 "40/32" → 40/16) and all t / Holm
results. Expect smaller |t|. Results most at risk: Luna's label effect (5/6 Holm), Haiku's
L1 − L0 = −4.6pp (t −3.3), the Holm counts in the decomposition table.

## R4-MUST 2 — `mother_father_main()` salary filter is wrong; §4.4 table has no inference

- `s = s[s != 0]` drops pairs whose salary *difference* is zero (identical offers) and keeps pairs
  where one side was withheld ($0), which produce diffs of tens of thousands of dollars. It should
  drop pairs where **either** candidate's salary is 0/null, and keep zero differences.
  (My earlier computation with that rule: parent cue M − F salary ≈ DeepSeek +$81, Haiku −$170,
  Luna −$134, Qwen −$436 [t ≈ −2.1] — different from the table.)
- All rows are raw call-level means with no SE. Compute per-pair-cluster means for mothers and
  fathers, take pair-matched differences, report t and Holm.
- Units: the E1 interview row is a proportion (−.006) while the text uses pp elsewhere.

## R4-MUST 3 — The "perception-asymmetric" claim is not supported by the table as shown

The §4.4 table shows ≈ 0 mother − father differences for DeepSeek, Luna, and Qwen in every row
(only Haiku is asymmetric), yet the text and abstract (4) say mothers' extra penalty appears in
commitment/likability/salary "for three models". The evidence for that pattern was in **E1**, not E2
(main run, résumé-clustered, from round-2 checks): DeepSeek commitment M − F −0.09 to −0.12
(t ≈ −3 to −3.8) and salary −$607 (parent) / −$749 (gap, t −2.5); Qwen E1 salary −$833 (t −1.7).
Either add E1 rows (commitment, competence, likability, salary; clustered by résumé, Holm) and
state exactly which models show it, or soften the claim to "Haiku genders perception and choice;
the others show little mother-specific penalty on any margin".

## R4-MUST 4 — References are paraphrased, with wrong titles/authors

Copy exact citations from `docs/proposal.md`:
- An, J., Huang, D., Lin, C., & Tai, M. (2025). Measuring gender and racial biases in large
  language models: Intersectional evidence from automated resume evaluation. *PNAS Nexus*, 4(3),
  pgaf089. (Current entry has a wrong title and author initial.)
- Armstrong, L., Liu, A., MacNeil, S., & Metaxa, D. (2024). The Silicon Ceiling: Auditing GPT's race
  and gender biases in hiring. arXiv:2405.04412. (Current title is invented.)
- Rozado, D. (2025). Gender and positional biases in LLM-based hiring decisions: Evidence from
  comparative CV/résumé evaluations. arXiv:2505.17049.
- Veldanda, A. K., et al. (2023). Investigating hiring bias in large language models /
  algorithmic hiring bias in the era of ChatGPT. arXiv:2310.05135 (check exact title).
- Wilson, K., & Caliskan, A. (2024). Gender, race, and intersectional bias in resume screening via
  language model retrieval. AIES. (Current entry: wrong initial and title.)
- Yin, L., Alba, D., & Nicoletti, L. (2024). OpenAI's GPT is a recruiter's dream tool. Tests show
  there's racial bias. *Bloomberg*.
- Frermann, L., Njoto, S., Cheong, M., & Ruppanner, L. (2023) — first name is Lea; title still to verify.
Rule for the agent: never paraphrase a title; if unknown, write "[title to verify]".

## R4-SHOULD

- §4.6 "No model exceeds 3.1% withholding in any non-pregnancy cell" — main-run Qwen is 4.2%
  (none and married), and Haiku itself is 7.3% for married women. Restate precisely.
- §4.10 "pre-registered ±.03 flag" → "pre-specified" (consistent with §3: not OSF-registered).
- §5.1 says the bundle adds ".09–.24"; the table says −.08 to −.24.
- Abstract (3) "Holm-surviving in all 24 model×set tests" — recheck after R4-MUST 1.

---

# Round 5 — academic review along seven dimensions (Draft 4.1; report.md unchanged since 10:05 UTC)

R4 technical items are still open (see R4-MUST 1–4). This round is about the paper as research.

## 1. Key question

- The title asks "Do LLM hiring tools penalize mothers?" but the answer the data give is
  "they penalize caregivers and employment gaps, largely regardless of gender". The title and
  abstract are framed around the hypothesis the paper ends up rejecting.
- Six numbered findings in the abstract dilute the message. Proposed core claim:
  *LLM screeners do not reproduce the gendered motherhood penalty; they impose a gender-neutral
  caregiver penalty, visible only when candidates are compared, with thin vendor-specific
  gendered behaviors layered on top.*
- Suggested title direction: "From Motherhood Penalty to Caregiver Penalty: How LLM Résumé
  Screeners Treat Family Signals" (or similar). Q1/Q2 stay; Q3 becomes supporting evidence.

## 2. Situating the question

Missing literatures that change how readers interpret the findings:
- **Gender-neutral penalties with gendered impact.** Acker (1990) ideal/disembodied worker;
  disparate impact / indirect discrimination (Title VII; EU law). A caregiver-general penalty is
  not benign: caregiving gaps and PTA-type signals are carried mostly by women, so a
  gender-neutral rule produces a gendered outcome. The discussion must say this explicitly or
  readers will conclude "no gender problem".
- **Fathers who signal caregiving are penalized in human studies too** (flexibility stigma):
  Rudman & Mescher (2013); Williams, Blair-Loy & Berdahl (2013). The "no fatherhood bonus;
  fathers penalized" result is consistent with this literature for the leave cue, and differs
  from Correll et al. only for the plain PTA cue. Position it that way.
- **Employment-gap audits.** Weisshaar (2018, ASR) on re-entry after family-related lapses;
  Kroft, Lange & Notowidigdo (2013) on duration dependence. These are the human benchmarks for
  the gap/label decomposition — far more direct than Correll for this component.
- Statistical vs normative discrimination (Phelps 1972; Benard & Correll 2010) is used; good.
- AI side: alignment/over-correction and format sensitivity of LLM evaluations; algorithmic
  monoculture (Kleinberg & Raghavan 2021 — cited in references but not used in text).
(Verify every citation against the source before adding; no paraphrased titles.)

## 3. Does the method address the question?

- **Task dependence may partly be a forced-choice amplification.** When two candidates are
  near-equivalent, a small consistent preference becomes a large choice share (a tie-breaker).
  "The penalty lives in the comparison, not the score" needs two checks:
  (a) relate the E2 penalty to the pretest quality gap between the two résumés in each pair —
      if it is concentrated in near-tie pairs, say so;
  (b) translate E1 score differences into the choice probability they would imply under a
      simple noise model (e.g. probit on E1 fit with its residual SD) and show E2 exceeds it.
  Without this, a reviewer can argue the scoring scale (integer, ceiling) is simply too coarse.
- **The travel placebo may carry its own stigma** (leisure, low seriousness). "Parental leave
  costs the same as travel" supports "the label adds nothing" only if travel is a neutral reason.
  Add one or two neutral gap labels (e.g. "company closure — job search", "full-time
  certification program") at L0 on O20, DeepSeek + Haiku (~$5–10), or state this as a limitation
  and soften "availability inference".
- **Ecological validity of the cue.** US applicants rarely write "married with two children" in a
  cover note; say the cue is a strong, explicit disclosure by design, and that real-world
  signals (gaps, volunteer lines, references) are weaker. The leave gap is the most realistic cue —
  emphasize it.
- **Model scope.** Four low-cost tiers, no system prompt, reasoning off. Real HR tools use system
  prompts (often with fairness instructions) and sometimes larger models. State the population
  of inference: high-volume, low-cost screening configurations.

## 4. Measurement validity and robustness

- Open from R4: ordered-pair clustering in round3.py (n doubled); salary filter bug in the
  mother–father table; no inference in that table; reference errors.
- The decomposition table reports ranges across six matched sets — hard to read and not an
  estimate. Choose a primary estimand (e.g. O20 at L1/L2 pooled, 40 pairs) with a CI; put the
  six sets in an appendix as robustness.
- Report the gap's own effect (`gap_travel` − `none`) with a CI; the text says "costs 10–20pp"
  without a table entry.
- Main tables still lack uncertainty (E2 table: "every cell |t| ≥ 5" only). Add CIs.
- Main-run vs phase-3 tables use different prompt versions; label each table's source run.

## 5. Presentation of results

- Abstract: cut to 3–4 findings; one unit system (pp of choice probability; % of salary). Avoid
  mixing proportions (.107), pp, t-values and dollars in one sentence.
- Figures: the listed figures are main-run only. Phase-3 results (the paper's center now) have
  none. Minimum set:
  1. Same cue across scoring / choice / ranking on a common scale (task dependence)
  2. Decomposition waterfall: none → disclosure → gap → label → family bundle
  3. L0–L3 lines per model (gender-information invariance)
  4. Direct gender preference by cue level (vendor divergence)
  5. Haiku abstention and its interview consequence
- Each results subsection should open with its one-sentence answer, then the evidence.

## 6. Interpretation for readers

- "Chosen 23% of the time against an otherwise-identical childless candidate": the paired
  résumés are *different* (comparable, roles counterbalanced). Say "a comparably qualified
  childless candidate, with résumé roles counterbalanced".
- Explain what P = .23 means in plain terms (the parent loses about 3 of 4 head-to-head finals;
  50/50 would be no penalty).
- The human-benchmark comparison ("models reduce the human penalty") compares a forced-choice
  share with a 2007 student-lab hire rate. Keep it out of the abstract; in the text, present it as
  context, not a finding, or readers will take away "LLMs are less biased than humans".
- "Single-résumé audits would certify all four models as fair": E1 effects are small but some are
  significant. Say "would detect only small effects".
- State the disparate-impact implication of the gender-neutral penalty (see §2).

## 7. Coherent framework

The pieces fit a two-layer account that the discussion almost states:
- **Layer 1 — a caregiving / ideal-worker layer.** Common to all four vendors in sign; invariant
  to gender information; driven by the gap and overt family signals; amplified when the job ad
  makes the ideal-worker norm salient (E4 greedy wording); hidden in single scores and exposed in
  comparisons. This is Acker's gender-neutral-in-form, gendered-in-effect ideal worker.
- **Layer 2 — a thin, vendor-specific gender layer.** Appears mainly when gender is made
  salient: Luna's pro-woman shift, Haiku's mother-specific penalty, refusal to state gender, and
  pregnancy abstention. Consistent with alignment shaping overt gender behavior while leaving
  layer 1 intact.
- Task dependence explains why audits miss layer 1; cue-level manipulation explains layer 2.
- Occupation results (weak) and E4 (greedy wording) then slot in as "what activates layer 1".
Rewrite the introduction's questions and the discussion around this structure.

---

# Round 6 review (Draft 5.0, commit 3e540f8)

R4 technical fixes are in (unordered-pair clustering, salary filter, inference on the
mother–father table, references from the proposal). The paper now has a clear question, a
coherent two-layer framework, and phase-3 figures. Remaining items, by the seven dimensions.

## 1. Key question — precise the central concept
The decomposition shows Layer 1 has two parts: a **generic interruption penalty** (an 8-month
*travel* gap alone costs 11–26pp) and a **caregiver-specific family-signal penalty** (parent −
personal; bundle on top of a labeled leave). "Caregiver penalty" fits the second part only.
State in the abstract, §1 and §5.1: Layer 1 = interruption penalty (anyone with a gap; caregivers
carry most gaps) + family-signal penalty (caregiver-specific). Keep the title, define the term.

## 2. Situating — good; two citation errors (my earlier suggestions, from memory)
- Weisshaar (2018) is "From opt out to blocked out: The challenges for labor market re-entry
  after family-related employment lapses," *ASR* 83(1), 34–60 (check). Current title/issue/pages
  look wrong.
- Rudman & Mescher (2013): "…Is flexibility stigma a femininity stigma?" (not "norm").
- Williams, Blair-Loy & Berdahl (2013): "Cultural schemas, social class, and the flexibility
  stigma," *Journal of Social Issues* 69(2), 209–234 (not *Social Problems*).
Verify all ◆ entries against the source before submission.

## 3. Method vs question — the amplification test needs one more step
- Forced choice amplifies *any* difference, including ordinary quality differences. To claim "the
  comparison itself adds penalty that scores do not contain", show that **family cues are
  amplified more than quality differences**. Use the pairs themselves: the two résumés in each
  pair differ in E1 fit; with roles counterbalanced you can estimate how strongly E2 choice tracks
  the E1 quality gap. Compare that amplification with the amplification of the family-cue gap.
- `round5.py` uses P = Φ(gap / σ) with σ = SD within family×gender×occupation. That σ mixes
  between-résumé variation with sampling noise, and a difference of two draws has SD σ√2.
  Use within-résumé SD (same résumé, same condition) and report sensitivity to σ.
- Lead with the strongest piece of evidence: Haiku's E1 fit gap for parents is *positive* (+.34)
  but it chooses parents 23% of the time — a sign reversal, which no amplification account produces.
- The "label" conclusion rests on travel as the reference gap. The neutral-label arm is designed;
  fielding it (company closure / certification program; L0, O20, DeepSeek + Haiku; ~$5–10) would
  turn the main limitation into a result. Otherwise keep the current caveat.

## 4. Measurement and consistency
- Abstract Finding 2: "the 8-month interruption and the explicit family bundle each cost 7–24pp"
  — the primary table gives interruption 10.6–26.0pp and bundle 10.5–17.6pp. Use primary-estimand
  numbers in the abstract.
- "Disclosure alone is nearly free": `personal` is −3 to −4pp with t −4.1 to −4.6 — small but
  significant. Say so.
- Decomposition table: CIs shown for some cells only, and the caption ("95% CIs shown where the
  six matched-set ranges … are summarized; brackets are the primary-estimand CIs") is confusing.
  Give every cell estimate [95% CI].
- §2.3 cue table is broken (`parent_gap` row has an unclosed quote; `parent_committed` row has
  two columns).
- §5.2 "vendor choice moves the penalty by a factor of two to eight" — not derived anywhere.
  Compute it or delete it.
- §4.10 "Table sources" lists §4.3 under both main run and phase 3.

## 5. Presentation — figures
- None of the figures is referenced in the text. Add "(Figure 9)" etc. at each claim.
- Fig 9: three panels in three units (fit points, choice share, ratio), and no CIs for E1/E3.
  The headline is better shown as *predicted choice share from scores vs observed choice share*,
  per model and cue — that is exactly the claim.
- Fig 10 ("waterfall") draws a cumulative path parity → +personal → +gap → label → +bundle, but the
  conditions are not nested that way (`gap_travel` does not contain the personal disclosure;
  `parent` is not on the path). Either plot the truly nested chain
  (none → gap_travel → gap_parental_only → parent_gap) plus `personal` and `parent` separately,
  or show the four components as a dot plot with CIs.
- Figs 10–12 have no CIs. Fig 12's y-axis starts at .475, which visually exaggerates small
  differences; add CIs and mark Holm-significant cells.
- Fig 13 right panel title "withheld ⇒ no interview" overstates — 30% are interviewed.

## 6. Interpretation
- §6 still says audits "will certify as fair systems that are not"; §5.2 correctly says
  single-résumé audits "detect only small effects". Use the softer, accurate wording throughout.
- Layer 2 "consistent with alignment shaping overt gender behavior" is an interpretation without a
  test in this study (no unaligned comparison). Label it as a conjecture.

## 7. Framework — coherent
The two-layer account now organizes the paper. With the Layer-1 split (interruption +
family signal) made explicit, every result has a place: task dependence (why audits miss Layer 1),
decomposition (what Layer 1 is), invariance (Layer 1 is not gender-based), E4 (what activates
Layer 1), direct gender + abstention (Layer 2).

## Round 6b — statistical inference checklist (Draft 5.0)

Done well: within-résumé contrasts; clustering at design units (E2 unordered pairs, E1 résumés,
E3 occupations with résumé/position FE, E4 résumés); Holm within test families; strict-validity
re-estimates; cross-model pooling with I².

To add:
1. **Equivalence tests for "no change" claims.** "Blind = names" (p ≥ .08, 16 pairs) is absence of
   evidence. Pre-state a smallest effect of interest (e.g. ±5pp) and run TOST; report the 90% CI.
   Same for "label adds nothing" (Haiku) and "Qwen at parity".
2. **Test differences between models/levels directly** (Gelman & Stern 2006: a significant vs a
   non-significant result is not a significant difference). E.g. Luna vs Qwen response to the
   field; Haiku vs others in mother − father gap: model × condition interaction, clustered.
3. **Small-cluster corrections.** O8 (16 pairs), E3 (20 occupations), E4 (32 résumés): use CR2
   with Satterthwaite df or wild cluster bootstrap; check that conclusions hold.
4. **Regression version of the cluster-mean t-tests** (LPM or logit with pair/résumé FE and
   clustered SEs, or crossed random effects for pair, name, occupation) as a robustness check,
   so position, paraphrase and name enter as controls.
5. **Uncertainty on the noise-model test** (bootstrap over résumé pairs: CI for observed −
   predicted).
6. **CIs in every table and figure**; one decimal convention.
7. **Confirmatory vs exploratory.** List the confirmatory tests (from SPEC/SPEC_PHASE3) in §2.6;
   everything else exploratory.
8. **Sensitivity / minimum detectable effects** for every null (invariance, occupational
   moderation, EEO wording).
9. **Scope of inference** stated: conclusions are about these four pinned model versions and
   résumés like ours; cross-model comparisons are descriptive (n = 4 models).

---

# Round 7 review (Draft 5.1, commit 68355a5)

Round 6/6b is done well: cue-vs-quality amplification (with the Haiku sign reversal up front),
corrected noise model with bootstrap CIs and an honest DeepSeek exception, TOST at ±5pp, direct
model contrasts, wild bootstrap, LPM checks, MDEs, confirmatory list, scope statement, CIs in
Figs 9–12. Remaining small fixes:

1. Header still says "Draft 5.0 … 2026-10-22".
2. "We pre-state ±5pp as the smallest effect of interest": it was chosen after data collection
   (round 6b). Say "chosen before running the equivalence tests, after data collection".
3. §4.3 heading "Removing gender information changes nothing" → "…leaves the penalty unchanged"
   (7/8 equivalent; explicit fields *do* change Haiku and Luna).
4. Haiku label: text says "90% CI [−3.2, +0.9]" but the table gives that as the 95% CI. Report the
   90% CI for TOST and the 95% CI in the table, labeled.
5. Abstract is ~600 words. Journals expect 150–250. Keep this as an extended summary and write a
   short abstract with the three findings.
6. Fig 10: legend sits on top of the "family bundle" row's markers; move it outside the axes.
   Fig 9: legend overlaps the parent-cue markers; add CIs to the predicted points if available.

Open by design decision (not yet done; see the "complete story" discussion):
- Rationale coding (mechanism evidence from existing logs; ~no API cost)
- Fairness-instruction system-prompt arm (does a standard fairness prompt remove Layer 1?)
- Disparate-impact quantification (gap prevalence by gender × measured penalties)
- Neutral gap-label arm (company closure / certification)

## Round 8 (2026-10-30) — organization pass

See docs/SPEC_FINALIZE.md (Part 1 analysis for opencode; Part 2 writing). Key items: rationale-coding mechanism
paragraph is not actually in report.md (despite commit fea0faf message); drop
`qualifications` (κ .01) and `gender` (κ .20) codes from claims; human-validation
CSV exposes machine codes (blind it); spend/call totals and §3 omit phase 4;
Figures 1–8 uncited.

## Round 9 (2026-10-30) — finalize F1–F6 review
See docs/SPEC_FINALIZE.md "Round 9". MUST: main-run stats.json regression (E3 identical
across models; Haiku/Qwen E2 contaminated by repair runs of phase-3 calls);
disparate impact inherits it; Holm `p or 1` bug inverts F1e significance.
