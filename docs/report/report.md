# Do LLM Hiring Tools Penalize Mothers? A Four-Model Audit Across Decision Tasks and Gender-Information Regimes

*Draft 4.1 (round-3 revisions), 2026-10-22. All statistics are generated from run
logs — main run: `uv run audit stats` → `stats.json`, `tables.md`; phase 3:
`audit.analysis.{phase3_key_stats,cross_model,round3}` → `phase3_key_stats.json`,
`CROSS_MODEL.md`, `round3_stats.json`. No hand-typed numbers.*

## Abstract

Language models increasingly assist résumé screening, yet audits typically vary
one design dimension at a time. We cross three — **decision task** (scoring,
pairwise choice, pool ranking), **family cue** (disclosure, employment
interruption, caregiving label, family bundle), and **gender-information regime**
(gendered names, explicit gender field, initials-only, fully blind) — on
identical validated materials (28 occupations, 154 résumés, 6 rotating names per
gender, 602,093 logged calls; DeepSeek V4.1 Flash, Claude Haiku 5.5, GPT-6 Luna,
Qwen 3.8 Flash at pinned versions). We find: **(1) the penalty is task-dependent**
— near-zero in isolated scoring (fit ≤ 0.35 points on a 10-point scale;
interview gaps ≤ 1.5pp) but large in comparison: pooled, mothers with a
parental-leave gap are chosen **23%** of the time against an otherwise-identical
childless candidate (t(39) between −8 and −19 per model), and the same résumé is
shortlisted at 23–81% of its childless rate (résumé-FE adjusted). **(2) The
penalty does not depend on gender information**: under fully blind rendering the
parent-choice penalty equals the name-based penalty for all four models
(pair-matched tests, all p ≥ .08); explicit gender fields *soften* the plain-parent
penalty for two models (Haiku +7.1pp, t = 4.8; Luna +3.4pp, t = 2.6). **(3) A
matched-occupation placebo decomposition shows what drives it**: parenthood net
of a personal-disclosure placebo (−.07 to −.23) and the family bundle on top of a
labeled leave (−.08 to −.24) are large and Holm-surviving in all 24 model×set
tests; the caregiving *label* never adds a penalty, and for two models
"Parental leave" is modestly *less* costly than an identically-dated "Career
break — extended travel" (+.02 to +.08). **(4) There is no fatherhood bonus anywhere**; only
Claude Haiku 5.5 penalizes mothers more than fathers in same-gender comparisons
(Holm-corrected), with the asymmetry concentrated in perceptions (commitment,
likability) more than choices for other models. **(5) Explicit gender activates
vendor-specific preferences**: Qwen stays at parity in direct woman-vs-man
choices at every level (all |t| ≤ 0.4); Luna's mother-vs-father preference rises
from .58 (names) to .65 (explicit field; L1−L0 = +6.9pp, t = 6.6); Haiku's falls
by 4.6pp (t = −3.3) to parity. **(6) Haiku withholds salary offers entirely for
19.8% of pregnant applicants (27.5% under an explicit field) — and withheld
applicants are interviewed only 30% of the time**, a −9.4pp net interview
penalty (t = −4.8) invisible to scoring audits that treat missing outputs as
missing data. On pay and hire margins these models *reduce* the human laboratory
motherhood penalty (≈ −$11,000 ≈ −7.4%; Correll et al. 2007) to −1.7% to −2.3%,
while redistributing it into comparative decisions, ranking composition, and
abstention. Effective sample sizes are smaller than call counts imply: all
inference clusters on résumé pairs (E2), résumés (E1/E4), or occupations (E3).

## 1. Introduction

Automated résumé screening is among the most commercially deployed uses of large
language models, and among the most regulated. The canonical account of hiring
discrimination against mothers — Correll, Benard & Paik (2007) — describes a
*status-based* penalty: motherhood triggers a competence/commitment discount
applied to women specifically (a 37-point hire-rate gap and an ≈ $11,000 salary
penalty in the laboratory), with no parallel fatherhood penalty; Benard &
Correll (2010) further showed the penalty survives direct evidence of
commitment — a *normative* component. Whether LLM hiring tools reproduce that
gendered penalty, a gender-neutral caregiver penalty, or no penalty at all is an
empirical question with direct regulatory consequences (EEOC Uniform Guidelines'
four-fifths rule; EU AI Act high-risk-system testing).

Prior LLM hiring audits have established single pieces of the picture: pairwise
gender-choice tests across 22 models (Rozado 2025), large-scale résumé scoring
(An et al. 2025), ranking designs (Yin et al. 2024; Frermann et al. 2023),
pregnancy and parental-leave cues (Veldanda et al. 2023; Frermann et al. 2023),
name-frequency sensitivity (Wilson & Caliskan 2024), and generator-side
distortions (Armstrong et al. 2024). None, to our knowledge, crosses **tasks ×
cues × gender-information regimes on identical materials with cue-validation
and a gender-perception manipulation check**, which is what identifying *where*
and *why* the penalty lives requires. Our contribution is that crossing:

- **Q1 (margin).** Where does the penalty live — scores, choices, rankings, or abstention?
- **Q2 (content).** Is it about being a woman, being a parent, or having interrupted employment?
- **Q3 (moderation).** Does it depend on gender information, occupation, or job-ad wording?

## 2. Design overview

### 2.1 Models and governance

Four deployed consumer models via OpenRouter, pinned to dated slugs and single
endpoints (never `*-latest`; Claude/Anthropic, GPT-6/OpenAI, Qwen/Alibaba
first-party; DeepSeek pinned to DeepInfra fp8 after first-party routing was
blocked by account guardrails — QUESTIONS.md §2b): reasoning disabled, JSON
mode, per-call logging with provider attribution, deterministic and resumable
plans, append-only ledger, hard budget $200 (reserve $20). Total: 602,093 logged
calls, $160.48 spent. All materials pass a phrase-level cue validator (no
family/gender/PII wording in base résumés) and a merit pretest.

### 2.2 Materials

- **Occupations.** Main run (O20): 20 occupations on a gender-composition ×
  wage grid (female share 4.7%–97.1%, BLS CPS Table 11; median wage, OEWS;
  O*NET time-demands composite). Phase 3 adds O8: 8 occupations chosen by
  exhaustive quota-constrained search over O*NET work-activity composites to
  break the care↔female-share confound (childcare worker, electrician,
  EMT/paramedic, health-services manager, housekeeper, police officer, security
  guard, veterinarian; female-share–care correlation .53 → .32; Appendix A).
- **Résumés.** 154 validated (28 anonymized Kaggle-derived + O*NET-grounded
  synthetic; contiguous 8–12-year histories; no gender/family/PII wording).
  Two unqualified attorney résumés detected and replaced by qualified
  J.D./bar-admitted attorneys (fit 3.3 → 9.2), affected cells re-run.
- **Names.** Six gendered, White-coded first names per gender (Bertrand &
  Mullainathan 2004 list, validated in Gaddis 2017), rotating within every
  cell; three shared surnames; race held constant throughout.

### 2.3 Family-status cues (within-résumé)

All cues render identically across genders; a cover note is present in every
condition.

| code | cover note | résumé change |
| --- | --- | --- |
| `none` (baseline) | "excited to be applying" | — |
| `parent` | "married with two children" | PTA volunteer line |
| `parent_gap` | " + leave | 8-month *Parental leave* entry; later dates shifted |
| `parent_committed` | " + objective commitment bullets |
| `pregnant` (women only) | "currently pregnant" | — |
| `personal` *placebo* | marathon/hobby line | shelter-volunteer line (length-matched) |
| `gap_travel` *placebo* | neutral | 8-month *Career break — extended travel*, same dates |
| `gap_parental_only` *placebo* | neutral | 8-month *Parental leave*, no children line, no PTA |

This ladder identifies disclosure alone (`personal`), the interruption
(`gap_travel`), the caregiving label (`gap_parental_only` − `gap_travel`), and
the family bundle (`parent_gap` − `gap_parental_only`).

### 2.4 Gender-information regimes (phase 3)

Four cue levels: **L0** gendered first name; **L1** name + header line
"Gender: Female/Male"; **L2** gender-neutral initial + the same field; **L3**
initials only — fully gender-blind. A manipulation check combines a *direct
question* (perceived gender) with an *implicit* check (pronoun congruence in
free-text rationales; §4.1). Direct woman-vs-man choice pairs (same family
status on both sides, roles and screen positions rotated) measure gender
preference at L0–L2.

### 2.5 Tasks

- **E1 scoring**: one candidate; fit (1–10), interview, salary, 1–7 ratings.
- **E2 pairwise choice**: two finalists, one childless one cued; P(cued chosen);
  parity = .50.
- **E3 ranking**: pools of six with a token parent (role and gender rotated by
  a margin-balanced design); top-3 shortlisting vs the same résumés shown
  childless (résumé fixed effects).
- **E4 job-ad wording**: leave-gap penalty under base / EEO / family-friendly /
  greedy wording (résumé-FE difference-in-differences).

### 2.6 Inference

Every estimate is within-résumé. SEs are clustered where stimuli repeat: E1 by
résumé; E2 by résumé pair (mean of pair-cluster means, t vs parity, df = 39;
naïve binomial z-tests would overstate precision several-fold); E3 by
occupation with résumé and position fixed effects; E4 by résumé. Holm
correction within each test family (gender differences; decomposition
components; direct-gender cells). Strict validity (nothing clamped):
out-of-range responses are parse failures; condition-correlated invalidity
(Qwen's E2 scale overflow, ~23% of its E2 calls raw) is handled by logged,
`repair_of`-linked repair passes (final main-run validity 99.91% / 98.99% /
98.95% / 99.83% for DeepSeek / Haiku / Luna / Qwen; phase-3 100% / 100% / 100% /
99.98%), and every headline estimate is re-computed on strict-validity samples
excluding any call whose valid response came from a repair. Refusals and salary
withholding are analyzed as outcomes. Effective sample sizes: E2 cells rest on
40 résumé-pair clusters (O20) or 32 (O8) despite thousands of calls.

## 3. Preregistration status

The main-run design (SPEC.md) and phase-3 addendum (SPEC_PHASE3.md) with
analysis plans were specified in advance in the project proposal and committed
before each paid run; two documented deviations (DeepSeek endpoint substitution;
replacement of clinical psychologists — whose CPS female share is suppressed —
with health-services managers) were researcher-approved before execution. This
is a prospective internal audit, not an OSF-registered report; exploratory
analyses are labeled as such.

## 4. Results

### 4.1 What the models know about gender: direct question vs. implicit use

The direct manipulation check ("what is the most likely gender of this
applicant? female/male/unknown") shows explicit fields are answered perfectly
(**100%** correct at L1/L2 for all models, n = 336 each) but gendered names are
answered "unknown" often — by Luna (34%) and Haiku (58%) in particular. This
does **not** mean those models fail to read names. In the *implicit* check —
gendered pronouns in free-text E1 rationales — every model that genders the
candidate does so correctly: among rationales containing gendered pronouns,
congruence with the name/field is **100%** for all four models at L0–L2 (usage
rates 5–26% at L0: DeepSeek 8%, Haiku 7%, Luna 22%, Qwen 16%; 0.7–7.9% at L2).
Under blind rendering, gendered pronouns nearly vanish (≤ 0.6%), so blind
packets are not being silently gendered either.

So the direct question measures **willingness to state gender**, itself an
interesting alignment behavior (Haiku declines to label what it demonstrably
uses), not legibility; and gendered names are legible to all four models.
Throughout, L1/L2 are therefore interpreted as *certifying* gender knowledge
the models already have at L0, and the L3 blind condition as genuinely removing
it.

### 4.2 The penalty is task-dependent (Q1)

**Scoring (E1).** Women, cue-cell minus childless-cell (same résumé, occupation,
model):

| model | fit: parent | fit: leave-gap | interview: parent | interview: gap | salary: parent |
| --- | --- | --- | --- | --- | --- |
| DeepSeek | −0.13 | −0.35 | +1.1pp | −1.5pp | −$933 |
| Haiku | **+0.34** | +0.14 | +1.2pp | 0.0pp | −$252 |
| Luna | −0.08 | −0.25 | +0.3pp | +0.6pp | +$412 |
| Qwen | −0.02 | −0.14 | +0.7pp | −1.1pp | −$1,150 |

Interview rates sit at 95–100% in most cells (a ceiling that limits this
outcome's variance); fit and salary are the informative scoring margins, and
both are small.

**Choice (E2).** The same models, cues, résumés — two finalists at a time.
P(cued candidate chosen) vs the childless candidate in the same prompt (parity
.50; t over 40 résumé-pair clusters; every cell |t| ≥ 5):

| contrast | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| parent — mother | .357 | .233 | .297 | .387 |
| parent — father | .349 | .276 | .294 | .398 |
| + committed — mother | .419 | .266 | .228 | .407 |
| + leave gap — mother | .310 | **.110** | .186 | .230 |
| + leave gap — father | .308 | .130 | .184 | .256 |

Pooled, mothers with the plain parent cue are chosen 33.7% of the time (−16.3pp
below parity); with a leave gap, 23.2% (−26.8pp). Between-model heterogeneity is
large (I² = 91–95%): the same cue costs −11pp (Qwen) to −27pp (Haiku).

**Ranking (E3).** One token parent in a pool of six; top-3 shortlisting of the
same résumés shown childless (résumé-FE adjusted impact ratios; four-fifths
line = .80):

| model | mothers | fathers | t |
| --- | --- | --- | --- |
| DeepSeek | .71 | .70 | −4.5 / −4.7 |
| Haiku | **.25** | **.23** | −8.4 / −9.8 |
| Luna | .78 | .81 | −2.8 / −4.1 |
| Qwen | .75 | .80 | −4.7 / −4.9 |

The scoring-vs-choice contrast is the first headline: **the penalty lives in
the comparison, not the score.** A single-résumé audit would certify all four
models as essentially fair.

### 4.3 What the penalty is about (Q2): interruption + family bundle

Phase-3 placebo decomposition on **matched occupation sets** (all contrasts
present: O8 at each level; O20 at L1/L2), computed as pair-matched differences
of résumé-pair cluster means with t-tests across pairs and Holm correction
within model. Range across the six matched sets; mothers (fathers and pooled
give the same structure):

| component (comparator) | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| parenthood net of disclosure (`parent` − `personal`) | −.10 to −.12 (t −4.2 to −8.2; 6/6 H ✓) | −.16 to −.23 (t −5.3 to −8.7; 6/6 H ✓) | −.07 to −.13 (t −3.2 to −6.0; 6/6 H ✓) | −.07 to −.10 (t −4.0 to −5.0; 6/6 H ✓) |
| caregiving label (`gap_parental_only` − `gap_travel`) | −.01 to +.03 (all n.s., 0/6) | −.03 to +.02 (all n.s., 0/6) | **+.02 to +.07 (H ✓ in 5/6 sets)** | **+.04 to +.08 (H ✓ in 6/6 sets)** |
| family bundle (`parent_gap` − `gap_parental_only`) | −.08 to −.12 (t −3.0 to −9.6; 6/6 H ✓) | −.17 to −.24 (t −5.0 to −8.8; 6/6 H ✓) | −.10 to −.16 (t −3.0 to −5.2; 6/6 H ✓) | −.08 to −.12 (t −3.7 to −7.3; 6/6 H ✓) |

Reading: a personal-disclosure placebo line costs almost nothing. The
8-month interruption plus the explicit family bundle carry the penalty, and
both components are large and correction-surviving for every model. The
*caregiving label* never adds a penalty for any model — and for Luna and Qwen
an interruption labeled *Parental leave* is modestly **less** costly than the
identically-dated *Career break — extended travel* (a recognized reason beats
an unexplained one); DeepSeek and Haiku are indifferent to the label.

**Gender-information invariance (pair-matched tests, O8, 32 pairs).**
P(parent chosen), names (L0) minus blind (L3): DeepSeek +.006 (t 0.3), Haiku
−.005 (t −0.3), Luna −.013 (t −1.2), Qwen +.003 (t 0.2) — **no model's parent
penalty changes when all gender information is removed** (same for the leave-gap
cue: all |t| ≤ 1.8, p ≥ .08). Explicit gender *fields* are a different
intervention: L1 − L0 *softens* the plain-parent penalty for Haiku (+.071,
t = 4.8) and Luna (+.034, t = 2.6), with no effect for DeepSeek or Qwen — an
alignment-driven partial offset, not amplification. E3 ranking replicates the
invariance (top-3 ratios across L0–L3: DeepSeek .64/.66/.66/.65, Haiku
.15/.19/.17/.16, Luna .70/.72/.70/.71, Qwen .68/.71/.74/.71).

### 4.4 No fatherhood bonus; where the mother-specific penalty lives

Fathers are below parity in every cell of every model (e.g., leave-gap fathers
.308/.130/.184/.256) — no fatherhood bonus exists in any task.
Mother-minus-father differences are ≈ 0 in choice for DeepSeek and Luna,
nominal-but-not-Holm-surviving for Qwen, and significant for Haiku (parent
−.043, Holm p = .037; committed −.065, Holm p = .001). Decomposing the
mother-father gap by outcome (main run, parent cue; mothers' minus fathers'
within-cue penalty):

| outcome (comparator) | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| E2 choice (P(parent chosen), M − F) | +.006 | **−.044** | −.004 | −.008 |
| E2 salary (paired $ diff, M − F) | +$147 | −$248 | −$397 | −$37 |
| E2 commitment (paired rating diff, M − F) | +.02 | **−.14** | −.01 | −.01 |
| E2 likability (M − F) | +.04 | **−.10** | +.04 | +.01 |
| E1 interview gap (parent − none, M − F) | −.006 | +.010 | +.003 | −.018 |

The pattern is **perception-asymmetric, decision-symmetric**: for three models,
mothers' extra penalty (where any exists) appears in perceived commitment,
likability, and salary — not in the choice itself; Haiku is again the exception,
gendering both perception and decision. This mirrors Benard & Correll's (2010)
finding that the human penalty migrates to new margins (warmth, likability)
rather than disappearing when commitment is established.

### 4.5 Explicit gender: vendor divergence in direct preference

Direct woman-vs-man choices (same family status both sides; parity .50;
pair-clustered t, n = 112 pairs; Holm over the six cells per model):

| model | cell | names (L0) | field (L1) | initials+field (L2) |
| --- | --- | --- | --- | --- |
| Qwen | childless / parent | .503 / .504 | .495 / .513 | .517 / .490 |
| DeepSeek | childless / parent | .514 / .536 | .541 / .540 | .537 / .548 |
| Luna | childless / parent | .522 / .577 | .587 / **.646** | .575 / **.634** |
| Haiku | childless / parent | .528 / .546 | .526 / .500 | .513 / .470 |

Qwen is exactly at parity everywhere (all |t| ≤ 0.4) — genuinely gender-neutral
in choice. DeepSeek shows a small, never-significant pro-woman tilt (+1.4 to
+4.8pp). **Luna** is the strong case: its mother-vs-father preference rises
from .577 (names) to .646 with the explicit field — the L1 cell differs from
parity (t = 4.3, Holm p = .0002) and the level contrast L1 − L0 is +6.9pp
(t = 6.6; childless +6.5pp, t = 5.6). **Haiku** moves the other way: from a
nominal pro-mother tilt to below parity — the level contrast L1 − L0 is
**−4.6pp (t = −3.3)**, though no Haiku cell individually differs from parity.
Explicit gender fields — standard in many markets and encouraged by some
transparency policies — are therefore not neutral: they activate vendor-specific
preferences that name-only screening conceals.

### 4.6 Abstention: withholding offers as a discrimination margin

**Haiku withholds salary entirely (returns $0) for pregnant applicants**: 19.8%
in the main run (names only; 3.1% for childless women, 7.3% married), rising to
**27.5%** with an explicit gender field (25.7% under initials+field). Other
models abstain far less on pregnancy: Luna 3.1% (main run) and ≤ 0.2% (phase 3),
Qwen 5.8% (main run) and 1.4–2.9% (phase 3, by level), DeepSeek ≤ 2.0%. No model
exceeds 3.1% withholding in any non-pregnancy cell. Withholding is not benign:
withheld pregnant applicants are advanced to interview only **29.9%** of the
time (vs 100% when a salary is named), producing a net within-résumé interview
penalty of **−9.4pp (t = −4.8)** relative to childless women. Among *scored*
offers, no model shows a meaningful pregnancy salary penalty (−0.8% at most).
Rationales frame the withholding as protective ("salary should not depend on
pregnancy"), yet the downstream result is that one in five pregnant applicants
receives neither a price nor an interview. Audits that treat missing outputs as
missing data will score Haiku's abstention period as its fairest.

### 4.7 Salary and the human benchmark

E2 paired salary, mother minus her paired childless woman (withheld excluded):
DeepSeek −$1,854 (−2.19%), Haiku −$1,332 (−1.68%), Luna −$1,548 (−1.66%), Qwen
−$1,775 (−2.33%); leave-gap −$942 to −$3,145. Against Correll et al.'s
laboratory benchmark (≈ −$11,000 ≈ −7.4%; 84% vs 47% hire recommendation), the
LLM salary penalty is roughly one-quarter the human one, and the choice penalty
(−16 to −27pp) is smaller than the human 37pp hire-rate gap. Directionally,
these deployed models *reduce* the classic motherhood penalty on pay and hire
margins while redistributing it into shortlist composition, comparative
rejection, and abstention. (Directional only: a within-pair choice share is not
metrically a between-persons hire rate; we drop standardized effect-size
comparisons for that reason.)

### 4.8 Job-ad wording (E4)

Varying only the JD's closing paragraph (résumé-FE DiD vs base wording, 32
résumé clusters): **greedy** wording — *"This is a fast-paced role. Candidates
must be available after hours and on weekends as needed, and travel up to 40%
of the time."* — adds a significant extra interview penalty to leave-gap
mothers for DeepSeek (−2.7pp, t = −2.3) and, combined with family-friendly
language, for DeepSeek both genders (−5.2/−6.0pp) and Haiku mothers (−8.0pp,
t = −2.8). Family-friendly sentences *alone* never significantly help and often
slightly hurt; **EEO boilerplate has no effect in any model**. The greedy
signal, not the diversity signal, moves behavior.

### 4.9 Occupational moderation (exploratory)

With 28 occupations and female share separable from task composites, we regress
occupation-level leave-gap penalties on standardized female share, wage, and
O*NET physical/care/analytic/manage (24 tests across 4 models × 6 regressors,
uncorrected). Female share carries a positive sign in all four models but is
nominally significant only for DeepSeek (+.057, p = .025); Luna's care
composite is −.058 (p = .05). We read this as hypothesis-generating only: the
main run found no moderation, the corrected evidence here is one nominally
significant coefficient, and the sign pattern is not specific to mothers (it
appears for fathers too). Occupational moderation remains unresolved at this
sample size.

### 4.10 Robustness

**Drift.** The designed E2 anchor (parent cue, L0, O20 minus the re-run lawyer
occupation) moves +.008 to +.024 across models and genders — within the
pre-registered ±.03 flag everywhere. E1 interview-rate anchors move +1.1 to
+3.5pp (one of four models' cells crosses .03). Prompt versions differ between
main-run and phase-3 tables; all headline comparisons are within-run.
**Validity.** Final main-run validity 99.91% / 98.99% / 98.95% / 99.83%
(DeepSeek / Haiku / Luna / Qwen) after logged repair passes; phase-3 validity
100% / 100% / 100% / 99.98%. Qwen's condition-correlated E2 overflow is
analyzed under both strict validity and repair-recovered samples; conclusions
are unchanged. **Materials.** Replacing the two unqualified attorney résumés
(fit 3.3 → 9.2) converted near-arbitrary lawyer-pair choices (.38 mothers/.43
fathers) into measurable penalties (.21/.08). **Position bias** (main-run E2,
per model): Luna near-neutral (P(A) = .53), Qwen .58, DeepSeek .68 prefer the
first slot; Haiku prefers the second (.39). All positions counterbalanced.
**Names**: six per gender rotated within every cell (name-frequency sensitivity
documented by Wilson & Caliskan 2024); paraphrase templates balanced.

## 5. Discussion

### 5.1 What kind of discrimination is this?

The human motherhood penalty in the status-characteristics tradition is
*mother-specific*. What we find in deployed LLMs is structurally different, and
the placebo decomposition splits it into two components. The **interruption
component** — an identically-dated break costs the same (or more, for two
models) labeled *travel* as labeled *parental leave*, and the whole penalty is
invariant to removing gender information entirely — behaves like **availability
inference**: the model reads a recent employment gap, whatever its stated
reason and whoever the candidate, as risk in a pairwise or ranking contest.
The **bundle component** — children lines and PTA activity penalized a further
.09–.24 *on top of* the interruption, for fathers as much as mothers — does not
fit that account, and neither does the fate of objective commitment evidence,
which only partly restores parity (and *deepens* the penalty for Luna). This is
the signature of a **normative component** (Benard & Correll 2010): overt
family signals are penalized as such, not merely as availability proxies.

Layered on this common structure are **vendor-specific gender components**:
Haiku adds the only mother-specific choice penalty (plus pregnancy abstention
and its interview denial, and an anti-mother shift under explicit gender);
Luna adds a strong pro-woman preference that only activates when gender is
explicit; Qwen adds nothing gendered at all. There is no single "LLM bias":
four deployed models realize different preference structures over identical
materials — vendor choice is itself a bias decision.

### 5.2 Implications for auditing and regulation

Three design mandates follow. **First, audits must be comparative.** Every
headline effect is invisible or near-zero in single-résumé scoring; pairwise
choice and pool ranking — what actual screening systems do — carry 10–27pp
penalties. **Second, abstention must be an outcome.** The largest pregnancy
effect is a refusal to price that carries a real interview denial; listwise
deletion would miscount it as fairness. **Third, gender knowledge must be
manipulated and *measured implicitly*, not assumed.** Direct questions measure
willingness to state gender; pronoun use shows all four models read names
correctly. An audit standard that varies only names (the correspondence-study
inheritance) or only asks models to state gender will mischaracterize what the
system knows.

For deployment: EEO boilerplate does nothing; greedy availability language
amplifies the penalty; explicit gender fields change behavior for two of four
vendors in opposite directions; and vendor choice moves the penalty by a factor
of two to eight.

### 5.3 Limitations

Materials are US-market, English-language, text-only (photo study designed, not
run), race held constant — nothing identified about race intersections.
"Pregnancy" has no male analogue. Salary and interview are recommendations, not
negotiated outcomes or callbacks. Occupational moderation is exploratory.
Models are consumer endpoints of four vendors at pinned versions; behavior may
differ across versions, system prompts, and retrieval contexts. Pools and pairs
are synthetic by construction — the design identifies marginal cue effects, not
population hiring rates. The human benchmark is a 2007 laboratory study,
compared directionally only. Effective sample sizes are constrained by design
clustering (40/32 résumé pairs per E2 cell).

## 6. Conclusion

Deployed LLM hiring tools do not so much inherit the human motherhood penalty
as **redistribute** it. Where an applicant sees a score, they are nearly fair.
Where systems compare, shortlist, and price, they impose a large,
precisely-estimated penalty on caregivers — fathers included — split between an
availability inference over employment interruptions and a normative penalty on
overt family signals, largely indifferent to the candidate's gender but with
vendor-specific gendered exceptions and one vendor's pregnancy-driven
abstention. Audit regimes that stop at single-résumé scoring, ignore abstention,
or assume name-based gender manipulations, will certify as fair systems that
are not.

## References

- An, Z., et al. (2025). Large language models perceive their own and others'
  gender identities... résumé-screening experiments. *PNAS Nexus*. (Scoring;
  ~361,000 randomized résumés, 5 models.)
- Armstrong, A., et al. (2024). Do LLMs exhibit gender or racial biases in
  résumé screening? arXiv:2405.04412.
- Benard, S., & Correll, S. J. (2010). Normative discrimination and the
  motherhood penalty. *Gender & Society*, 24(5), 616–646.
- Bertrand, M., & Mullainathan, S. (2004). Are Emily and Greg More Employable
  Than Lakisha and Jamal? *American Economic Review*, 94(4), 991–1013.
- Correll, S. J., Benard, S., & Paik, I. (2007). Getting a Job: Is There a
  Motherhood Penalty? *American Journal of Sociology*, 112(5), 1297–1338.
  [Salary benchmark quoted as ≈ $11,000 ≈ −7.4%, the commonly cited figure;
  verify against paper tables before journal submission.]
- EEOC (1978). Uniform Guidelines on Employee Selection Procedures, 43 FR 38290.
- European Union (2024). Regulation (EU) 2024/1689 (AI Act).
- Frermann, A., et al. (2023). Do LLMs exhibit gender/parental-leave bias in
  ranking? University of Melbourne working paper. [Gender × parental-leave gap
  ranking study; full citation to be verified before submission.]
- Gaddis, S. M. (2017). How Black Are Lakisha and Jamal? Racial Perceptions
  from Names Used in Correspondence Audit Studies. *Sociological Science*, 4,
  469–489.
- Kleinberg, J., & Raghavan, M. (2021). Algorithmic monoculture and social
  welfare. *PNAS*, 118(22).
- Rozado, D. (2025). LLMs gender bias in hiring — pairwise CV experiments
  across 22 models and 70 professions. arXiv:2505.17049.
- Veldanda, A., et al. (2023). LLM screening bias: gender, race and pregnancy
  on 334 résumés. arXiv:2310.05135.
- Wilson, C., & Caliskan, A. (2024). Gender, race, and name-frequency bias in
  résumé-ranking language models. arXiv:2407.20371.
- Yin, K., et al. (2024). Bloomberg's GPT hiring-racial-discrimination
  investigation (ranking design).

## Appendices

- **A. Occupation design (O8)**: `docs/report/occupation_design.md`.
- **B. Manipulation check**: `docs/phase3/manipulation_check.md` (direct) and
  §4.1 (implicit pronoun check; `round3_stats.json`).
- **C. Phase-3 tables**: `docs/phase3/CROSS_MODEL.md`; per-model
  `report_<model>.md`; `phase3_key_stats.json`; round-3 tests `round3_stats.json`.
- **D. Main-run tables**: `docs/report/tables.md` (programmatic).
- **E. Reproducibility**: pinned slugs/configs, frozen materials, deterministic
  plans, append-only logs and ledger ($160.48); regenerate with `uv run audit
  stats`, `uv run python -m audit.analysis.{cross_model,phase3_key_stats,round3}`,
  `uv run audit figures`. Decisions and deviations: QUESTIONS.md.
- **F. Figures**: `docs/report/figures/fig1–fig8` (main run).
