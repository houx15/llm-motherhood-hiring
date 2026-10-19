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
  token mother's résumé-FE-adjusted top-3 rate falls to 25–78% of an identical childless
  woman's rate; (2) no fatherhood bonus in any model — fathers are always below parity —
  though only Claude Haiku 5.5 penalizes mothers significantly *more* than fathers
  (surviving Holm correction in two of three contrasts);
  (3) a caregiving leave gap is always the most damaging cue; (4) motherhood salary
  penalties cluster in a narrow band (−1.7% to −2.3% versus the same woman shown
  childless in the same pairwise comparison), roughly
  one-quarter of the human laboratory benchmark (≈ −$11,000 ≈ −7.4%); and (5) Claude
  Haiku 5.5 responds to pregnancy disclosure by withholding salary offers entirely
  (19.8% of pregnant applicants receive $0) — and those withheld applicants are advanced
  to interview only 30% of the time, producing a net within-résumé interview penalty of
  −9.4pp (pregnant minus childless women, same résumés; t = −4.8) with no residual
  salary penalty once withheld offers are excluded.
  Under clustered difference-in-differences inference, greedy job-ad wording amplifies
  the leave-gap interview penalty for DeepSeek (and, combined with family-friendly
  language, for Haiku); EEO boilerplate and family-friendly sentences alone show no
  reliable effects. LLM hiring tools reproduce a gender-generalized form of the
  motherhood penalty that is invisible in individual scores but systematic in
  comparative decisions — and add a new margin, abstention.
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
  pass (logged, costed, `repair_of`-linked) recovered 2,902 of the 3,062 invalid
  responses across all experiments.
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

**The pregnancy result is an abstention phenomenon with a real interview cost — not a
salary cut.** Claude Haiku 5.5 returns `starting_salary_usd: 0` — a withheld offer —
for 19.8% of pregnant applicants (vs 3.1% of childless women; married 7.3%;
Figure 6), with rationales that explicitly cite protected characteristics. The earlier
draft treated those zeros as $0 offers (a spurious −$18.7k "salary cut"). Corrected
within-résumé estimates (résumé FE, clustered SEs; Tables 5–6, generated from
`stats.json`):

**Table 5. Pregnancy within-résumé gaps (résumé FE, clustered SE).**

| Outcome | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| Interview (pp) | +1.9 (t 1.8) | **−9.4 (t −4.8)*** | +0.8 (t 1.5) | +0.7 (t 0.9) |
| Fit (1–10) | −0.1 (t −2.2) | −0.1 (t −0.7) | +0.0 (t 1.0) | +0.1 (t 2.6) |
| Salary (excl. withheld) | −$705 (−0.8%) | −$693 (−0.8%) | +$515 (+0.6%) | −$115 (−0.1%) |

**Table 6. Salary withholding ($0) and interview denial, E1 women.**

| Model | Withheld: none / married / pregnant | Interview rate when withheld (pregnant) | when offered (pregnant) |
| --- | --- | --- | --- |
| DeepSeek | 1.6% / 2.2% / 2.0% | .000 (n=24) | .958 (n=1176) |
| Haiku | 3.1% / 7.3% / **19.8%** | **.299 (n=234)** | 1.000 (n=947) |
| Luna | 0.9% / 1.3% / 3.1% | .000 (n=37) | .953 (n=1163) |
| Qwen | 4.2% / 4.2% / 5.8% | .000 (n=70) | .970 (n=1130) |

Three facts discipline the interpretation. (i) Once withholding is excluded, *no*
model shows a meaningful pregnancy salary penalty (−0.8% at most). (ii) Abstention is
not benign: Haiku advances a withheld pregnant applicant to interview only 30% of the
time, so the withholding mass produces the −9.4pp net interview penalty — roughly what
19.8% × 70% denial would deliver. (iii) The other models almost never withhold (≤5.8%)
and show no pregnancy interview gaps. The rationales express protective intent
("salary should not depend on pregnancy"), but the downstream result is that one in
five pregnant applicants gets neither a price nor an interview. We treat withholding
as an outcome distinct from scoring: zeros are excluded from all salary analyses in
all models, and §6.5 notes that Haiku's pregnant-cell *scored* outcomes condition on
non-abstention.

## 5.3 E2 — paired comparison: robust penalties; one model genders them

Figure 2 shows P(parent chosen) with pair-clustered 95% CIs; Tables 1–2 are
generated programmatically from `stats.json` (see `docs/report/tables.md`).

**Table 1. E2 probability the parent candidate is chosen (mean of 40 résumé-pair
cluster means; t vs 0.5, df 39).**

| Contrast | DeepSeek F / M | Haiku F / M | Luna F / M | Qwen F / M |
| --- | --- | --- | --- | --- |
| Parent (PTA) | .357 (−11) / .349 (−10) | .233 (−12) / .276 (−10) | .297 (−8) / .294 (−8) | .387 (−6) / .398 (−5) |
| Parent + committed | .419 (−8) / .411 (−8) | .266 (−10) / .331 (−9) | .228 (−9) / .246 (−8) | .407 (−6) / .430 (−5) |
| Parent + leave gap | .310 (−12) / .308 (−13) | .110 (−19) / .130 (−17) | .186 (−8) / .184 (−8) | .230 (−11) / .256 (−11) |

(a) **Every cell is far below parity** (all |t| ≥ 5 with 39 df). (b) **The leave gap
is always the worst cue**, and objective commitment evidence never restores parity —
for GPT-6 Luna it *deepens* the penalty (.228 vs .297 for mothers), the cleanest
normative-discrimination signature (H6). (c) **No fatherhood bonus in any cell.**
The mother-father difference itself (Table 2) is significant only for Haiku — and,
nominally, Qwen:

**Table 2. E2 mother-minus-father differences (pair-matched t-tests; Holm over 12
tests; \*\* survives Holm, \* raw p < .05 only).**

| Contrast | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| Parent (PTA) | +.008 (t 0.8) | **−.043 (t −3.1; Holm p=.037)\*\*** | −.004 (−0.6) | −.011 (−1.3) |
| Committed | +.008 (1.2) | **−.065 (t −4.6; Holm p=.001)\*\*** | −.018 (−1.8) | −.023 (−2.6; Holm p=.121)\* |
| Leave gap | +.002 (0.2) | −.020 (−2.1; Holm p=.332)\* | +.002 (0.3) | −.026 (−2.8; Holm p=.075)\* |

Corrected claim: *no model shows a fatherhood bonus; Haiku's mother-heavier penalty
survives Holm correction for the parent and committed contrasts (not the leave gap);
Qwen's nominal mother-heavier differences do not survive correction.*

Paired salary differences — the mother's recommended salary minus that of the
childless woman she is paired against (same occupation, same gender, same call) —
are −1.7% to −2.3% across models for the parent cue (leave gap −1.2% to −4.1%).
**Pooled across models, mothers with the plain parent cue are chosen 33.7% of the
time in head-to-head pairs against an otherwise-identical childless woman (parity
= 50%; −16.3pp); with a leave gap, 23.2% (−26.8pp).** Every model penalizes; the
magnitude varies substantially by model
(I² = 91–95%), from −11pp (Qwen) to −27pp (Haiku) for the parent cue.

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
DeepSeek (.71 mothers / .70 fathers) and Qwen mothers (.75) remain below it; Qwen
fathers (.798) sit at the line; Luna straddles it (.78 mothers / .81 fathers). The
honest statement is: *token parents are ranked significantly below the same résumés
shown childless in every model (|t| ≥ 2.8), with adjusted impact ratios of 0.70–0.81
for three models and 0.23–0.25 for Haiku — a decisive four-fifths violation for
Haiku, violations for DeepSeek (both genders) and Qwen mothers, and borderline
results for Qwen fathers and Luna.* In mixed 3+3 pools the résumé-FE parent effect is small but still
negative (−0.04 to −0.15), so we find no evidence of the earlier-draft "parents
favored in mixed pools" reversal. Composition-d results are confounded (§4.4) and
unreported.

## 5.5 E4 — job-ad wording effects under clustered inference

Table 4 reports résumé-fixed-effects estimates with SEs clustered by résumé (32
clusters): the base leave-gap penalty, and the difference-in-differences of each
variant against base (generated from `stats.json`).

**Table 4. E4 leave-gap interview penalty (pp; résumé-FE DiD vs base;
\* raw p<.05, \*\* p<.01).**

| | DeepSeek F / M | Haiku F / M | Luna F / M | Qwen F / M |
| --- | --- | --- | --- | --- |
| Base (gap) | −0.6 (−1.4) / +0.2 (0.3) | +0.8 (1.0) / +0.2 (0.2) | −0.0 / −0.0 | +0.4 (1.4) / −0.0 |
| EEO (DiD) | +1.5 (1.5) / +0.0 | −1.3 (−1.7) / +0.8 | −0.4 / −0.0 | −1.0 (−0.7) / −0.4 |
| Family-friendly (DiD) | −0.8 (−0.6) / −1.5 (−1.2) | −2.1 (−1.4) / −1.1 (−0.6) | −1.0 / −0.6 | −1.9 (−1.5) / −0.4 |
| Greedy (DiD) | **−2.7 (−2.3)\*** / −1.9 (−1.1) | −4.0 (−1.9) / −2.9 (−1.1) | −0.8 / −0.8 | −2.1 (−2.1)\* / −1.0 (−0.5) |
| Greedy + family-friendly (DiD) | **−5.2 (−2.9)\*\*** / **−6.0 (−2.2)\*** | **−8.0 (−2.8)\*\*** / −6.2 (−1.7) | −0.2 / −0.8 | −1.2 (−1.4) / −3.1 (−2.0) |

What survives clustered inference: **greedy wording adds a significant extra
interview penalty for leave-gap mothers under DeepSeek (−2.7pp DiD, t = −2.3) and
Qwen (−2.1pp, t = −2.1, marginal)**, and combining greedy with family-friendly
wording adds significant penalties for DeepSeek (both genders) and Haiku mothers
(−8.0pp, t = −2.8). Several claims from earlier drafts do *not* survive: Haiku's
greedy-only DiD (−4.0) is not significant at this cluster count (t = −1.9); the
small family-friendly-alone effects (−0.4 to −2.1) are all insignificant; "mothers
pay double" holds only in DeepSeek's greedy-only cell (and neither gender's estimate
is individually significant there for fathers); under greedy+FF, DeepSeek's penalty
is the same for both genders and Qwen's is larger for fathers. EEO boilerplate never
does anything. The defensible summary: *point estimates consistently point in the
greedy-hurts direction for leave-gap mothers, statistically confirmed for two models;
family-friendly and EEO sentences show no reliable repair effect anywhere.*

## 5.6 Occupational moderation (H3/H4): not supported in scoring

Re-run with withheld ($0) salaries excluded, the pooled E1 regressions find small,
non-significant interaction terms of the family gap with female share, median wage,
and time demands in every model (largest main-effect-level term: DeepSeek's
leave-gap gender gap in salary, −$779 at the occupation-mean Z, p = .008 — a
conditional main effect, not an interaction; all Z-interactions have p ≥ .2).
Résumé fixed effects absorb occupation *main* effects but not these interactions,
so the correct reading is simply that the interactions are near zero: occupational
moderation of the motherhood penalty is not detectable in scoring tasks at this
sample size. The E4 experiment (§5.5) shows the greedy-*signal* mechanism is real
within occupation for two models; the cross-occupation gradient is not where it
operates.

## 5.7 Benchmark: LLMs are milder than the human laboratory, not harsher

Correll et al. (2007)'s lab study recommended hiring **84% of childless women versus
47% of mothers** (−37pp) and offered non-mothers roughly **$11,000 more (≈ 7.4% of
the childless offer — the commonly cited figure; verify against the paper's tables
before journal submission)**; their employer audit found childless women received
about twice the callbacks. Our pooled LLM choice penalty for mothers — P(mother
chosen) in head-to-head pairs against an otherwise-identical childless woman,
relative to 50% parity (−16.3pp parent
cue; −26.8pp leave gap) — is **smaller than the human hiring gap** (mothers minus
childless women, between-persons), and the LLM salary
band (−1.7% to −2.3%, mother minus her paired childless woman) is roughly one-quarter
of the human salary penalty (Figure 7).
Caveat: the LLM figure is a within-pair *choice share* while the human figure is a
between-persons *hire rate* — directionally comparable, not metrically; we drop any
standardized commitment comparison (paired d_z is not comparable to Correll's
between-persons d). Classification: on pay and hiring margins, these LLMs **reduce**
the human motherhood penalty; they do not amplify it — with the exceptions of
shortlist *composition* effects (E3) and Haiku's abstentions, which have no clean
human analogue.

## 5.8 Model-specific signatures

- **Claude Haiku 5.5** — severity and abstention outlier: largest choice penalties
  (leave-gap mothers .110), lowest adjusted impact ratio (.25), the only refuser
  (0.5%), the only large-scale salary-withholder (19.8% of pregnant applicants; 7.3%
  married) — and abstention carries an interview denial (30% interview rate when
  withheld), netting a −9.4pp pregnancy interview penalty. It is also the only model
  with a second-position preference and the only one whose mother-father gap survives
  Holm correction (parent, committed). Interestingly, its *fit ratings* show no
  penalty for parents versus childless candidates in E1 (+0.15 points, parent minus
  none) — its discrimination appears only in choices,
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
strict-validity bounds (excluding the 2,621 E2 calls whose valid response came from
any repair attempt): P(parent chosen)
.391/.398 (parent) and .214/.240 (leave gap) — within ±0.02 of the repaired
estimates; no conclusion changes. (iii) Excluding the two low-quality lawyer résumés
(§6.4) moves E2 means by <0.02. (iv) Salary-withholding exclusion is applied to all
models; Haiku's E4 salary gaps are reported as upper bounds.

**6.4 Materials quality.** Two Kaggle-derived résumés (`lawyer_00` mean fit 2.3,
`lawyer_01` 2.9) describe legal assistants without law degrees — these candidates
fail regardless of condition. Two further résumés are weak rather than failing
(`registered_nurse_01` mean fit 4.6, `medical_assistant_01` 4.5). Because conditions
rotate within résumé, estimates are unbiased, but weak cells compress sensitivity.
Sensitivity analyses excluding the fit<4 pair, and separately the full named set of
four, are materially identical for E2 (e.g., Haiku leave-gap mothers .110 → .107 →
.097) and E3 ratios (±.02); licensed-occupation résumés are flagged for regeneration
in future runs.

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
amplified by greedy job ads for two models under clustered inference, untouched by
EEO boilerplate — and joined by a new behavior humans did not exhibit in the
benchmark literature: withholding the offer entirely for one in five pregnant
applicants and advancing them to interview only 30% of the time. Models do not
simply inherit human biases; they redistribute them across tasks, margins, and
vendors. Auditing regulation that stops at single-résumé scoring will not see any
of it.

# Reproducibility

Pinned slugs, frozen materials, deterministic plans, append-only logs with per-call
costs, and analysis code are in the repository; total spend $40.04 against a $200
cap. All statistics regenerate via `uv run audit stats` (code:
`src/audit/analysis/report_stats.py`; outputs `docs/report/stats.json` and the
programmatically generated `docs/report/tables.md`); figures via `uv run audit
figures`. Per-model reports:
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
