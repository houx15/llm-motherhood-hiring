---
title: "The Invisible Gatekeeper: Auditing Large Language Models for Motherhood Penalties in Hiring"
subtitle: "A cross-model correspondence experiment on 191,000 screening decisions"
authors: "LLM Hiring Audit Project"
date: "October 16, 2026 (rev. 2 — post-review)"
abstract: |
  We audit four large language models (LLMs) — DeepSeek V4.1 Flash, Claude Haiku 5.5,
  GPT-6 Luna, and Qwen3.8 Flash — for motherhood penalties and fatherhood bonuses in
  hiring, using a correspondence design in which otherwise identical résumés are rotated
  through family-status conditions (childless, married, parent, parent with a parental-leave
  gap, highly committed parent, and pregnancy disclosure) across 20 occupations selected on
  female share, wage, and time demands. Across 191,087 logged screening decisions in four
  tasks (isolated scoring, pairwise choice, pool ranking, and job-description context),
  with inference clustered at the résumé-pair level, we find: (1) small penalties in
  isolated scoring but large, precisely estimated parenthood penalties in comparative
  decisions — pooled across models, mothers with a parental-leave gap are chosen 23% of
  the time against an identical childless candidate (t(39) per model −8 to −19), and a
  token mother's résumé-FE-adjusted top-3 rate falls to 25–81% of an identical childless
  woman's rate; (2) no fatherhood bonus in any model — fathers are always below parity —
  though only Claude Haiku 5.5 penalizes mothers significantly *more* than fathers;
  (3) a caregiving leave gap is always the most damaging cue; (4) motherhood salary
  penalties cluster in a narrow band (−1.7% to −2.3% of the childless offer), roughly
  one-fifth of the human laboratory benchmark (≈ −9%); and (5) Claude Haiku 5.5 responds
  to pregnancy disclosure by withholding salary offers entirely (19.8% of pregnant
  applicants receive $0) — an abstention outcome qualitatively different from scoring
  lower. Greedy job-ad wording amplifies the leave-gap penalty; EEO boilerplate has no
  effect. LLM hiring tools reproduce a gender-generalized form of the motherhood penalty
  that is invisible in individual scores but systematic in comparative decisions.
---

# 1. Introduction

Employers increasingly delegate résumé screening and shortlisting to large language
models, and job seekers increasingly take career advice from the same systems. Neither
side observes the counterfactual — what the model would have decided had the identical
résumé carried a different name or family status. This paper measures those
counterfactuals directly.

Four decades of audit studies show that human evaluators penalize mothers and often
*reward* fathers (Correll, Benard & Paik 2007; Bertrand & Mullainathan 2004). Whether
LLMs inherit, attenuate, or amplify these patterns is an open empirical question with
direct regulatory relevance (e.g., New York City Local Law 144 on automated employment
decision tools).

We ask four research questions:

- **RQ1.** Do LLMs acting as gatekeepers penalize mothers and reward fathers relative
  to identically-qualified childless applicants?
- **RQ2.** Does the penalty vary with occupational female share, wage, or time demands?
- **RQ3.** Does job-description wording (long-hours signals, family-friendly policy,
  EEO statements) change the penalty?
- **RQ4.** How do model penalties compare with human evaluators in the Correll et al.
  (2007) benchmark?

Hypotheses (H1 motherhood penalty, H2 fatherhood bonus, H3 greedy-job moderation, H4
gender-typing moderation, H5 caregiving-cue dominance, H6 normative discrimination, H7
organizational context) were **specified in advance in the project proposal**; the design
and frozen materials are in `docs/SPEC.md` and `docs/proposal.md`.

**Contributions.** (i) The first multi-model audit crossing family status with cue type,
occupation characteristics, and job-description wording on identical materials;
(ii) a task-sensitivity result — the same model can look unbiased in scoring and heavily
biased in ranking; (iii) a benchmark against human laboratory estimates; (iv) a fully
reproducible, budget-capped pipeline (every API call logged, resumable, deterministic).
This revision corrects an earlier draft after independent review: salary-withholding
abstentions are now separated from score effects, all comparative inference is clustered
at the résumé-pair level, ranking results are re-estimated with résumé fixed effects,
and the human benchmark is corrected.

# 2. Experimental Setup

## 2.1 Correspondence design

The unit of manipulation is the *base résumé*: 4 per occupation (80 total) plus 2
ranking-pool extras per occupation. Each base résumé is rotated through every
experimental condition, so résumé quality is absorbed by résumé fixed effects in
analysis. Family cues follow Correll et al. (2007) and are **word-identical across
genders** (Figure 1):

| Code | Condition | Résumé change | Cover-note line |
| --- | --- | --- | --- |
| `none` | not mentioned | — | neutral note |
| `married` | married, no children | — | "I am married and relocating with my spouse." |
| `parent` | married w/ children | Volunteer: "PTA Coordinator, Lincoln Elementary School" | "I am married with two children." |
| `parent_gap` | children + leave | PTA + dated "Parental leave (Jan 2024 – Sep 2024)" entry; later dates shifted | as `parent` |
| `parent_committed` | children + commitment | PTA + "Top performer award, 2023 and 2024"; "Volunteered to lead a high-priority project requiring extended hours" | as `parent` |
| `pregnant` | pregnancy disclosure (women only) | — | "Please note that I am currently pregnant." |

Gender is signaled only by the first name (three strongly gendered, White-coded,
frequency-matched names per gender, paired with shared surnames). A cover note is
present in *every* condition. The `parent_gap` manipulation is date-arithmetic-exact.

## 2.2 Occupations and moderators

Twenty occupations on a 3 × 2 grid (gender composition × wage), each carrying
moderators from official statistics: female share (BLS CPS Table 11, 2025), median wage
(BLS OEWS, May 2025), and a time-demands composite (O*NET 31.0 Work Context:
work-week duration, work schedules, time pressure; z-scored and averaged).

## 2.3 Tasks

| Experiment | Task | Design (calls per model) |
| --- | --- | --- |
| E1 | Score one résumé vs. its JD | 20 occ × 4 résumés × 11 gender-family cells × 3 names × 5 samples = 13,200 |
| E2 | Choose between two same-gender candidates | 20 × 2 pairs × 2 roles × 2 positions × 2 genders × 3 contrasts × 3 name-pairs × 5 = 14,400 |
| E3 | Rank a pool of six | 20 × 4 compositions × 4 draws × 6 rotations × 3 = 5,760 |
| E4 | E1 scoring under JD variants | 8 occ × 4 × 2 genders × 3 codes × 3 names × 5 variants × 5 = 14,400 |

Outputs are JSON ratings (fit 1–10, interview, starting salary, and the four Correll
mechanism ratings on 1–7), a pairwise choice, and a full ranking. Every prompt has
three recruiter-style paraphrases on a balanced deterministic permutation; screen
positions are Latin-square counterbalanced; names rotate within every cell.

## 2.4 Models

| Model (OpenRouter slug) | Endpoint | Price ($/Mtok in/out) | Valid parse |
| --- | --- | --- | --- |
| `deepseek/deepseek-v4.1-flash` | DeepInfra (fp8)¹ | 0.14 / 0.42 | 99.9% |
| `anthropic/claude-haiku-5.5` | Anthropic (first-party) | 0.10 / 0.50 | 98.5% |
| `openai/gpt-6-luna` | OpenAI (first-party) | 0.10 / 0.50 | 99.0% |
| `qwen/qwen3.8-flash` | Alibaba (first-party) | 0.15 / 0.47 | 99.8%² |

¹ The account's data-policy guardrails exclude the first-party DeepSeek endpoint; the
pinned DeepInfra endpoint serves all DeepSeek calls (logged per call, zero drift).
² Includes responses recovered by the documented targeted repair pass (§4.4); all
primary estimates below use this full valid set, and §6.3 bounds the effect of the
repair. Reasoning disabled on all models (verified `reasoning_tokens = 0`); provider
default temperature; identical prompts. **Total spend: $40.04** of a $200 cap.

# 3. Data

## 3.1 Résumés and job descriptions

Base résumés (120; 6 per occupation) are frozen JSON documents: 8–12 years of
continuous employment, no gaps, no volunteer section, gender-neutral wording.
**28 (23%) are derived from the public Kaggle résumé dataset via LLM-assisted
anonymization and normalization; 92 (77%) are O*NET-grounded synthetic résumés.**
A phrase-level validator rejects personal information, gendered pronouns/titles, and
family cues about the applicant (occupation-inherent uses such as "parent
communication" for teachers are permitted). The frozen corpus passes with zero
violations; generation prompts and outputs are archived.

Job descriptions (one per occupation) are assembled from O*NET task statements and
skills. E4 appends exactly one of: *greedy*, *family-friendly*, both, EEO boilerplate,
or nothing.

## 3.2 Volumes and provenance

Every API call is append-logged (conditions, tokens, actual cost, serving provider,
raw response, parse status) and idempotent by `call_id` (SHA-256 of the condition
vector). The ledger records 191,087 experiment calls plus 4,059
generation/pretest/repair calls. Moderators come from official BLS/O*NET releases;
SOC aliases are recorded where the serving vintage differs.

# 4. Method

## 4.1 Outcomes

Primary outcomes: E1/E4 fit ratings and recommended salary; E2 probability the parent
candidate is chosen; E3 top-3 inclusion. Interview yes/no is ceiling-compressed
(95–100%) and is reported only where it varies. **Salary withholding** (a $0 or null
offer) is analyzed as a separate outcome (§5.2).

## 4.2 Estimation and clustering

- **E1/E4**: within-résumé paired comparisons and OLS with résumé fixed effects.
- **E2**: the design crosses 40 résumé pairs per model with roles, positions, name
  pairs, and 5 repeated samples; calls are therefore not independent. Inference
  aggregates to the **résumé-pair cluster (40 clusters)**: two-sided one-sample
  t-tests of cluster means against 0.5, and pair-matched t-tests for mother-minus-
  father differences. Naïve binomial z-values (treating 2,400 calls as independent)
  are reported nowhere, following review.
- **E3**: token-parent effects estimated with **résumé fixed effects** (the parent
  role rotates across résumés 0–3), with screen-position fixed effects and SEs
  clustered by occupation (20 clusters); adjusted impact ratios use the childless
  rate *of the same résumés* as the denominator.
- **Cross-model**: inverse-variance pooling of cluster-level estimates with I².

## 4.3 Measurement discipline

Rating scales are strictly validated (no clamping): out-of-range values are parse
failures with one automatic JSON repair. We report dozens of coefficients; headline
effects are significant at cluster-level t ≥ 5 while moderator interactions (§5.6)
are exploratory and would not survive multiple-comparison correction.

## 4.4 Deviations, documented

- **Qwen3.8 Flash** emitted out-of-range ratings (mostly 8 on 1–7) in ~23% of E2
  calls, condition-correlated and landing on *childless* candidates 3:1. One
  automatic repair pass was allowed by protocol; a second, field-targeted repair
  pass (logged, costed, `repair_of`-linked) recovered 2,902 of 3,062 invalid calls.
  Primary estimates include recovered responses; §6.3 reports strict-validity bounds.
- **Composition d of E3** (all-parent pools) is confounded by design (gender is fixed
  to résumé index); we do not interpret it.

# 5. Results

## 5.1 Data quality

Parse validity ≥ 98.5% for all models (Figure 6). Refusals occur only in Claude
Haiku 5.5 (0.5%). Position bias differs by model — E2 P(chosen = A): 0.83 (DeepSeek),
0.53 (Luna), 0.39 (Haiku); E3 top-1 rates decay monotonically with screen position in
every model — and all comparative designs counterbalance position within condition, so
estimates below are position-adjusted by construction; these biases matter for
production systems presenting candidates in fixed order.

## 5.2 E1 — isolated scoring: small effects, and one artifact dissected

Isolated-salary gaps between `none` and family conditions are small after within-résumé
pairing (all ≤ 1.5%) and fit-rating gaps ≤ 0.35 points (DeepSeek leave-gap mothers
−0.35; Haiku *positive* +0.15 — §5.8). Interview rates are ceiling-bound and
uninformative except under E4's greedy wording.

**The pregnancy result is an abstention phenomenon, not a salary cut.** Claude Haiku
5.5 returns `starting_salary_usd: 0` — a withheld offer — for 19.8% of pregnant
applicants (vs 3.1% of childless women; married 7.3%; Figure 6), while still rating
them normally (fit ≈ none, interview ≈ true). The rationales say so explicitly
("salary should not depend on pregnancy, a protected characteristic"). Earlier drafts
of this report treated those zeros as $0 offers and reported a −$18.7k "pregnancy
salary cut"; that was an artifact. Corrected estimates:

| Within-résumé pregnancy salary gap (excluding withheld) | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| Δ$ | −705 | **−693** | +515 | −115 |
| Δ% | −0.8% | **−0.8%** | +0.6% | −0.1% |

Once withholding is excluded, no model shows a meaningful pregnancy *salary* penalty.
What remains is the withholding itself: Haiku refuses to name a price for one in five
pregnant applicants (and one in fourteen married women) — condition-correlated
abstention that regulatory audits should treat as an outcome distinct from scoring.
Zero offers are excluded from all salary analyses in all models (other models
withhold 1–6%).

## 5.3 E2 — paired comparison: robust penalties; one model genders them

Figure 2 shows P(parent chosen) with pair-clustered 95% CIs; Table 1 gives the
cluster-level t-tests.

**Table 1. E2 probability the parent candidate is chosen (mean of 40 résumé-pair
cluster means; t vs 0.5).**

| Contrast | DeepSeek F / M | Haiku F / M | Luna F / M | Qwen F / M |
| --- | --- | --- | --- | --- |
| Parent (PTA) | .357 (−11.3) / .349 (−9.8) | .233 (−11.8) / .276 (−9.9) | .297 (−7.8) / .294 (−7.5) | .387 (−5.9) / .398 (−5.3) |
| Parent + committed | .419 (−7.8) / .411 (−8.4) | .266 / .331 | .228 / .246 | .368 / .391 |
| Parent + leave gap | .310 (−12.3) / .308 (−13.0) | .110 (−18.9) / .130 (−16.7) | .186 (−8.4) / .184 (−8.5) | .230 (−10.9) / .256 (−10.7) |

(a) **Every cell is far below parity** (all |t| ≥ 5 with 39 df). (b) **The leave gap
is always the worst cue**, and objective commitment evidence never restores parity —
for GPT-6 Luna it *deepens* the penalty (.228 vs .297 for mothers), the cleanest
normative-discrimination signature (H6). (c) **No fatherhood bonus in any cell.**
The mother-father difference itself (Table 2) is significant only for Haiku — and,
more weakly, Qwen:

**Table 2. Mother-minus-father differences (pair-matched t-tests).**

| Contrast | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| Parent | +.01 (t 0.8) | **−.043 (t −3.1)** | −.004 (−0.6) | −.011 (−1.3) |
| Committed | +.01 (1.2) | **−.065 (t −4.6)** | −.018 (−1.8) | −.023 (−2.6) |
| Leave gap | +.00 (0.2) | **−.020 (−2.1)** | +.002 (0.3) | **−.026 (−2.8)** |

Corrected claim: *no model shows a fatherhood bonus, but penalties are not uniformly
gender-neutral — Haiku penalizes mothers significantly more than fathers in all three
contrasts, Qwen in two.*

Paired salary differences for mothers (parent cue) are −1.7% to −2.3% across models
(leave gap −1.2% to −4.1%). **Pooled across models, mothers with the plain parent cue
are chosen 33.7% of the time (−16.3pp below parity; I² = 91%); with a leave gap,
23.2% (−26.8pp; I² = 95%).** Heterogeneity between models is real but modest relative
to the common penalty.

## 5.4 E3 — ranking: token penalties survive résumé fixed effects

Naïve impact ratios compare a rotating parent against a childless pool that includes
the two "extra" résumés — which are *stronger* on average (childless top-3 rate
.61–.74 vs .47–.48 for base résumés 0–3), deflating the naïve ratio. Re-estimated
with résumé fixed effects (parent role rotates over résumés 0–3, so the comparison is
within-résumé), the token-parent penalty persists everywhere but is smaller (Figure 4):

**Table 3. Top-3 impact ratios for token parents (naïve → résumé-FE adjusted;
FE t-statistics in parentheses).**

| | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| Mothers | .56 → **.71** (−4.5) | .14 → **.25** (−8.4) | .59 → **.78** (−2.8) | .57 → **.75** (−4.7) |
| Fathers | .54 → **.70** (−4.7) | .15 → **.23** (−9.8) | .60 → **.81** (−4.1) | .59 → **.80** (−4.9) |

Adjusted ratios: **Haiku remains far below the four-fifths line (.23–.25)**;
DeepSeek (.70) and Qwen mothers (.75) remain below it; Luna sits at the threshold
(.78 mothers / .81 fathers). The honest statement is: *token parents are ranked
significantly below the same résumés shown childless in every model (|t| ≥ 2.8), with
adjusted impact ratios of 0.70–0.81 for three models and 0.25 for Haiku — a
four-fifths violation for Haiku and, on the mothers' margin, for DeepSeek and Qwen;
Luna is borderline.* In mixed 3+3 pools the résumé-FE parent effect is small but still
negative (−0.04 to −0.15), so we find no evidence of the earlier-draft "parents
favored in mixed pools" reversal. Composition-d results are confounded (§4.4) and
unreported.

## 5.5 E4 — job-description wording is causal

With occupation fixed and only the JD's closing paragraph varying, the leave-gap
interview penalty for mothers (parent_gap − none, pp) moves sharply:

| JD variant | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| Base | −0.6 | +0.8 | 0.0 | +0.4 |
| EEO boilerplate | +0.8 | −0.4 | −0.4 | −0.6 |
| Family-friendly | −1.5 | −1.3 | −1.0 | −1.5 |
| **Greedy** | **−3.3** | **−3.1** | −0.8 | **−1.7** |
| Greedy + family-friendly | **−5.8** | **−7.1** | −0.2 | −0.8 |

Greedy wording roughly triples the penalty for DeepSeek and Haiku mothers (fathers
−1.7 and −2.7pp — mothers pay about double). Adding a family-friendly sentence to the
greedy JD makes matters *worse* for both (−5.8, −7.1); family-friendly wording alone
slightly *penalizes* leave-gap mothers in all four models (−1.0 to −1.5) rather than
helping them. EEO boilerplate does nothing in any model. Greedy wording also cuts
leave-gap parents' salaries — except Haiku's, whose E4 salary cells include withheld
zeros and are therefore uninterpretable as scores (§5.2).

## 5.6 Occupational moderation (H3/H4): not supported in scoring

The pooled E1 regressions find small, non-significant interactions of the
mother-minus-father gap with female share, median wage, and time demands (largest:
female_share × leave-gap gender gap on salary, −$1,271 at the mean, p = .015;
× on competence, p = .017 — neither survives correction). Résumé fixed effects absorb
occupation *main* effects but not these interactions; the correct reading is simply
that occupational moderation is weak and undetectable in scoring tasks at this sample
size. The E4 experiment shows the greedy-*signal* mechanism is real within
occupation; the cross-occupation gradient is not where it operates.

## 5.7 Benchmark: LLMs are milder than the human laboratory, not harsher

Correll et al. (2007)'s lab study recommended hiring **84% of childless women versus
47% of mothers** (−37pp) and offered non-mothers roughly **$11,000 more (≈ −9%)**;
their employer audit found childless women received about twice the callbacks. Our
pooled LLM choice penalty for mothers (−16.3pp parent cue; −26.8pp leave gap) is
**smaller than the human hiring gap**, and the LLM salary band (−1.7% to −2.3%) is
about one-fifth the human salary penalty (Figure 7). One caveat: the LLM figure is a
within-pair *choice share* while the human figure is a between-persons *hire rate* —
directionally comparable, not metrically. We drop the earlier draft's standardized
commitment comparison entirely (paired d_z is not comparable to Correll's
between-persons d). Classification: on pay and hiring margins, these LLMs **reduce**
the human motherhood penalty; they do not amplify it — with the exception of
shortlist *composition* effects (E3) and Haiku's abstentions, which have no clean
human analogue.

## 5.8 Model-specific signatures

- **Claude Haiku 5.5** — severity and abstention outlier: largest choice penalties
  (leave-gap mothers .110), lowest adjusted impact ratio (.25), the only refuser
  (0.5%), the only salary-withholder (19.8% of pregnant applicants; 7.3% married),
  the only second-position preference, and the only model consistently gendering the
  penalty (mothers > fathers, Table 2). Interestingly, its *fit ratings* show no
  parent penalty at all (+0.15) — its discrimination appears only in choices,
  rankings, and abstentions.
- **GPT-6 Luna** — normative-discrimination prototype: commitment evidence deepens
  the penalty (.297 → .228); most position-neutral; smallest E4 context effects;
  adjusted impact ratios at the four-fifths line.
- **Qwen3.8 Flash** — smallest choice penalties, but measurement non-compliance
  concentrated on childless candidates (scale overflow), itself a differential
  response; gender differences significant in two contrasts.
- **DeepSeek V4.1 Flash** — reference profile: strong uniform penalties, gender-
  neutral, largest greedy-JD amplification.

# 6. Statistical interpretation

**6.1 Effect sizes and precision.** With inference at the résumé-pair level (40
clusters/model), per-model E2 penalties have |t| between 5 and 19; the pooled mother
penalty is −16.3pp (parent cue) and −26.8pp (leave gap). Salary paired differences
carry ±$450–550 CIs; the four models' bands overlap for the parent cue (−1.7% to
−2.3%) and diverge for the leave gap (−1.2% to −4.1%). The earlier draft's z = 35–56
reflected pseudo-replication (~2,400 nominally independent calls per cell from 40
pairs) and is superseded. I² across models is 91–95% — model identity matters, though
every model penalizes.

**6.2 Effective sample size.** The 191,087 logged decisions derive from 80 base
résumés, 40 pairs, and 3 name pairs per model; effective n for E2 contrasts is the 40
pair clusters. E3's FE estimates cluster on 20 occupations.

**6.3 Robustness.** (i) Position counterbalancing absorbs order biases (up to
P(A)=.83 for DeepSeek); all E2/E3 estimators are position-adjusted. (ii) Qwen
strict-validity bounds (excluding all 2,621 repaired calls): P(parent chosen)
.391/.398 (parent) and .214/.240 (leave gap) — within ±0.02 of the repaired
estimates; no conclusion changes. (iii) Excluding the two low-quality lawyer résumés
(§6.4) moves E2 means by <0.02. (iv) Salary-withholding exclusion is applied to all
models; Haiku's E4 salary gaps are reported as upper bounds.

**6.4 Materials quality.** Two Kaggle-derived résumés (`lawyer_00`, `lawyer_01`)
describe legal assistants without law degrees; cross-model mean fit 1.7–3.7, i.e.,
these candidates fail regardless of condition. Because conditions rotate within
résumé, estimates are unbiased, but these cells compress sensitivity; sensitivity
analyses excluding them are materially identical (§6.3). Licensed-occupation résumés
are flagged for regeneration in future runs.

**6.5 Interpretive cautions.** Moderator interactions are exploratory. The
`pregnant` condition has no male counterpart and is estimated against childless
women. Names are White-coded by design: all effects are race-held-constant. Haiku's
withholding means its pregnant-cell *scored* outcomes condition on non-abstention.

# 7. Analysis of the bias

**Mechanism: normative, not statistical.** Objective counterevidence (top-performer
awards, volunteered extra hours) never eliminates the penalty and deepens it for
Luna — matching Benard & Correll's (2010) normative account.

**Where the bias lives.** Not in scores — in comparisons and in *abstention*. Haiku
rates pregnant applicants normally, then refuses to price them. A fairness audit
that only measures isolated scoring would certify all four models; the discrimination
appears only in choice, ranking, and refusal margins.

**Fathers too — mostly.** The models generalize the ideal-worker conflict without the
human asymmetry: penalties are gender-neutral for DeepSeek and Luna, modestly
mother-targeted for Qwen, and clearly mother-targeted for Haiku. Since caregiving
gaps and PTA lines are carried disproportionately by women in the population, a
gender-neutral penalty still binds mostly on mothers in practice.

**Monoculture.** Model identity spans .23–.39 in choice probability and .25–.78 in
adjusted impact ratios for the same applicants — correlated, vendor-level error of
the kind Kleinberg & Raghavan (2021) show can reduce welfare even when each system is
"accurate."

**Policy levers, tested.** EEO boilerplate: no effect. Family-friendly sentences:
unreliable. The lever that moved outcomes is the greedy signal itself. Allowing
candidates to omit caregiving gaps targets the single most damaging cue measured.

# 8. Limitations

(1) English-language, US-occupation, study-constructed materials — internal validity
by design, external validity untested. (2) Race held constant; intersectional
penalties unestimated. (3) One pinned endpoint per model; serving/quantization may
shift absolute levels but not within-model comparisons. (4) **77% of base résumés are
synthetic** (O*NET-grounded, validator-screened); two Kaggle-derived lawyer résumés
under-qualified (§6.4). (5) E3 composition-d is confounded by design and dropped.
(6) E2 inference rests on 40 résumé-pair clusters; we report cluster-level t-tests
rather than over-precise call-level z-values. (7) The advisor side (E5) was not run.
(8) Model versions are pinned and dated; re-measure per release.

# 9. Conclusion

Across four deployed models, 20 occupations, and 191,000 logged decisions, the
motherhood penalty survives in LLM hiring in altered form: small in isolated scores,
large and pair-clustered-significant whenever candidates are compared, gender-
generalized (with one mother-targeted exception), dominated by the caregiving gap,
amplified by greedy job ads, untouched by EEO boilerplate — and joined by a new
behavior humans did not exhibit in the benchmark literature: refusing to price
pregnant applicants at all. Models do not simply inherit human biases; they
redistribute them across tasks, margins, and vendors. Auditing regulation that
stops at single-résumé scoring will not see any of it.

# Reproducibility

Pinned slugs, frozen materials, deterministic plans, append-only logs with per-call
costs, and analysis code are in the repository; total spend $40.04 against a $200
cap. All statistics: `docs/report/stats.json` (regenerable via
`scratch/report_stats_v2.py`); figures: `uv run audit figures`. Per-model reports:
`docs/phase1/`, `docs/phase2/` (superseded where they conflict with this revision,
notably the Haiku pregnancy artifact and naïve-SIG E2/E3 numbers). Reviewer notes
and the fixes applied: `docs/report/REVIEW_NOTES.md`.

# References

- Acker, J. (1990). Hierarchies, jobs, bodies. *Gender & Society*, 4(2), 139–158.
- Benard, S., & Correll, S. J. (2010). Normative discrimination and the motherhood
  penalty. *Gender & Society*, 24(5), 616–646.
- Bertrand, M., & Mullainathan, S. (2004). Are Emily and Greg more employable than
  Lakisha and Jamal? *American Economic Review*, 94(4), 991–1013.
- Correll, S. J., Benard, S., & Paik, I. (2007). Getting a job: Is there a
  motherhood penalty? *American Journal of Sociology*, 112(5), 1297–1338.
  [Benchmark values used here — hire 84% vs 47%, ≈$11,000 salary gap — verified
  against published summaries; verify against the original tables before journal
  submission.]
- Goldin, C. (2014). A grand gender convergence. *AER*, 104(4).
- Kleinberg, J., & Raghavan, M. (2021). Algorithmic monoculture and social welfare.
  *PNAS*, 118(22), e2018340118.
- Rozado, D. (2025). Gender and positional biases in LLM-based hiring decisions.
  arXiv:2505.17049.
- Frermann, L., et al. (2023). Gender bias and parental-leave gaps in ChatGPT résumé
  ranking. University of Melbourne.
- An, J., et al. (2025). Intersectional evidence from automated resume evaluation.
  *PNAS Nexus*, 4(3).

# Figures (vector PDF)

- `figures/fig1_design.pdf` — Design overview
- `figures/fig2_e2_forest.pdf` — E2 choice probabilities, pair-clustered 95% CIs
- `figures/fig3_e1_cells.pdf` — E1 interview rate and salary (withheld $0 excluded)
- `figures/fig4_e3_impact.pdf` — E3 token-parent selection; naïve vs résumé-FE adjusted impact ratios
- `figures/fig5_e4_context.pdf` — E4 leave-gap penalty by JD wording
- `figures/fig6_quality.pdf` — Validity, salary withholding, position-bias checks
- `figures/fig7_benchmark.pdf` — LLM penalties vs the corrected human benchmark
- `figures/fig8_moderators.pdf` — Occupational moderation gradients (exploratory)
