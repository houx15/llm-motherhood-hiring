# Do LLM Hiring Tools Penalize Mothers? A Four-Model Audit Across Decision Tasks and Gender-Information Regimes

*Draft 4.0 (integrated main-run + phase-3 results), 2026-10-21. All statistics are
generated from run logs by `uv run audit stats` (main run → `stats.json`,
`tables.md`) and `uv run python -m audit.analysis.{phase3_key_stats,cross_model}`
(phase 3 → `phase3_key_stats.json`, `CROSS_MODEL.md`); no hand-typed numbers.*

## Abstract

Language models increasingly assist résumé screening, yet audits of hiring bias
typically probe a single model scoring a single résumé. We audit four deployed
consumer LLMs (DeepSeek V4.1 Flash, Claude Haiku 5.5, GPT-6 Luna, Qwen 3.8 Flash;
pinned slugs, 600,000 logged calls, US-market materials, 28 occupations, 120+
validated résumés) across four decision tasks — isolated scoring, pairwise
choice, pool ranking, and job-ad context — using within-résumé designs that hold
candidate quality constant while varying family-status cues. We find: **(1) the
penalty is task-dependent** — near-zero in isolated scoring (fit ≤ 0.35 points on
a 10-point scale; interview gaps ≤ 1.5pp) but large in comparison: pooled across
models, mothers with a parental-leave gap are chosen **23%** of the time against
an otherwise-identical childless candidate (t(39) between −8 and −19 per model),
and the same résumé shortlisted at 23–81% of its childless rate. **(2) The
penalty is not about gender information**: under fully gender-blind rendering
(initials, no gender field) the parent-choice penalty is statistically
indistinguishable from gendered rendering for two models and mildly *smaller*
never larger for the rest. **(3) Placebo decomposition shows what the penalty is
about**: an 8-month employment interruption costs the same whether labeled
*Parental leave* or *Career break — extended travel* (label effect +.01 to +.07
across all four models), while the explicit family bundle (children + PTA lines)
adds a further −.11 to −.24. **(4) There is no fatherhood bonus anywhere**; only
Claude Haiku 5.5 penalizes mothers significantly more than fathers (Holm-corrected).
**(5) Vendors diverge sharply when gender is explicit**: Qwen is at parity in
direct woman-vs-man choices, Luna's pro-woman preference surges (.52 → .65 for
mother-vs-father), Haiku flips against mothers (.54 → .47). **(6) Haiku responds
to pregnancy disclosure by withholding salary offers entirely (19.8% of pregnant
applicants, rising to 27.5% under an explicit gender field) — and those withheld
applicants are advanced to interview only 30% of the time**, a net −9.4pp
interview penalty on a margin invisible to scoring audits. On pay and hiring
margins these models *reduce* the human laboratory motherhood penalty (≈ −$11k
≈ −7.4%; Correll et al. 2007) to −1.7% to −2.3% — but redistribute it into
comparative decisions, ranking composition, and abstention. Single-résumé audits
cannot see any of it.

## 1. Introduction

Automated résumé screening is among the most commercially deployed uses of large
language models, and among the most regulated. The canonical social-psychological
account of hiring discrimination against mothers — Correll, Benard & Paik (2007) —
describes a *status-based* penalty: motherhood triggers a competence/commitment
discount applied to women specifically, producing a 37-point hire-rate gap and an
≈ $11,000 salary penalty in the laboratory, with no parallel "fatherhood bonus"
for men. Whether LLM hiring tools reproduce that *gendered* penalty, a
gender-neutral caregiver penalty, or no penalty at all is an empirical question
with direct regulatory consequences (EEOC Uniform Guidelines' four-fifths rule;
EU AI Act high-risk-system testing obligations).

Existing LLM-bias audits mostly evaluate a single decision format — one model,
one résumé, one score. Our design varies the *decision task* while holding the
candidate fixed, because hiring is rarely scoring in isolation: real pipelines
rank, shortlist, and choose among finalists. We further vary *what the model can
know about gender* (explicit field, gendered names, initials-only, fully blind)
and *which part of the parent signal* is present (disclosure alone, interruption
alone, caregiving label, full family bundle). Finally we treat *abstention* —
refusing to name a salary — as an outcome in its own right.

Three questions organize the study:

- **Q1 (margin).** Where does the penalty live — scores, choices, rankings, or abstention?
- **Q2 (content).** Is the penalty about being a woman, being a parent, or having interrupted employment?
- **Q3 (moderation).** Does it depend on gender information, occupation, or job-ad wording?

## 2. Design overview

### 2.1 Models and governance

Four deployed consumer models via OpenRouter, pinned to dated slugs and single
endpoints (never `*-latest`; Claude/Anthropic, GPT-6/OpenAI, Qwen/Alibaba
first-party; DeepSeek pinned to DeepInfra fp8 after first-party routing was
blocked by account guardrails — see QUESTIONS.md §2b): reasoning disabled, JSON
mode, per-call logging with provider attribution, deterministic and resumable
plans, append-only ledger, hard budget $200 (reserve $20). Total: 602,093 logged
calls, $160.48 spent. All materials pass a phrase-level cue validator (no
family/gender/PII wording in base résumés) and a merit pretest.

### 2.2 Materials

- **Occupations (main run, O20).** 20 occupations on a gender-composition × wage
  grid (female share 4.7%–97.1% from BLS CPS Table 11; median wage from OEWS;
  O*NET time-demands composite).
- **Occupations (phase 3, O8).** 8 additional occupations selected by exhaustive
  quota-constrained search over O*NET work-activity composites to break the
  care↔female-share confound: childcare worker, electrician, EMT/paramedic,
  health-services manager, housekeeper, police officer, security guard,
  veterinarian (design in Appendix A; the female-share–care correlation falls
  .53 → .32, and female share becomes separable from every task composite).
- **Résumés.** 4–6 per occupation (120+ total): 28 anonymized Kaggle-derived +
  O*NET-grounded synthetic, all validated for contiguous 8–12-year histories,
  no gender/family/PII wording; 2 unqualified attorney résumés replaced by
  qualified J.D./bar-admitted attorneys after detection (fit 3.3 → 9.2), with
  affected cells re-run.
- **Names.** Six gendered, White-coded first names per gender (Bertrand &
  Mullainathan 2004 list, validated in Gaddis 2017), rotating within every cell;
  three shared surnames. Race is held constant throughout.

### 2.3 Family-status cues (within-résumé)

All cues render identically across genders; a cover note is present in every
condition.

| code | cover note | résumé change |
| --- | --- | --- |
| `none` (baseline) | "excited to be applying" | — |
| `parent` | "married with two children" | PTA volunteer line |
| `parent_gap` | " + leave | 8-month *Parental leave* entry inserted; later dates shifted |
| `parent_committed` | " + objective commitment bullets |
| `pregnant` (women only) | "currently pregnant" | — |
| `personal` *placebo* | marathon/hobby line | shelter-volunteer line (length-matched) |
| `gap_travel` *placebo* | neutral | 8-month *Career break — extended travel*, same date arithmetic |
| `gap_parental_only` *placebo* | neutral | 8-month *Parental leave*, no children line, no PTA |

The placebo ladder identifies: disclosure alone (`personal`), the interruption
(`gap_travel`), the caregiving label (`gap_parental_only` − `gap_travel`), and
the family bundle (`parent_gap` − `gap_parental_only`).

### 2.4 Gender-information regimes (phase 3)

Four cue levels: **L0** gendered first name; **L1** name + explicit header line
"Gender: Female/Male"; **L2** gender-neutral initial + the same field (isolating
the field from the name); **L3** initials only — fully gender-blind. A
manipulation check (§5.1) verifies each level's legibility. Direct woman-vs-man
choice pairs (same family status both sides, roles and screen positions rotated)
measure gender preference at L0–L2.

### 2.5 Tasks

- **E1 scoring**: one candidate; fit (1–10), interview, salary, 1–7 ratings.
- **E2 pairwise choice**: two finalists, one childless one cued; P(cued chosen);
  parity = .50.
- **E3 ranking**: pools of six with a token parent (role and gender rotated by a
  margin-balanced Latin design); top-3 shortlisting vs the same résumés shown
  childless (résumé fixed effects).
- **E4 job-ad wording**: leave-gap penalty under base/EEO/family-friendly/greedy
  wording (résumé-FE difference-in-differences).

### 2.6 Inference

Every estimate is within-résumé. SEs are clustered where stimuli repeat: E1 by
résumé; E2 by résumé pair (mean of pair-cluster means, t vs parity, df = 39 —
naïve binomial z-tests would overstate precision several-fold); E3 by occupation
with résumé and position fixed effects; E4 by résumé. Holm correction within
each test family. Strict validity (nothing clamped): out-of-range responses are
parse failures; condition-correlated invalidity (Qwen's E2 scale overflow, ~23%
of its E2 calls raw) is handled by logged, `repair_of`-linked repair passes
(final main-run validity 99.91% / 98.99% / 98.95% / 99.83% for DeepSeek / Haiku
/ Luna / Qwen; phase-3 100% / 100% / 100% / 99.98%), and every headline
estimate is re-computed on strict-validity samples that exclude any call whose
valid response came from a repair. Refusals and salary withholding are analyzed
as outcomes.

## 3. Preregistration status

The main-run design (SPEC.md) and phase-3 addendum (SPEC_PHASE3.md) with
analysis plans were fixed and committed before each paid run; two documented
deviations (DeepSeek endpoint substitution; manipulation-check-driven
substitution of clinical psychologists, whose CPS female share is suppressed,
with health-services managers) were researcher-approved before execution. This
report follows the analysis plans except where marked exploratory. The study is
a prospective internal audit, not a registered report.

## 4. Results

### 4.1 What the models can infer about gender (manipulation check)

Explicit fields are perfectly legible: with "Gender: Female/Male" present (L1/L2)
all four models identify the applicant's gender correctly **100%** of the time
(n = 336 each). Gendered names alone are read reliably by DeepSeek (96.7%) and
Qwen (98.2%) — but only partially by **Luna (66.1%)** and **Haiku (42.3%)**,
which answer "unknown" for 34% and 58% of name-only packets (Haiku also
recognizes male names better than female ones). Under blind rendering (L3) no
model defaults to "male" (≥ 97.6% "unknown"). Two consequences: (i) name-only
audits under-treat the gender *information* actually available to some vendors;
(ii) our L1/L2 comparisons cleanly manipulate the model's knowledge, validated
rather than assumed.

### 4.2 The penalty is task-dependent (Q1)

**Scoring (E1).** Women, cue-cell minus childless-cell (same résumé, occupation,
model):

| model | fit: parent | fit: leave-gap | interview: parent | interview: gap | salary: parent |
| --- | --- | --- | --- | --- | --- |
| DeepSeek | −0.13 | −0.35 | +1.1pp | −1.5pp | −$933 |
| Haiku | **+0.34** | +0.14 | +1.2pp | 0.0pp | −$252 |
| Luna | −0.08 | −0.25 | +0.3pp | +0.6pp | +$412 |
| Qwen | −0.02 | −0.14 | +0.7pp | −1.1pp | −$1,150 |

Isolated scoring is nearly flat: fit moves at most a third of a point on a
10-point scale, interview rates at most 1.5pp. Haiku — the most discriminatory
model below — actually rates parent versions *higher* when scoring them alone.

**Choice (E2).** The same models, same cues, same résumés, two finalists at a
time. P(cued candidate chosen) vs the childless candidate in the same prompt
(parity .50; t over 40 résumé-pair clusters; every cell |t| ≥ 5):

| contrast | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| parent — mother | .357 | .233 | .297 | .387 |
| parent — father | .349 | .276 | .294 | .398 |
| + committed — mother | .419 | .266 | .228 | .407 |
| + leave gap — mother | .310 | **.110** | .186 | .230 |
| + leave gap — father | .308 | .130 | .184 | .256 |

Pooled across models, mothers with the plain parent cue are chosen 33.7% of the
time (−16.3pp below parity); with a leave gap, 23.2% (−26.8pp). Between-model
heterogeneity is large (I² = 91–95%): the same cue costs −11pp (Qwen) to −27pp
(Haiku).

**Ranking (E3).** One token parent in a pool of six; top-3 shortlisting of the
same résumés shown childless (résumé-FE adjusted impact ratios; four-fifths
line = .80):

| model | mothers | fathers | t |
| --- | --- | --- | --- |
| DeepSeek | .71 | .70 | −4.5 / −4.7 |
| Haiku | **.25** | **.23** | −8.4 / −9.8 |
| Luna | .78 | .81 | −2.8 / −4.1 |
| Qwen | .75 | .80 | −4.7 / −4.9 |

The identical résumé, in the identical pool, is shortlisted at 70–81% of its
childless rate by three models and 23–25% by the fourth. Two of four models
violate the four-fifths rule for both genders; Luna fathers and Qwen fathers sit
exactly at the line.

**The scoring-vs-choice contrast is the first headline**: the penalty lives in
the comparison, not the score. A bias audit built on single-résumé scoring —
the default format — would report all four models as essentially fair.

### 4.3 What the penalty is about (Q2): interruption + family bundle, not gender, not the "parental" label

**Placebo decomposition (E2, mothers, L0; P(cued chosen) differences):**

| component | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| parenthood net of disclosure (`parent` − `personal`) | −.107 | −.269 | −.124 | −.095 |
| caregiving *label* net of interruption (`gap_parental_only` − `gap_travel`) | **+.010** | **+.013** | **+.041** | **+.074** |
| family bundle on top of the gap (`parent_gap` − `gap_parental_only`) | −.156 | −.238 | −.177 | −.108 |

Disclosure alone is nearly free (`personal` is chosen .45–.53 vs .50 parity).
The 8-month interruption costs 10–20pp **whether it is labeled "Parental leave"
or "Career break — extended travel"** — the caregiving label adds at most +.07
and is not significant for any model. The explicit family bundle (children +
PTA) adds a further 11–24pp *on top of* the interruption. The same structure
holds for fathers and at every cue level.

**Gender-information invariance.** In the clean same-occupation design (O8
occupations rendered at all four cue levels; both genders pooled), P(parent
chosen):

| model | L0 name | L1 name+field | L2 initial+field | L3 blind |
| --- | --- | --- | --- | --- |
| DeepSeek | .347 | .348 | .347 | .343 |
| Qwen | .406 | .396 | .406 | .384 |
| Luna | .344 | .378 | .389 | .357 |
| Haiku | .277 | .352 | .373 | .283 |

(leave-gap rows: DeepSeek .249/.258/.243/.277; Qwen .269/.268/.263/.263; Luna
.095/.098/.091/.102; Haiku .090/.129/.131/.098.)

For DeepSeek and Qwen the penalty is *numerically identical* with and without
any gender information — the spec's key test: if the blind penalty equals the
gendered penalty, the penalty is about caregiving, not gender. Luna and Haiku
show a partial exception: explicit gender *softens* their parent penalty by
5–10pp, and the effect vanishes under blind rendering. No model penalizes
parents *more* when gender is explicit.

**Ranking replicates the invariance.** E3 top-3 ratios (token parent vs
childless members, compositions a+b): DeepSeek .64/.66/.66/.65, Haiku
.15/.19/.17/.16, Luna .70/.72/.70/.71, Qwen .68/.71/.74/.71 across L0/L1/L2/L3.

### 4.4 No fatherhood bonus; who penalizes mothers *more*

Fathers are below parity in every cell of every model (e.g., leave-gap fathers
.308/.130/.184/.256) — no fatherhood bonus exists in any task. Mother-minus-
father differences (pair-matched t-tests, Holm over 12 tests) are ≈ 0 for
DeepSeek and Luna, nominal-but-not-surviving for Qwen, and significant only for
**Haiku** (parent −.043, Holm p=.037; committed −.065, Holm p=.001; leave gap
−.020, Holm p=.33). The traditional *gender-asymmetric* motherhood penalty is
thus the exception, not the rule: what generalizes across vendors is a
caregiver-general penalty; one vendor adds a mother-specific component.

### 4.5 Explicit gender: vendor divergence in direct preference

Direct woman-vs-man choices (same family status both sides; parity .50):

| model | childless L0 → L1 → L2 | mother-vs-father L0 → L1 → L2 |
| --- | --- | --- |
| Qwen | .497 → .492 → .514 | .503 → .514 → .488 |
| DeepSeek | .515 → .540 → .538 | .536 → .540 → .547 |
| Luna | .522 → **.587** → .575 | .578 → **.647** → .634 |
| Haiku | .528 → .526 → .513 | .544 → .498 → **.470** |

Qwen is gender-blind in choice. DeepSeek carries a small, stable pro-woman
tilt. **Luna** — which reads names correctly only 66% of the time — shows a
large pro-woman preference that appears only when gender is explicit (+13pp).
**Haiku** moves the other way: a mild pro-woman tilt under names becomes a
*penalty against mothers* when gender is explicit (−7pp). Explicit gender
fields, standard in many markets (and encouraged by some transparency
policies), are therefore not neutral: they activate vendor-specific gender
preferences that name-only screening conceals.

### 4.6 Abstention: withholding offers as a discrimination margin

**Haiku withholds salary entirely (returns $0) for pregnant applicants**: 19.8%
in the main run (names only), rising to **27.5%** with an explicit gender field
(and 25.7% under initials+field). No other model abstains at any cue level or
family condition (≤ 1.8%). Withholding is not benign abstention: withheld
pregnant applicants are advanced to interview only **29.9%** of the time
(vs 100% when a salary is named), producing a net within-résumé interview
penalty of **−9.4pp (t = −4.8)** — consistent with 19.8% × 70% denial. Among
*scored* offers, no model shows a meaningful pregnancy salary penalty (−0.8% at
most). Rationales frame the withholding as protective ("salary should not
depend on pregnancy"), yet the downstream result is that one in five pregnant
applicants receives neither a price nor an interview. Regulatory audits that
treat missing outputs as missing data will miscount this as fairness.

### 4.7 Salary and the human benchmark

E2 paired salary, mother minus her paired childless woman (withheld excluded):
DeepSeek −$1,854 (−2.19%), Haiku −$1,332 (−1.68%), Luna −$1,548 (−1.66%), Qwen
−$1,775 (−2.33%); leave-gap −$942 to −$3,145. Against Correll et al.'s
laboratory benchmark (≈ −$11,000 ≈ −7.4% between childless women and mothers;
84% vs 47% hire recommendation), the LLM salary penalty is roughly one-quarter
the human one, and the choice penalty (−16 to −27pp) is smaller than the human
37pp hire-rate gap. Directionally, these deployed models *reduce* the classic
motherhood penalty on pay and hire margins — while redistributing it into
shortlist composition (E3), comparative rejection (E2), and abstention. (The
comparison is directional: a within-pair choice share is not metrically a
between-persons hire rate.)

### 4.8 Job-ad wording (E4)

Varying only the JD's closing paragraph (résumé-FE DiD vs base wording, 32
clusters): **greedy** wording ("must be willing to work long hours and be fully
committed") adds a significant extra interview penalty to leave-gap mothers for
DeepSeek (−2.7pp, t = −2.3) and, combined with family-friendly language, for
DeepSeek both genders (−5.2/−6.0pp) and Haiku mothers (−8.0pp, t = −2.8).
Family-friendly sentences *alone* never help and often slightly hurt (−0.4 to
−2.1pp, all n.s.); **EEO boilerplate has no effect in any model**. The greedy
signal, not the diversity signal, moves behavior.

### 4.9 Occupational moderation: composition, not content (exploratory)

With 28 occupations and female share separable from task composites, we regress
occupation-level leave-gap penalties on standardized female share, wage, and
O*NET physical/care/analytic/manage composites (n = 28 per model). The penalty
is *smaller* in female-dominated occupations for every model (DeepSeek +.057,
p = .025; Luna +.047, p = .15; Qwen +.026; Haiku +.018), while task content is
essentially irrelevant (care: significant only for Luna, −.058, p = .05;
physical, analytic, manage: n.s. everywhere). Where mothers are common, the
caregiver penalty is muted — consistent with statistical-discrimination
updating against a group-specific base rate, not with task demands.

### 4.10 Robustness

**Drift**: phase-3 anchor cells run +1.1 to +3.5pp above the main run on
interview rates (all four models; one of four cells crosses the pre-set 0.03
flag) — mild upward drift across prompt versions, orthogonal to within-run
comparisons. **Validity**: final main-run validity 99.91% / 98.99% / 98.95% /
99.83% (DeepSeek / Haiku / Luna / Qwen, after logged repair passes; Qwen's
condition-correlated E2 overflow affected ~23% of its raw E2 calls and is
analyzed under both strict validity and repair-recovered samples); phase-3
validity 100% / 100% / 100% / 99.98%. All
repair passes are logged and `repair_of`-linked; strict-validity re-estimates
do not move any conclusion. **Materials**: replacing the two unqualified
attorney résumés (fit 3.3 → 9.2) converted near-arbitrary lawyer-pair choices
(.38 mothers/.43 fathers) into measurable penalties (.21/.08), confirming that
failing-candidate pairs compress rather than bias comparisons. **Names**: six
per gender, rotated within every cell; paraphrase templates balanced.
**Position bias** exists and is fully counterbalanced: Luna is near-neutral
(P(A) = .53), Qwen mild (.58) and DeepSeek strong (.68) first-position
preferences, while Haiku prefers the *second* position (.39) — consistent with
its opposite direction of asymmetry in other tasks.

## 5. Discussion

### 5.1 What kind of discrimination is this?

The human motherhood penalty in the status-characteristics tradition is
*mother-specific*: it is applied to women because they are mothers, and it does
not attach to fathers. What we find in deployed LLMs is different in structure.
The penalty (i) attaches to fathers as strongly as to mothers in three of four
models, (ii) is invariant to whether the model knows the candidate's gender at
all, and (iii) is driven by the *employment interruption* and the *explicit
family bundle*, not by the word "parental" — an identically-dated travel break
costs the same. This is the signature of a **committability heuristic**: the
model treats a recent caregiving interruption and overt family signals as
evidence of lower availability, against the candidate in any pairwise or
ranking contest, regardless of who the candidate is. It is closer to
statistical discrimination on inferred availability than to the gendered status
penalty of the human literature — including its occupational signature
(smaller penalties where mothers are common).

Yet the gendered version has not disappeared; it has become **vendor-specific**.
Haiku adds a mother-specific component in same-gender comparisons (the only
Holm-surviving mother-minus-father gaps), flips against mothers in direct
cross-gender comparison when gender is explicit, and is the only abstainer.
Luna, conversely, develops a strong *pro-woman* preference under explicit
gender. Qwen is at parity. There is no single "LLM bias": four deployed models
realize four different preference structures over the same materials.

### 5.2 Implications for auditing and regulation

Three design conclusions follow directly. **First, audits must be comparative.**
Every headline effect is invisible or near-zero in single-résumé scoring — the
format most audits and most regulations contemplate. Pairwise choice and pool
ranking, the tasks that actual screening systems perform, are where 10–27pp
penalties live. **Second, abstention must be an outcome.** The largest
pregnancy effect in the study is a *refusal to price*, and it carries a real
interview denial; scoring audits with listwise deletion would score Haiku as
its fairest period. **Third, gender-knowledge must be manipulated and checked,
not assumed.** Two of four models do not reliably read gendered names; explicit
fields change behavior for two vendors in opposite directions. Audit standards
that vary only the name (the current norm, inherited from correspondence
studies) are measuring a different treatment for different vendors.

For deployment: EEO boilerplate in job ads does nothing; greedy availability
language actively amplifies the penalty; vendor choice moves the penalty by a
factor of two to eight; and "family-friendly" additions are not protective in
isolation.

### 5.3 Limitations

Materials are US-market, English-language, text-only (no photos — designed but
not run), with race held constant, so we identify nothing about race
intersections. "Pregnancy" has no male analogue. Salary is a recommendation,
not a negotiated outcome; interview is a recommendation, not a callback.
Occupation-level moderation is exploratory (n = 28). Models are consumer
endpoints of four vendors at pinned versions; behavior may differ across
versions, system prompts, and RAG contexts. Our pools and pairs are synthetic
by construction — the point is identification of the marginal effect of cues,
not estimation of population-level hiring rates. The human benchmark is a
laboratory study from 2007, compared directionally only.

## 6. Conclusion

Deployed LLM hiring tools do not so much inherit the human motherhood penalty
as **redistribute** it. On the margins an individual applicant sees in a score,
they are nearly fair. On the margins that decide who is compared, shortlisted,
and priced, they impose a large, precisely-estimated penalty on caregivers —
fathers included — driven by employment interruptions and overt family signals
rather than gender or the word "parental," with one vendor adding
mother-specific penalties and pregnancy-driven abstention, and another adding
pro-woman preference under explicit gender. Any audit regime that stops at
single-résumé scoring, ignores abstention, or assumes name-based gender
manipulation, will certify as fair systems that are not.

## References

- Bertrand, M., & Mullainathan, S. (2004). Are Emily and Greg More Employable
  Than Lakisha and Jamal? A Field Experiment on Labor Market Discrimination.
  *American Economic Review*, 94(4), 991–1013.
- Correll, S. J., Benard, S., & Paik, I. (2007). Getting a Job: Is There a
  Motherhood Penalty? *American Journal of Sociology*, 112(5), 1297–1338.
  [Salary benchmark quoted as ≈ $11,000 ≈ −7.4%, the commonly cited figure;
  verify against paper tables before journal submission.]
- EEOC (1978). Uniform Guidelines on Employee Selection Procedures, 43 FR 38290
  (four-fifths rule).
- European Union (2024). Regulation (EU) 2024/1689 (AI Act), high-risk
  employment-system obligations.
- Gaddis, S. M. (2017). How Contexts Matter: A Multilevel Analysis of Names.
  *Sociological Science*, 4, 568–587.
- U.S. Bureau of Labor Statistics. CPS Table 11 (2025); OEWS May 2025 national
  files. O*NET 31.0 database, onetcenter.org.

## Appendices

- **A. Occupation design (O8)**: `docs/report/occupation_design.md` — O*NET
  composites, quotas, selection frontier, before/after correlations.
- **B. Manipulation check**: `docs/phase3/manipulation_check.md`.
- **C. Phase-3 cross-model tables**: `docs/phase3/CROSS_MODEL.md`;
  per-model `docs/phase3/report_<model>.md`; key stats
  `docs/phase3/phase3_key_stats.json`.
- **D. Main-run tables**: `docs/report/tables.md` (programmatic).
- **E. Reproducibility**: pinned slugs/configs, frozen materials, deterministic
  plans, append-only logs and ledger ($160.48 total), analysis code in
  `src/audit/` — regenerate all statistics with `uv run audit stats`,
  `uv run python -m audit.analysis.{cross_model,phase3_key_stats}` and all
  figures with `uv run audit figures`. Decisions and deviations: QUESTIONS.md.
- **F. Figures**: `docs/report/figures/fig1–fig8` (main run: penalty by task,
  cue, model; withholding; benchmarks; E4 DiD).
