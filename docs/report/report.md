---
title: "The Invisible Gatekeeper: Auditing Large Language Models for Motherhood Penalties in Hiring"
subtitle: "A cross-model correspondence experiment on 191,000 screening decisions"
authors: "LLM Hiring Audit Project"
date: "October 16, 2026"
abstract: |
  We audit four large language models (LLMs) — DeepSeek V4.1 Flash, Claude Haiku 5.5,
  GPT-6 Luna, and Qwen3.8 Flash — for motherhood penalties and fatherhood bonuses in
  hiring, using a correspondence design in which otherwise identical résumés are rotated
  through family-status conditions (childless, married, parent, parent with a parental-leave
  gap, highly committed parent, and pregnancy disclosure) across 20 occupations selected
  on female share, wage, and time demands. Across 191,087 logged screening decisions in
  four tasks (isolated scoring, pairwise choice, pool ranking, and job-description
  context), we find: (1) near-zero discrimination in isolated scoring but large
  parenthood penalties in comparative tasks — a token mother's top-3 shortlist rate falls
  to 14–59% of an identical childless woman's rate, violating the four-fifths rule in
  every model; (2) no fatherhood bonus in any model — fathers are penalized at rates
  statistically indistinguishable from mothers; (3) a caregiving leave gap is always the
  most damaging cue; (4) motherhood salary penalties cluster in a narrow band
  (−1.7% to −2.3% of the childless offer), roughly one-quarter of the classic human
  laboratory benchmark; and (5) greedy job-ad wording amplifies the leave-gap penalty up
  to three-fold while EEO boilerplate has no effect. We conclude that LLM hiring tools
  reproduce a gender-generalized form of the motherhood penalty that is invisible in
  individual scores but systematic in comparative decisions.
---

# 1. Introduction

Employers increasingly delegate résumé screening and shortlisting to large language
models, and job seekers increasingly take career advice from the same systems. Neither
side observes the counterfactual — what the model would have decided had the identical
résumé carried a different name or family status. This paper measures those
counterfactuals directly.

Four decades of audit studies in labor economics and sociology show that human
evaluators penalize mothers and often *reward* fathers (Correll, Benard & Paik 2007;
Bertrand & Mullainathan 2004). Whether LLMs inherit, attenuate, or amplify these
patterns is an open empirical question with direct regulatory relevance (e.g., New York
City Local Law 144 on automated employment decision tools).

We ask four research questions:

- **RQ1.** Do LLMs acting as gatekeepers penalize mothers and reward fathers relative
  to identically-qualified childless applicants?
- **RQ2.** Does the penalty vary with occupational female share, wage, or time demands?
- **RQ3.** Does job-description wording (long-hours signals, family-friendly policy,
  EEO statements) change the penalty?
- **RQ4.** How do model penalties compare with human evaluators in the Correll et al.
  (2007) benchmark?

Our preregistered hypotheses (H1 motherhood penalty, H2 fatherhood bonus, H3 greedy-job
moderation, H4 gender-typing moderation, H5 caregiving-cue dominance, H6 normative
discrimination, H7 organizational context) map onto these questions; the full
specification is in the project's `docs/SPEC.md` and `docs/proposal.md`.

**Contributions.** (i) The first multi-model audit that crosses family status with cue
type, occupation characteristics, and job-description wording on identical materials;
(ii) a task-sensitivity result — the same model can look unbiased in scoring and heavily
biased in ranking; (iii) a benchmark against human laboratory estimates; (iv) a fully
reproducible, budget-capped pipeline (every API call logged, resumable, deterministic)
that others can rerun on new models.

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

Gender is signaled only by the first name (three strongly gendered, racially
White-coded, frequency-matched names per gender: Emily/Sarah/Anne and Greg/Matthew/Todd,
paired with shared surnames). A cover note is present in *every* condition, so its
existence is constant. The `parent_gap` manipulation is date-arithmetic-exact: the
straddling job is split so no incidental gap is created.

## 2.2 Occupations and moderators

Twenty occupations on a 3 × 2 grid (gender composition × wage), each carrying three
continuous moderators from official statistics: female share of employment (BLS CPS
Table 11, 2025 annual averages), median annual wage (BLS OEWS, May 2025), and a time-
demands composite (O*NET 31.0 Work Context: duration of typical work week, work
schedules, time pressure; z-scored and averaged). Occupations span preschool teachers
(97% female, $38k, low time demands) to heavy-truck drivers (8% female, $59k, high
time demands).

## 2.3 Tasks

| Experiment | Task | Design (calls per model) |
| --- | --- | --- |
| E1 | Score one résumé vs. its JD | 20 occ × 4 résumés × 11 gender-family cells × 3 names × 5 samples = 13,200 |
| E2 | Choose between two same-gender candidates | 20 × 2 pairs × 2 roles × 2 positions × 2 genders × 3 contrasts × 3 name-pairs × 5 = 14,400 |
| E3 | Rank a pool of six | 20 × 4 compositions × 4 draws × 6 rotations × 3 = 5,760 |
| E4 | E1 scoring under JD variants | 8 occ × 4 × 2 genders × 3 codes × 3 names × 5 variants × 5 = 14,400 |

Outputs are JSON ratings (fit 1–10, interview yes/no, starting salary, and the four
Correll mechanism ratings competence/commitment/promotability/likability on 1–7), a
pairwise choice, and a full ranking. Every prompt has three recruiter-style
paraphrases, assigned by a balanced deterministic permutation; screen positions are
Latin-square counterbalanced; names rotate within every cell.

## 2.4 Models

| Model (OpenRouter slug) | Endpoint | Price ($/Mtok in/out) | Calls | Valid |
| --- | --- | --- | --- | --- |
| `deepseek/deepseek-v4.1-flash` | DeepInfra (fp8)¹ | 0.14 / 0.42 | 47,762 | 99.9% |
| `anthropic/claude-haiku-5.5` | Anthropic (first-party) | 0.10 / 0.50 | 47,760 | 98.5% |
| `openai/gpt-6-luna` | OpenAI (first-party) | 0.10 / 0.50 | 47,760 | 99.0% |
| `qwen/qwen3.8-flash` | Alibaba (first-party) | 0.15 / 0.47 | 47,805 | 99.8%² |

¹ The account's data-policy guardrails exclude the first-party DeepSeek endpoint; the
pinned DeepInfra endpoint serves all DeepSeek calls (logged per call, zero drift).
² After a documented targeted repair pass; see §4.4. All models ran with reasoning
disabled (verified `reasoning_tokens = 0`), provider default temperature, JSON mode,
identical prompts. Total spend: **$40.04** of a $200 cap.

# 3. Data

## 3.1 Résumés and job descriptions

Base résumés (120; 6 per occupation) are frozen JSON documents meeting strict
structural rules: 8–12 years of continuous employment, no gaps, no volunteer section,
gender-neutral wording. Sources: 28 are derived from the public Kaggle résumé dataset
(`snehaanbhawal/resume-dataset`) via LLM-assisted anonymization and normalization; 92
are O*NET-grounded synthetic résumés (top task statements + essential skills per SOC
code). A phrase-level validator rejects any draft containing personal information
(emails, phones, URLs, street addresses), gendered pronouns or titles, or
family/marital cues about the *applicant* (occupation-inherent uses such as "parent
communication" for teachers are permitted). The frozen corpus passes with zero
violations; generation prompts and outputs are archived.

Job descriptions (one per occupation, ~150–250 words) are assembled from O*NET task
statements and essential skills. E4 appends exactly one of five sentences/paragraphs:
*greedy* ("after hours and on weekends… travel up to 40%"), *family-friendly*
("16 weeks of paid parental leave… flexible hours… hybrid"), both, EEO boilerplate,
or nothing.

## 3.2 Volumes and provenance

Every API call is append-logged (condition fields, tokens, actual cost, serving
provider, raw response, parse status) and idempotent by `call_id` (SHA-256 of the
condition vector), so interrupted runs resume without re-paying. The ledger records
191,087 experiment calls plus 4,059 generation/pretest/repair calls. All moderators
come from official BLS/O*NET releases (see §2.2); where the serving vintage coded an
occupation differently (Pharmacists 29-1051 vs 29-1251) a SOC alias is recorded.

# 4. Method

## 4.1 Outcomes

Primary outcomes: E1/E4 interview rate and recommended salary; E2 probability the
parent candidate is chosen; E3 top-1/top-3 inclusion. Mechanism ratings
(competence, commitment, promotability, likability) follow Correll et al. (2007).

## 4.2 Estimation

- **E1/E4**: OLS, `Y ~ family × female (+ pregnant flag) + résumé FE + name FE`,
  SEs clustered by résumé (80 clusters). The pregnancy condition is female-only and
  enters as a separate full-rank indicator. Moderator models add standardized `Z ×
  family × female` interactions (Z ∈ female share, median wage, time demands).
- **E2**: exact binomial tests of P(parent chosen) = 0.5 with Wilson 95% intervals;
  paired differences (parent − childless) with t-based CIs and standardized effects
  (mean/SD of pair differences).
- **E3**: top-3 selection rates by candidate type; adverse-impact ratios (parent rate
  ÷ same-gender childless rate) judged against the EEOC four-fifths rule (< 0.80).
- **Cross-model**: inverse-variance fixed-effects pooling with I² heterogeneity.
- **Position robustness**: E2 P(chosen = A); E3 top-1 rate by screen label.

## 4.3 Measurement discipline

Rating scales are strictly validated (no clamping): out-of-range values (e.g., 8 on a
1–7 scale) or missing fields are parse failures. One automatic JSON repair pass re-asks
the same model. Multiple-comparisons caveat: we report dozens of coefficients; the
headline effects are significant at p < 10⁻³⁰ (binomial z > 10), far beyond any
Bonferroni correction, while moderator interactions (§5.6) should be read as
exploratory.

## 4.4 Qwen scale-overflow protocol

Qwen3.8 Flash emitted out-of-range ratings (mostly 8) in ~23% of E2 calls —
condition-correlated (leave-gap contrasts most affected) and landing on the *childless*
candidate 3:1. We therefore (i) keep strict validity for primary estimates,
(ii) run a field-targeted second repair pass (documented deviation; repairs logged and
costed), and (iii) report both bounds; recovered cases move Qwen's estimates toward
*larger* penalties, so strict validity is conservative.

# 5. Results

## 5.1 Data quality and robustness checks

Parse validity ≥ 98.5% for all models (Figure 6, left). Refusals occur only in Claude
Haiku 5.5 (0.48% overall; up to 1.9% in E2 leave-gap-mother cells) and take the form of
valid JSON with all-zero scores plus a rationale citing protected characteristics —
analyzed below as an outcome. Position bias differs by model: E2 P(chosen = A) ranges
from 0.39 (Haiku, second-position preference) through 0.53 (Luna, neutral) to 0.83
(DeepSeek); E3 top-1 rates decay monotonically with screen position in every model
(Figure 6). Because every comparative design counterbalances position, these biases
cancel within conditions; they matter only for production systems that present
candidates in a fixed order.

## 5.2 E1 — isolated scoring: surface fairness

Recommended-salary differences between `none` and any family condition within gender
are small: −0.3% to −1.5% (Figure 3). Interview-rate gaps for `parent_gap` women are
−1.5pp (DeepSeek), −1.1pp (Qwen), and statistically zero for Haiku/Luna (ceiling: their
base interview rates exceed 95%). Two exceptions stand out. First, **pregnancy
disclosure**: recommended salary for pregnant applicants falls by $852 (DeepSeek,
p = .025), $1,074 (Luna, n.s.), $1,562 (Qwen, n.s.) — and by **$18,713 (Haiku,
p < .001)**, a 24% cut. Second, the `married` cover note (relocation with spouse)
depresses *commitment* ratings for both genders in most models — a relocation signal,
not a family signal, and a useful placebo: models do read cover notes, but the
gender-differentiated action is in the comparative tasks below.

## 5.3 E2 — paired comparison: large, uniform, gender-generalized penalties

Figure 2 shows P(parent chosen) for every model × contrast × gender. Every one of the
24 cells is significantly below 0.5 (all p < .001; binomial z between 6 and 29).

| P(parent chosen) | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| Parent (PTA), women / men | .356 / .349 | .232 / .275 | .299 / .303 | .387 / .398 |
| Parent + high commitment, w / m | .419 / .411 | .266 / .331 | .235 / .254 | .434 / .421 |
| Parent + leave gap, w / men | .310 / .307 | .111 / .131 | .193 / .190 | .229 / .256 |

Three regularities: **(a)** the leave gap is always the worst cue and high-commitment
evidence never restores parity (H6: penalties persist — and for GPT-6 Luna they
*deepen*, .235 vs .299 for mothers, the cleanest normative-discrimination signature
we observe); **(b)** penalties are statistically indistinguishable by gender — the
fatherhood bonus predicted from human studies (H2) is absent everywhere; **(c)** model
rankings are stable: Haiku ≻ Luna ≻ DeepSeek ≻ Qwen in penalty size, with Haiku
roughly twice Qwen's.

Paired salary differences for mothers (parent cue) sit in a remarkably tight band:
−$1,332 to −$1,855 per model, i.e. **−1.7% to −2.3%** of the childless candidate's
offer (leave gap: −1.2% to −4.0%). Standardized commitment penalties for mothers range
from d = −0.21 (DeepSeek) to −0.64 (Luna).

**Meta-analysis.** Pooling the four models (inverse-variance): P(parent chosen) for
mothers = 0.319, i.e. **−18.1pp below parity** (z = −35.3); for the leave gap,
**−28.9pp** (z = −56.2). Heterogeneity is extreme (I² = 98%), underscoring that the
penalty's *existence* is universal while its *magnitude* is model-specific — an
algorithmic-monoculture concern (Kleinberg & Raghavan 2021): the same applicant faces
2–4× different penalties depending on which vendor's model the employer runs.

## 5.4 E3 — ranking pools: token parents fail the four-fifths rule in every model

When a single parent appears among five childless candidates, top-3 selection falls
(Figure 4): mothers 0.34 vs 0.61 for identical childless women (DeepSeek), 0.35 vs 0.53
(Qwen), 0.36 vs 0.61 (Luna) — and 0.09 vs 0.65 (Haiku). **Adverse-impact ratios:**
DeepSeek 0.56 (F) / 0.53 (M), Luna 0.59 / 0.60, Qwen 0.57 / 0.59, Haiku **0.14 / 0.15**
— all below the 0.80 threshold used in US employment-law practice; Haiku's token
mothers are effectively erased from shortlists. In all-parent pools the pattern
reverses (mothers outrank fathers), and in 3+3 mixed pools parents are at parity:
the penalty attaches to *being the caregiving outlier*, not to parenthood per se — a
pool-composition effect that isolated-résumé audits cannot detect.

## 5.5 E4 — job-description wording is causal

With the occupation fixed and only the closing paragraph of the JD varying, the
leave-gap interview penalty for mothers moves sharply (Figure 5): from −0.6pp (DeepSeek
base) to **−3.3pp under greedy wording**; Haiku −0.0 → −3.1pp; Qwen −1.7pp; Luna −0.8pp
(smallest, consistent with its cue-driven profile). A one-sentence family-friendly
policy does not reliably repair the greedy penalty; EEO boilerplate does nothing in any
model. Greedy wording also cuts commitment ratings for leave-gap parents (~0.5 scale
points) and their salaries ($1.6–3.9k). This is H7's pattern: the *signal* in the job
ad, not the occupation's average characteristics, switches the penalty on.

## 5.6 Occupational moderation (H3/H4): gradients are weak where the theory expects them

In the pooled E1 regressions with occupation interactions (Figure 8), the
mother-minus-father parent gap in commitment is robust at the occupation mean
(DeepSeek −0.09, p = .002; Haiku −0.06, p < .001), but the triple interactions with
time demands and female share are small and mostly non-significant, with two
exploratory exceptions: DeepSeek's leave-gap gender gap in salary is −$1,271 (p = .015)
at mean female share, and its interaction with female share on competence ratings is
negative (mothers penalized *more* in female-dominated occupations; p = .017). We read
this against H3/H4 as follows: the observational occupation gradient is mostly
absorbed by résumé fixed effects and is weak in scoring tasks — but E4 shows the
*mechanism* is real when greediness is manipulated experimentally within occupation.
Occupation-level moderation in scoring should thus be interpreted cautiously; the
greedy-job channel operates primarily through job-ad language.

## 5.7 Benchmark: LLMs versus human evaluators

Comparing our mother-vs-childless estimates with Correll et al. (2007)'s laboratory
benchmarks (Figure 7): recommended-salary penalties are **one-quarter the human size**
(human −7.4%; LLMs −1.7% to −2.3%), while commitment penalties for the two strongest
models (Luna d = −0.64, Qwen −0.57) approach the human commitment benchmark
(≈ −0.87). Shortlisting penalties are where LLMs *exceed* human behavior: a −18pp
pooled choice deficit and four-fifths violations in ranking have no counterpart in the
human audit literature's hiring rates at this magnitude. Classification (Table in
Correll terms): LLMs **reduce** the salary penalty, **mirror or amplify** the
commitment/schema penalty, **generalize it to fathers**, and **add** a
ranking-specific failure mode humans did not exhibit.

## 5.8 Model-specific signatures

- **Claude Haiku 5.5** — severity outlier: 2× the pairwise penalty, token-mother
  impact ratio 0.14, pregnancy salary cut −$18.7k, the only refuser (0.5%,
  cue-concentrated), and the only second-position preference. Safety-refusal behavior
  and discriminatory ranking coexist.
- **GPT-6 Luna** — normative-discrimination prototype: commitment evidence deepens
  the penalty (H6); most position-neutral (P(A) = .53), so its penalties are not
  order artifacts; smallest E4 context effects.
- **Qwen3.8 Flash** — smallest choice penalties, but its measurement failure is
  itself differential (scale overflow toward childless candidates in leave-gap
  contrasts); after repair it remains the least penalizing model.
- **DeepSeek V4.1 Flash** — reference profile: moderate everywhere; only model with a
  significant leave-gap gender gap in salary (−$1.3k, p = .015) and the largest
  greedy-JD amplification.

# 6. Statistical interpretation

**Effect sizes and precision.** All headline choice results are extreme relative to
sampling error: the smallest single-cell z is 6.1 (Qwen, mothers, parent cue,
z = (0.387−0.5)/√(0.25/2396) ≈ −11); pooled z = −35 to −56. Salary paired differences
carry 95% CIs of ±$250–550 — the four models' bands overlap for the parent cue
(−1.7% to −2.3%) but diverge for the leave gap (−1.2% to −4.0%). Interview-rate
penalties in E1 are small precisely because outcomes are ceiling-compressed
(95–100% base rates); the tasks that force a choice (E2/E3) carry the discriminative
variance, and analyses of LLM "fairness" that use only isolated scoring will
systematically understate discrimination.

**Heterogeneity.** I² ≈ 98% across models implies the fixed-effects pooled estimate
should be read as "the average deployed model," not as a property of the class;
model identity dominates every design factor in magnitude.

**Robustness.** (i) Position counterbalancing absorbs order biases that range up to
P(A) = 0.83. (ii) The Qwen repair protocol bounds the scale-overflow issue: strict
validity (reported) yields *smaller* penalties than the repaired/winsorized variants,
so cross-model conclusions are conservative. (iii) Refusals (Haiku only) are treated as
an outcome, not missing-at-random: they concentrate in exactly the cells that carry
treatment (up to 1.9%), so naïve exclusion would overstate Haiku's fairness; including
all-zero refusal scores would overstate its severity. We report both boundaries.

**Interpretive cautions.** Moderator interactions (§5.6) are exploratory (≈100
coefficients; several p-values near .05 would not survive correction). The
`pregnant` condition has no male counterpart and is estimated against childless women
only. Names are racially White-coded by design, so all effects are race-held-constant.

# 7. Analysis of the bias

**Mechanism: normative, not statistical.** If models used family status as a proxy for
unobserved productivity (statistical discrimination), explicit counterevidence —
top-performer awards, volunteered extra hours — should eliminate the penalty. It never
does; for GPT-6 Luna it backfires. The pattern matches Benard & Correll's (2010)
normative account: the penalty enforces an ideal-worker schema rather than responding
to information.

**Why fathers too?** Human schemas gender the devoted-parent/ideal-worker conflict;
the models generalize the *conflict* itself without the asymmetry. Downstream this is
still a gendered problem: in the population, caregiving gaps and PTA lines are worn by
women, so a gender-neutral penalty binds mostly on mothers in practice — and pregnancy
disclosure (a strictly female signal) draws the largest single penalty we observe
(Haiku −$18.7k).

**Where the bias lives.** Not in scoring, but in comparison — consistent with
alignment training suppressing overt single-item judgments while comparative
frames ("which of these two?") elicit schema-consistent trade-offs. This is precisely
the "surface fairness, deep bias" pattern: audits that only measure isolated scores
will certify as fair systems that exclude mothers from shortlists.

**Monoculture.** The same applicant faces penalties ranging from −11pp (Qwen) to −27pp
(Haiku) below parity depending on the vendor. Because a handful of models serve
thousands of employers, these are correlated market-level errors, the condition under
which Kleinberg & Raghavan show a single algorithm's bias reduces welfare more than
dispersed human bias.

**Policy levers, tested.** EEO boilerplate: no effect. Family-friendly policy
sentences: partial and unreliable. The one lever that moved outcomes is the *greedy
signal itself* — job ads that do not demand around-the-clock availability do not
trigger the amplification. Banning the inference of caregiving gaps (or letting
candidates omit them, as several jurisdictions now do with salary history) targets the
single most damaging cue we measured.

# 8. Limitations

(1) English-language, US-occupation context; JDs and résumés are study-constructed, so
effects are internal to our materials — by design (correspondence audits trade
external validity for causal identification). (2) Race is held constant; intersection
penalties are not estimated. (3) One endpoint per model (pinned for internal
consistency); quantization or serving differences may shift absolute levels, though
not within-model comparisons. (4) 32% of base résumés are synthetic and LLM-generated
(O*NET-grounded, validator-screened); resume fixed effects absorb level differences
within occupation, and the pretest found no résumé-quality outliers that survived
correction for small-sample z-inflation. (5) The advisor side of the market (E5) is
implemented but not run; the "deep bias" claim here concerns gatekeeping only.
(6) Model versions are pinned and dated; bias levels should be re-measured per release.

# 9. Conclusion

Across four commercially deployed models, 20 occupations, and 191,000 logged
decisions, the motherhood penalty survives in LLM hiring — but transformed. It is
nearly invisible in isolated scores, large and precisely estimated whenever candidates
are compared, gender-generalized (no fatherhood bonus), dominated by the caregiving
gap, amplified by greedy job ads, untouched by EEO boilerplate, and worst where
shortlists are built. Models do not merely inherit human biases; they redistribute
them across tasks, genders, and vendors. Auditing regulation that stops at single-résumé
scoring will not see it.

# Reproducibility

Pinned model slugs, frozen materials, deterministic plans (call_id = SHA-256 of
condition vector), append-only logs with per-call costs, and analysis code are in the
project repository; total spend $40.04 against a $200 cap. Per-model reports:
`docs/phase1/` (DeepSeek), `docs/phase2/` (three models); cross-model table:
`runs/pooled/model_comparison.csv`; statistics: `docs/report/stats.json`.

# References

- Acker, J. (1990). Hierarchies, jobs, bodies. *Gender & Society*, 4(2), 139–158.
- Benard, S., & Correll, S. J. (2010). Normative discrimination and the motherhood
  penalty. *Gender & Society*, 24(5), 616–646.
- Bertrand, M., & Mullainathan, S. (2004). Are Emily and Greg more employable than
  Lakisha and Jamal? *American Economic Review*, 94(4), 991–1013.
- Correll, S. J., Benard, S., & Paik, I. (2007). Getting a job: Is there a
  motherhood penalty? *American Journal of Sociology*, 112(5), 1297–1338.
- Goldin, C. (2014). A grand gender convergence: Its last chapter. *AER*, 104(4).
- Goldin, C. (2021). *Career and Family*. Princeton University Press.
- Kleinberg, J., & Raghavan, M. (2021). Algorithmic monoculture and social welfare.
  *PNAS*, 118(22), e2018340118.
- Rozado, D. (2025). Gender and positional biases in LLM-based hiring decisions.
  arXiv:2505.17049.
- Frermann, L., et al. (2023). Gender bias and parental-leave gaps in ChatGPT résumé
  ranking. University of Melbourne.
- An, J., et al. (2025). Intersectional evidence from automated resume evaluation.
  *PNAS Nexus*, 4(3).
- Full prior-literature table: `docs/proposal.md`.

# Figures (vector PDF)

- `figures/fig1_design.pdf` — Design overview
- `figures/fig2_e2_forest.pdf` — E2 choice probabilities with 95% CIs
- `figures/fig3_e1_cells.pdf` — E1 interview rate and salary by condition
- `figures/fig4_e3_impact.pdf` — E3 token-parent selection and adverse-impact ratios
- `figures/fig5_e4_context.pdf` — E4 leave-gap penalty by JD wording
- `figures/fig6_quality.pdf` — Validity, refusals, position-bias checks
- `figures/fig7_benchmark.pdf` — Benchmarking against Correll et al. (2007)
- `figures/fig8_moderators.pdf` — Occupational moderation gradients
