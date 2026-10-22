# From Motherhood Penalty to Caregiver Penalty: How LLM Résumé Screeners Treat Family Signals

*Draft 5.0 (rounds 4–5 revisions), 2026-10-22. Every statistic is generated from
run logs — main run: `uv run audit stats` → `stats.json`, `tables.md`; phase 3:
`audit.analysis.{phase3_key_stats,cross_model,round3,round5}` →
`phase3_key_stats.json`, `CROSS_MODEL.md`, `round3_stats.json`,
`round5_stats.json`. No hand-typed numbers.*

## Abstract

Language models increasingly assist résumé screening, but audits typically vary
one design dimension at a time. We cross three — **decision task** (scoring,
pairwise choice, pool ranking), **family cue** (disclosure, employment
interruption, caregiving label, family bundle), and **gender-information regime**
(gendered names, explicit gender field, initials, fully blind) — on identical
validated materials (28 occupations, 154 résumés, six rotating names per gender;
602,093 logged calls; DeepSeek V4.1 Flash, Claude Haiku 5.5, GPT-6 Luna, Qwen
3.8 Flash at pinned versions). **Finding 1 — the penalty appears only in
comparison.** In isolated scoring, family cues move fit ratings by at most 0.35
points (10-point scale) and interview recommendations by at most 1.5pp. In
pairwise choice, the same cues cost parents 10–27 percentage points (pp) of
choice probability: a parent with a parental-leave gap wins a head-to-head
final against a comparably qualified childless candidate (résumé roles
counterbalanced) only 11–31% of the time, where 50% means no penalty; the same
résumé is shortlisted at 23–81% of its childless rate. A noise model fitted to
the scoring data predicts choice shares 8–41pp fairer than observed — the
comparison itself adds penalty that scores do not contain. **Finding 2 — the
penalty is a caregiver penalty, not a gender penalty.** Removing all gender
information (blind rendering) leaves the parent-choice penalty unchanged in
every model (pair-matched tests, all p ≥ .08). A matched-occupation placebo
decomposition shows the 8-month employment interruption and the explicit family
bundle each cost 7–24pp (Holm-corrected, 23 of 24 model×set tests), while the
*label* of the interruption never adds a penalty — for three models, "Parental
leave" is modestly *less* costly than the identical dates labeled "Career
break — extended travel." There is no fatherhood bonus anywhere. **Finding 3 —
thin, vendor-specific gendered behaviors layer on top.** In direct
woman-vs-man choices, Qwen is at parity at every gender-information level;
DeepSeek shows a small robust pro-woman preference (+3.6 to +4.8pp,
Holm-corrected); Luna's pro-woman preference activates only when gender is
explicit (.58 → .65 for mother-vs-father); Haiku shifts the other way (−4.5pp,
p = .003) and is the only model that penalizes mothers more than fathers in
same-gender pairs — concentrated in perceived commitment. **Finding 4 —
abstention is a discrimination margin.** Haiku withholds salary offers entirely
for 19.8% of pregnant applicants (27.5% under an explicit gender field), and
withheld applicants are interviewed only 30% of the time — a −9.4pp interview
penalty (t = −4.8) that listwise deletion would misread as fairness. Because
caregiving gaps and family signals are carried disproportionately by women in
real applicant pools, a gender-neutral-in-form rule is not gender-neutral in
effect. Single-résumé audits would detect only the small effects; the
decision-relevant penalties are comparative. Effective sample sizes reflect
design clustering (40 or 16 résumé pairs per E2 cell), not call counts.

## 1. Introduction

Automated résumé screening is among the most commercially deployed uses of
large language models, and among the most regulated. Whether LLM hiring tools
reproduce the human motherhood penalty is an empirical question with direct
regulatory consequences (EEOC Uniform Guidelines' four-fifths rule; EU AI Act
high-risk-system obligations). The human benchmark is well characterized:
mothers are rated as less competent and committed, recommended for hire less
often, and offered less money, with no parallel fatherhood penalty (Correll,
Benard & Paik 2007); the penalty persists when mothers present direct evidence
of commitment, migrating instead to warmth and likability — a normative
component (Benard & Correll 2010). Organizations are built around an
unencumbered "ideal worker" (Acker 1990; Williams 2000), and men who signal
caregiving are punished too — the flexibility stigma (Rudman & Mescher 2013;
Williams, Blair-Loy & Berdahl 2013). Separately, employment gaps themselves
attract employer penalties in audit and experimental studies (Weisshaar 2018;
Kroft, Lange & Notowidigdo 2013).

Prior LLM hiring audits have established single pieces of this picture: pairwise
gender-choice tests (Rozado 2025), large-scale scoring (An et al. 2025),
ranking designs (Yin, Alba & Nicoletti 2024; Frermann et al. 2023), pregnancy
and parental-leave cues (Veldanda et al. 2023; Frermann et al. 2023),
name-frequency sensitivity (Wilson & Caliskan 2024), and generator-side
distortions (Armstrong et al. 2024). None crosses **tasks × cues ×
gender-information regimes on identical materials**, with cue validation, a
gender-perception check, and inference clustered at the design's actual units —
which is what identifying *where* the penalty lives and *what it is about*
requires. We ask:

- **Q1.** Where does the family-status penalty appear — scores, choices, rankings, or abstention?
- **Q2.** Is it about being a woman, being a parent, or having interrupted employment?

The answer that emerges is a two-layer account. **Layer 1** is a
caregiving/ideal-worker penalty shared by all four vendors in sign: gender-blind,
driven by the employment interruption and overt family signals, hidden in
single scores and exposed in comparisons, and amplified when a job ad makes the
ideal-worker norm salient. **Layer 2** is a thin, vendor-specific gender layer
that surfaces mainly when gender is made explicit — one model's pro-woman
preference, another's mother-specific penalty and pregnancy abstention.

## 2. Design

### 2.1 Models and governance

Four deployed consumer models via OpenRouter, pinned to dated slugs and single
endpoints (never `*-latest`; first-party endpoints except DeepSeek, pinned to
DeepInfra fp8 after first-party routing was blocked by account guardrails —
QUESTIONS.md §2b). Configuration: reasoning disabled, JSON mode, no system
prompt (consumer default), temperature default. **Population of inference**:
high-volume, low-cost screening configurations; real HR tools typically add
system prompts (often with fairness instructions) and may use larger models —
both are untested here. Every call is logged with provider attribution; plans
are deterministic and resumable; the ledger is append-only under a hard $200
budget (reserve $20). Total: 602,093 logged calls, $160.48 spent.

### 2.2 Materials

- **Occupations.** Main run (O20): 20 occupations on a gender-composition ×
  wage grid (female share 4.7%–97.1%, BLS CPS Table 11; median wage, OEWS;
  O*NET time-demands). Phase 3 adds O8, chosen by exhaustive quota-constrained
  search over O*NET work-activity composites to break the care↔female-share
  confound (childcare worker, electrician, EMT/paramedic, health-services
  manager, housekeeper, police officer, security guard, veterinarian;
  female-share–care correlation .53 → .32; Appendix A).
- **Résumés.** 154 validated (28 anonymized Kaggle-derived + O*NET-grounded
  synthetic; contiguous 8–12-year histories; no gender/family/PII wording).
  Two unqualified attorney résumés were detected and replaced by qualified
  attorneys (pretest fit 3.3 → 9.2), affected cells re-run.
- **Names.** Six gendered, White-coded first names per gender (Bertrand &
  Mullainathan 2004 list; Gaddis 2017), rotating within every cell; three
  shared surnames; race held constant.

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

The ladder identifies disclosure alone (`personal`), the interruption
(`gap_travel` vs parity), the label (`gap_parental_only` − `gap_travel`), and
the family bundle (`parent_gap` − `gap_parental_only`). One caveat travels with
this design: "extended travel" is a *recognized but leisure-coded* reason; if
models read it as low seriousness, label comparisons understate the cost of
other unrecognized gaps and overstate the neutrality of "Parental leave"
(§5.3). The cues are also deliberately strong and explicit — US applicants
rarely write "married with two children" in a cover note — which suits
identification; the leave gap, the cue real résumés actually carry, is the most
ecologically valid and is the anchor of the decomposition.

### 2.4 Gender-information regimes (phase 3)

Four levels: **L0** gendered first name; **L1** name + header line
"Gender: Female/Male"; **L2** gender-neutral initial + the same field; **L3**
initials only — fully blind. Perception is checked both directly (asked gender)
and implicitly (pronoun congruence in rationales; §4.1). Direct woman-vs-man
choice pairs (same family status both sides, roles and positions rotated)
measure gender preference at L0–L2.

### 2.5 Tasks

- **E1 scoring**: one candidate; fit (1–10), interview, salary, four 1–7 ratings.
- **E2 pairwise choice**: two finalists, one childless one cued; P(cued chosen);
  parity = .50.
- **E3 ranking**: pools of six with a token parent (role and gender rotated by
  a margin-balanced design); top-3 shortlisting vs the same résumés shown
  childless (résumé fixed effects).
- **E4 job-ad wording**: leave-gap penalty under base / EEO / family-friendly /
  greedy wording (résumé-FE difference-in-differences).

### 2.6 Inference

Every estimate is within-résumé. SEs cluster at the design's actual units:
E2 by *unordered* résumé pair (40 clusters on O20, 16 on O8; t vs parity, df =
clusters − 1); E1 by résumé; E3 by occupation with résumé and position fixed
effects; E4 by résumé. Holm correction within each test family. Strict
validity (nothing clamped): Qwen's condition-correlated E2 scale overflow
(~23% of its E2 calls raw) is handled by logged `repair_of`-linked repair
passes (final validity: main run 99.91/98.99/98.95/99.83%; phase 3
100/100/100/99.98%), and headline estimates are re-computed on strict-validity
samples. Refusals and withholding are outcomes. Prompt versions differ between
main-run and phase-3 tables; each table below states its source.

## 3. Preregistration status

Designs and analysis plans (SPEC.md, SPEC_PHASE3.md) were specified in advance
in the project proposal and committed before each paid run; two documented
deviations (DeepSeek endpoint substitution; replacement of clinical
psychologists — CPS female share suppressed — with health-services managers)
were researcher-approved before execution. This is a prospective internal
audit, not an OSF-registered report; exploratory analyses are labeled.

## 4. Results

### 4.1 What the models know about gender: asked vs. used

**Asked directly, models differ in willingness to state gender; using it
implicitly, they all read names perfectly.** The direct check ("most likely
gender of this applicant? female/male/unknown") shows explicit fields answered
perfectly (100% at L1/L2, n = 336 each) and names answered "unknown" often —
by Luna (34%) and Haiku (58%). But in free-text E1 rationales, whenever a
model uses a gendered pronoun at L0–L2 it matches the name/field **100%** of
the time (usage 5–26% at L0; 0.7–7.9% at L2); under blind rendering gendered
pronouns nearly vanish (≤ 0.6%). The direct question therefore measures
*willingness to state* gender — itself an alignment behavior — not legibility.
L1/L2 certify knowledge the models already have at L0; L3 genuinely removes it.

### 4.2 The penalty appears only in comparison (Q1)

**Scores barely move; choices and rankings move a lot; a noise model shows
scores cannot account for choices.** Women, cue-cell minus childless-cell
(same résumé, occupation, model; main run):

| model | fit: parent | fit: leave-gap | interview: parent | interview: gap | salary: parent |
| --- | --- | --- | --- | --- | --- |
| DeepSeek | −0.13 | −0.35 | +1.1pp | −1.5pp | −$933 |
| Haiku | **+0.34** | +0.14 | +1.2pp | 0.0pp | −$252 |
| Luna | −0.08 | −0.25 | +0.3pp | +0.6pp | +$412 |
| Qwen | −0.02 | −0.14 | +0.7pp | −1.1pp | −$1,150 |

In pairwise choice (main run; P(cued chosen) vs the childless finalist in the
same prompt; parity .50; pair-clustered SEs give 95% CIs of ±.02–.07; no cell's
CI includes .50):

| contrast | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| parent — mother | .357 | .233 | .297 | .387 |
| parent — father | .349 | .276 | .294 | .398 |
| + committed — mother | .419 | .266 | .228 | .407 |
| + leave gap — mother | .310 | **.110** | .186 | .230 |
| + leave gap — father | .308 | .130 | .184 | .256 |

In plain terms: a mother with a leave gap loses roughly three of four
head-to-head finals she would need to split evenly. In pools of six (E3,
résumé-FE adjusted impact ratios; four-fifths line .80): DeepSeek .71 mothers /
.70 fathers; Haiku **.25 / .23**; Luna .78 / .81; Qwen .75 / .80 — the same
résumés shortlisted at 23–81% of their childless rate.

Two checks address the possibility that forced choice merely *amplifies* small
score differences (a tie-breaker) or that the integer scoring scale is too
coarse. **(a) Noise model.** Converting each model's E1 fit gap into a
predicted choice share via a probit with the E1 within-cell fit SD (σ =
0.94–1.23) predicts choice shares 8–41pp *fairer* than observed — e.g.,
DeepSeek parent .46 predicted vs .36 actual; Luna leave-gap .41 vs .19; Haiku,
whose E1 fit gap is *positive* (+.34), would be predicted to win 64% of finals
but wins 23%. **(b) Tie-breaker split.** The choice penalty is larger when the
two résumés' pretest qualities are near-ties (all eight model×cue cells,
t = −0.9 to −4.0), consistent with tie-breaking — but remains 9–32pp in
clear-gap pairs. Scoring differences, thresholded or not, do not explain the
comparative penalties.

### 4.3 What the penalty is about (Q2): interruption + family bundle, not gender

**A matched-occupation placebo decomposition (primary estimand: O20, L1+L2
pooled, 40 pairs, mothers) with the six-set robustness in the appendix:**

| component (comparator) | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| interruption itself (P(`gap_travel`) vs .50) | −10.6pp (t −8.2) | **−25.6pp** (t −9.9) | **−26.0pp** (t −7.4) | −22.6pp (t −9.1) |
| parenthood net of disclosure (`parent` − `personal`) | −10.4pp [−12.8, −8.0] (t −8.4) | −19.2pp [−23.4, −15.0] (t −8.9) | −12.1pp (t −5.7) | −6.8pp (t −4.1) |
| caregiving label (`gap_parental_only` − `gap_travel`) | +1.7pp [.5, 2.9] (t 2.8) | −1.1pp [−3.2, +.9] (t −1.1) | +6.5pp (t 4.6) | +6.7pp (t 7.5) |
| family bundle (`parent_gap` − `gap_parental_only`) | −10.5pp [−12.5, −8.4] (t −9.8) | −17.6pp (t −8.2) | −11.5pp (t −5.7) | −12.2pp (t −8.5) |

(95% CIs shown where the six matched-set ranges in Appendix C are summarized;
brackets are the primary-estimand CIs.) Disclosure alone is nearly free
(`personal` −3 to −4pp vs parity, t −4.1 to −4.6). The interruption itself —
an 8-month break labeled *travel* — costs 11–26pp. The *label* never adds a
penalty: Haiku is indifferent; DeepSeek shows a tiny positive (+1.7pp);
Luna and Qwen treat *Parental leave* as 6–7pp *less* costly than the same
dates labeled travel. The family bundle adds a further 10–18pp *on top of* a
labeled parental leave. In the six-set robustness (O8 at L0–L3, O20 at L1/L2
separately), parenthood and bundle survive Holm in 23 of 24 tests each; the
label is null for Haiku and positive for Luna (5/6 sets) and Qwen (6/6).

**Removing gender information changes nothing.** Pair-matched tests on O8
(16 pairs): P(parent chosen), names (L0) minus blind (L3): DeepSeek +.006
(t 0.3), Haiku −.005 (t −0.3), Luna −.013 (t −1.2), Qwen +.003 (t 0.2); the
leave-gap cue likewise (all |t| ≤ 1.8, p ≥ .08). Explicit gender *fields*
partially offset the plain-parent penalty for Haiku (+7.4pp, t 7.7) and Luna
(+3.4pp, t 3.0), with no effect on DeepSeek or Qwen. E3 ranking replicates the
invariance (top-3 ratios across L0–L3: .64/.66/.66/.65 DeepSeek;
.15/.19/.17/.16 Haiku; .70/.72/.70/.71 Luna; .68/.71/.74/.71 Qwen).

### 4.4 No fatherhood bonus; where a mother-specific penalty exists

**Fathers are penalized everywhere; only Haiku penalizes mothers more — and
the asymmetry lives mainly in perceptions.** Fathers sit below parity in every
cell of every model (leave-gap fathers .308/.130/.184/.256). Mother-minus-
father differences (main run; E2 pair-matched across unordered pairs, E1
résumé-matched; Holm within each contrast's family; parent cue):

| margin (comparator) | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| E2 choice, pp | +0.6 (t 0.6) | **−4.4 (t −3.2, H .02)** | −0.4 (t −0.4) | +0.1 (t 0.0) |
| E2 paired salary, $ | +138 (t 1.0) | −150 (t −1.4) | −109 (t −1.2) | −16 (t −0.1) |
| E2 commitment (paired rating) | +.02 (t 0.5) | **−.14 (t −4.3, H .0009)** | +.00 (t 0.1) | +.12 (t 1.1) |
| E1 commitment gap (cue − none) | **−.09 (t −3.1, H .03)** | **−.06 (t −3.8, H .002)** | +.03 (t 1.7) | +.00 (t 0.0) |

The pattern is *perception-asymmetric, decision-symmetric*: DeepSeek's only
mother-specific penalty is perceived commitment; Haiku's spans commitment,
likability, and choice; Luna and Qwen show none that survives correction.

### 4.5 Explicit gender: vendor-specific preferences

**Qwen is at parity everywhere; DeepSeek has a small robust pro-woman tilt;
Luna's pro-woman preference appears only when gender is explicit; Haiku's
disappears.** Direct woman-vs-man choices (same family status both sides;
parity .50; 56 unordered pairs; Holm over six cells per model; phase 3):

| model | cell | names (L0) | field (L1) | initials+field (L2) |
| --- | --- | --- | --- | --- |
| Qwen | childless / parent | .496 / .502 | .491 / .513 | .513 / .488 |
| DeepSeek | childless / parent | .514 / **.536** | **.540 / .541** | **.538 / .548** |
| Luna | childless / parent | **.522 / .578** | **.587 / .646** | **.575 / .634** |
| Haiku | childless / parent | **.528 / .544** | .526 / .498 | .513 / .471 |

(bold = Holm-corrected difference from parity.) Level contrasts: Luna jumps
+6.4 to +6.9pp when the field is added (t 5.7–6.6); Haiku moves −4.5pp on the
mother-vs-father contrast (t −3.1, p = .003), from a significant pro-mother
tilt at L0 (.544) to parity (.498) and below (.471). Explicit gender fields —
standard in many markets — are not neutral: they activate vendor-specific
preferences that name-only screening conceals.

### 4.6 Abstention: withholding offers as a discrimination margin

**One model withholds salary from pregnant applicants — and withholding
denies interviews.** Haiku returns $0 for **19.8%** of pregnant applicants in
the main run (childless women 3.1%; married 7.3%), rising to **27.5%** under an
explicit gender field. Other models abstain far less on pregnancy: DeepSeek
≤ 2.0%, Luna 3.1% (main run) and ≤ 0.2% (phase 3), Qwen 5.8% (main run) and
1.4–2.9% (phase 3); in non-pregnancy cells no model exceeds Haiku's own 7.3%
(married women) and most stay below 5%. Withheld pregnant applicants are
advanced to interview only **29.9%** of the time (vs 100% when priced),
producing a −9.4pp net interview penalty vs childless women (t = −4.8). Among
*scored* offers no model shows a meaningful pregnancy salary penalty (−0.8% at
most). Rationales frame withholding as protective; the downstream result is
that one in five pregnant applicants gets neither a price nor an interview.

### 4.7 Salary and the human benchmark

E2 paired salary, mother minus her paired childless woman (withheld excluded,
both offers present): DeepSeek −$1,854 (−2.19%), Haiku −$1,332 (−1.68%), Luna
−$1,548 (−1.66%), Qwen −$1,775 (−2.33%); leave-gap −$942 to −$3,145
(−1.2% to −4.1%). For context — not a metrically comparable estimate —
Correll et al.'s (2007) laboratory study found ≈ $11,000 (≈ −7.4%) between
childless women and mothers and an 84%-vs-47% hire recommendation; the LLM
salary penalties are roughly one-quarter that figure, and the choice penalties
(−10 to −27pp) are smaller than the 37pp human hire-rate gap. We make
nothing of this ordering beyond noting the direction: on pay and hire margins
these configurations do not amplify the classic human penalty; they
redistribute it into comparisons, rankings, and abstention.

### 4.8 Job-ad wording (E4)

**Greedy availability language amplifies the leave-gap penalty; diversity
language does nothing.** Varying only the JD's closing paragraph (résumé-FE
DiD, 32 résumé clusters): *greedy* wording — "This is a fast-paced role.
Candidates must be available after hours and on weekends as needed, and travel
up to 40% of the time." — adds a significant extra interview penalty to
leave-gap mothers for DeepSeek (−2.7pp, t = −2.3) and, combined with
family-friendly language, for DeepSeek both genders (−5.2/−6.0pp) and Haiku
mothers (−8.0pp, t = −2.8). Family-friendly sentences alone never
significantly help; EEO boilerplate has no effect in any model.

### 4.9 Occupational moderation (exploratory)

With 28 occupations and female share separable from task composites (24
uncorrected tests across 4 models × 6 regressors), female share carries a
positive sign in all four models but is nominally significant only for
DeepSeek (+.057, p = .025); nothing else approaches correction. Hypothesis-
generating only.

### 4.10 Robustness

**Drift** (pre-specified flag |Δ| > .03 on E2 choice): the phase-3 anchor
(parent cue, L0, O20 minus the re-run lawyer occupation) moves +.008 to +.024
across models and genders — within flag. E1 interview anchors move +1.1 to
+3.5pp. **Validity**: final main-run 99.91/98.99/98.95/99.83%; phase 3
100/100/100/99.98% after logged repairs; strict-validity re-estimates do not
move conclusions. **Materials**: replacing unqualified attorney résumés
converted near-arbitrary lawyer-pair choices into measurable penalties.
**Position bias** (main-run E2): Luna near-neutral (P(A) = .53), Qwen .58,
DeepSeek .68 first-slot preference; Haiku prefers the second slot (.39); all
positions counterbalanced. **Names**: six per gender rotated within cells;
name-frequency sensitivity documented by Wilson & Caliskan (2024).
**Table sources**: §§4.2–4.4 and 4.6–4.9 main run (phase-1/2 prompts);
§§4.3 (decomposition, invariance) and 4.5 phase 3.

## 5. Discussion

### 5.1 A two-layer account

**Layer 1: a caregiving / ideal-worker penalty, common to all four vendors in
sign.** It is invariant to gender information (blind = names-only, everywhere);
it is carried by the employment interruption and by overt family signals
rather than the word "parental"; it is hidden in single scores and exposed in
comparisons; and it is amplified when the job ad makes the ideal-worker norm
salient (E4). This is Acker's (1990) ideal worker rendered as a selection
rule: gender-neutral in form, but gendered in effect, because caregiving gaps
and PTA-type signals are carried overwhelmingly by women in real applicant
pools — a textbook disparate-impact / indirect-discrimination structure. That
fathers who *signal* caregiving are also penalized matches the human
flexibility-stigma literature (Rudman & Mescher 2013; Williams et al. 2013);
what differs from the human benchmark is the absence of the plain-cue
fatherhood bonus. Within Layer 1, the interruption component behaves like
availability inference (Phelps 1972; Kroft et al. 2013; Weisshaar 2018), while
the bundle component — penalized on top of a labeled leave, resistant to
commitment evidence that only partly restores parity — behaves like the
normative discrimination Benard & Correll (2010) describe.

**Layer 2: a thin, vendor-specific gender layer.** It appears when gender is
made salient: Luna's pro-woman preference switching on with explicit fields;
Haiku's mother-specific penalty in same-gender comparisons, its refusal to
*state* gender while demonstrably using it, and its pregnancy abstention. The
pattern is consistent with alignment shaping overt gender behavior while
leaving Layer 1 intact — vendors differ in exactly the behaviors most trained
against. Because four vendors realize four different preference structures
over identical materials, vendor concentration in screening infrastructure
would convert vendor idiosyncrasy into market-wide correlation (Kleinberg &
Raghavan 2021).

### 5.2 Implications for auditing and regulation

**Audit comparatively**: single-résumé scoring detects only small effects
while the decision-relevant margins — pairwise choice and shortlisting — carry
the penalties. **Treat abstention as an outcome**: the largest pregnancy
effect is a refusal to price that carries a real interview denial; deletion
miscounts it as fairness. **Measure gender knowledge implicitly**: direct
questions measure willingness to state; pronoun use shows names are read.
And because Layer 1 is formally gender-neutral, audits keyed to gender
categories alone (including four-fifths comparisons on sex) can miss it;
audits must also compare caregiving-signal holders.

For deployment: EEO boilerplate does nothing; greedy availability language
amplifies the penalty; explicit gender fields change two of four vendors in
opposite directions; vendor choice moves the penalty by a factor of two to
eight.

### 5.3 Limitations

The label contrast uses "extended travel" as its unrecognized-gap reference —
a recognized but leisure-coded reason; a "company closure" or "certification
program" label could be more neutral, and the parental-label estimates should
be read as *relative to travel* (a neutral-label arm is designed but not
fielded). Cues are deliberately strong and explicit; real-world signals
(gaps, volunteer lines, references) are weaker, and the leave gap is the most
ecologically valid. Materials are US-market, English, text-only, race held
constant — nothing identified about intersections. "Pregnancy" has no male
analogue. Salary and interview are recommendations, not negotiated outcomes
or callbacks. Four low-cost tiers without system prompts; fairness-instruction
system prompts and larger models untested. Occupational moderation is
exploratory. Pools and pairs are synthetic — the design identifies marginal
cue effects, not population hiring rates. Effective sample sizes are bounded
by design clustering (40/16 pairs per E2 cell).

## 6. Conclusion

Asked whether LLM screeners penalize mothers, the answer is: they penalize
*caregivers* — employment interruptions and overt family signals — regardless
of the candidate's gender, and only when candidates are compared. On that
layer all four vendors agree. What differs by vendor is a thin gender layer
that surfaces when gender is explicit, plus one vendor's pregnancy abstention.
An audit regime that scores single résumés, ignores abstention, or assumes
name-based gender manipulations will certify as fair systems that are not —
and because the caregiver layer is gender-neutral in form, it will evade
category-keyed fairness checks even when it reproduces the motherhood penalty
in effect.

## References

*(Titles verified against docs/proposal.md; entries marked ◆ to re-verify
against the source document before journal submission.)*

- Acker, J. (1990). Hierarchies, jobs, bodies: A theory of gendered
  organizations. *Gender & Society*, 4(2), 139–158.
- An, J., Huang, D., Lin, C., & Tai, M. (2025). Measuring gender and racial
  biases in large language models: Intersectional evidence from automated
  resume evaluation. *PNAS Nexus*, 4(3), pgaf089.
- Armstrong, L., Liu, A., MacNeil, S., & Metaxa, D. (2024). The Silicon
  Ceiling: Auditing GPT's race and gender biases in hiring. arXiv:2405.04412.
- Benard, S., & Correll, S. J. (2010). Normative discrimination and the
  motherhood penalty. *Gender & Society*, 24(5), 616–646.
- Bertrand, M., & Mullainathan, S. (2004). Are Emily and Greg more employable
  than Lakisha and Jamal? *American Economic Review*, 94(4), 991–1013.
- Correll, S. J., Benard, S., & Paik, I. (2007). Getting a job: Is there a
  motherhood penalty? *American Journal of Sociology*, 112(5), 1297–1338.
- EEOC (1978). Uniform Guidelines on Employee Selection Procedures, 43 FR 38290.
- European Union (2024). Regulation (EU) 2024/1689 (AI Act).
- Frermann, L., Njoto, S., Cheong, M., & Ruppanner, L. (2023). Gender bias and
  parental-leave gaps in ChatGPT résumé ranking. University of Melbourne. ◆
- Gaddis, S. M. (2017). How black are Lakisha and Jamal? Racial perceptions
  from names used in correspondence audit studies. *Sociological Science*, 4,
  469–489.
- Kleinberg, J., & Raghavan, M. (2021). Algorithmic monoculture and social
  welfare. *PNAS*, 118(22), e2018340118.
- Kroft, K., Lange, F., & Notowidigdo, M. J. (2013). Duration dependence and
  labor market conditions: Evidence from a field experiment. *Quarterly
  Journal of Economics*, 128(3), 1123–1167. ◆
- Phelps, E. (1972). The statistical theory of racism and sexism. *American
  Economic Review*, 62(4), 659–661. ◆
- Rozado, D. (2025). Gender and positional biases in LLM-based hiring
  decisions. arXiv:2505.17049.
- Rudman, L. A., & Mescher, K. (2013). Penalizing men who request a family
  leave: Is flexibility stigma a femininity norm? *Journal of Social Issues*,
  69(2), 322–340. ◆
- Veldanda, A. K., et al. (2023). Investigating algorithmic hiring bias in
  the era of ChatGPT. arXiv:2310.05135. ◆
- Weisshaar, K. (2018). From opt out to blocked out: The consequences of
  employment interruptions for mothers' career advancement. *American
  Sociological Review*, 83(6), 1054–1093. ◆
- Williams, J. C. (2000). *Unbending Gender: Why Family and Work Conflict and
  What to Do About It*. Oxford University Press.
- Williams, J. C., Blair-Loy, M., & Berdahl, J. L. (2013). Cultural schemas,
  social class, and the flexible workplace. *Social Problems*, 60(3). ◆
- Wilson, K., & Caliskan, A. (2024). Gender, race, and intersectional bias in
  resume screening via language model retrieval. AIES.
- Yin, L., Alba, D., & Nicoletti, L. (2024). OpenAI's GPT is a recruiter's
  dream tool. Tests show there's racial bias. *Bloomberg*.

## Appendices

- **A. Occupation design (O8)**: `docs/report/occupation_design.md`.
- **B. Perception checks**: `docs/phase3/manipulation_check.md` (direct);
  pronoun congruence in `round3_stats.json` (implicit; summarized §4.1).
- **C. Decomposition robustness**: six matched sets × four models with t and
  Holm — `round3_stats.json`; primary estimand with CIs — `round5_stats.json`.
- **D. Main-run tables**: `docs/report/tables.md` (programmatic).
- **E. Reproducibility**: pinned slugs/configs, frozen materials,
  deterministic plans, append-only logs and ledger ($160.48); regenerate with
  `uv run audit stats`, `uv run python -m
  audit.analysis.{cross_model,phase3_key_stats,round3,round5}`, `uv run audit
  figures`. Decisions and deviations: QUESTIONS.md.
- **F. Figures**: `docs/report/figures/fig1–fig8` (main run); fig9–fig13
  (phase 3): task dependence, decomposition waterfall, cue-level invariance,
  direct-gender divergence, abstention.
