# From Motherhood Penalty to Caregiver Penalty: How LLM Résumé Screeners Treat Family Signals

*Draft 6 (phases 1–4 complete), 2026-10-31. Yuxin Hou. Every statistic is generated
from run logs by `uv run audit reproduce` — main run → `stats.json`, `tables.md`;
phase 3 → `phase3_key_stats.json`, `CROSS_MODEL.md`, `round3/5/6_stats.json`;
phase 4 → `phase4_stats.json`, `docs/final/{coding_stats,disparate_impact_stats,
study_totals}.json`. Numbers quoted in the abstract, summary, and §§4.6–4.7 are
registered in `claims.yaml` and checked by `tests/test_claims.py`.*

## Abstract (short)

Deployed LLM résumé screeners were audited across decision tasks, family-cue
components, and gender-information regimes (4 pinned models; 28 occupations;
616,419 logged calls). Family cues barely move isolated scores but cost
parents 11–39pp in pairwise choice and up to 77% of shortlist probability:
choices amplify the cues 3.5–38× beyond their score effects, with one model
scoring parents *higher* yet choosing them 23% of the time. The penalty is a
caregiver penalty, not a gender penalty: it is statistically unchanged when
all gender information is removed (TOST ±5pp), and decomposes into a generic
interruption penalty (10.5–26.0pp) plus a family-signal penalty (10.6–17.4pp);
the "parental" label itself never adds a penalty. No fatherhood bonus exists.
Vendor-specific gendered behaviors layer on top — pro-woman preference
activating under explicit gender in one model, an anti-mother shift and
pregnancy salary-withholding (19.8%, denying interviews) in another, near
parity in a third. Because caregiving gaps are carried mostly by women, a
gender-neutral-in-form rule is not gender-neutral in effect. Comparative-task
testing, abstention as an outcome, and implicit gender-knowledge checks are
required to see any of this; single-résumé audits would not.

## Extended summary

Language models increasingly assist résumé screening, but audits typically vary
one design dimension at a time. We cross three — **decision task** (scoring,
pairwise choice, pool ranking), **family cue** (disclosure, employment
interruption, caregiving label, family bundle), and **gender-information regime**
(gendered names, explicit gender field, initials, fully blind) — on identical
validated materials (28 occupations, 154 résumés, six rotating names per gender;
616,419 logged calls; DeepSeek V4.1 Flash, Claude Haiku 5.5, GPT-6 Luna, Qwen
3.8 Flash at pinned versions). **Finding 1 — the penalty appears only in
comparison, amplified far beyond its footprint in scores.** In isolated
scoring, family cues move fit ratings by at most 0.35 points (10-point scale)
and interview recommendations by at most 1.5pp. In pairwise choice the same
cues cost parents 11–39pp of choice probability: a parent with a parental-leave
gap wins a head-to-head final against a comparably qualified childless
candidate (résumé roles counterbalanced) only 11–31% of the time, where 50%
means no penalty; the same résumé is shortlisted at 23–81% of its childless
rate. Choices track ordinary quality differences at 13–18pp per fit point, but
the family cues act, in choice terms, like quality losses of 0.9–2.0 fit points
— 3.5× to 38× their actual score effects in the three models where those effects
are negative (the ratio is largest where score effects are near zero) — and in one model the sign reverses:
Claude Haiku 5.5 *scores* parents higher (+0.34) yet chooses them 23% of the
time. **Finding 2 — the penalty is a caregiver penalty, not a gender penalty.**
Removing all gender information (blind rendering) leaves the parent-choice
penalty statistically unchanged in every model (equivalence at ±5pp, TOST, 7 of
8 model×cue cells). A matched-occupation placebo decomposition (primary
estimand: 40 pairs, 95% CIs) shows two components: a **generic interruption
penalty** (an 8-month gap labeled *travel* costs 10.5–26.0pp) and a
**caregiver-specific family-signal penalty** (the family bundle adds 10.6–17.4pp
on top of a labeled parental leave; parenthood net of a disclosure placebo
7.3–19.2pp). The *label* of the interruption never adds a penalty — for three
models "Parental leave" is modestly *less* costly than the identical dates
labeled "Career break — extended travel" — and disclosure alone (a
length-matched hobby/volunteer line) costs a small 3pp in three models, while
Haiku slightly favors it (+3.7pp). There is no fatherhood bonus anywhere. Because
caregiving gaps and family signals are carried disproportionately by women in
real applicant pools, a gender-neutral-in-form rule is not gender-neutral in
effect. **Finding 3 — thin, vendor-specific gendered behaviors layer on top.**
In direct woman-vs-man choices, Qwen is within ±5pp of parity at every level
(equivalence confirmed; one cell shows a 1.8pp tilt to women); DeepSeek shows a small robust pro-woman preference (+3.5
to +4.8pp, Holm-corrected); Luna's pro-woman preference activates only when
gender is explicit (.58 → .65 for mother-vs-father; its field response exceeds
Qwen's and DeepSeek's by 5.8–7.0pp, pair-matched); Haiku moves the opposite way
(−4.5pp, p = .003) and is the only model whose mother-father choice gap differs
from the others (tested directly) — concentrated in perceived commitment.
**Finding 4 — standard mitigation does not remove it.** A
deployed-style EEO system prompt leaves the caregiver penalty in place for
two models, reduces it for one, and *deepens* it for one; a targeted
"do not penalize caregiving gaps" instruction cuts the interruption penalty
(4–14pp) but leaves the family-signal penalty untouched; nothing reaches
parity. **Finding 5 — abstention is a discrimination margin.** Haiku withholds salary
offers entirely for 19.8% of pregnant applicants (27.5% under an explicit
gender field), and withheld applicants are interviewed only 30% of the time —
a −9.4pp interview penalty (t = −4.8) that listwise deletion would misread as
fairness. Haiku's abstention and its interview consequence are shown in
Figure 13. Single-résumé audits would detect only the small scoring effects;
the decision-relevant penalties are comparative. Effective sample sizes reflect
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
caregiving/ideal-worker penalty shared by all four vendors in sign, with two
distinguishable parts: a *generic interruption penalty* — anyone returning from
an 8-month employment gap is penalized, and caregivers carry most gaps — and a
*caregiver-specific family-signal penalty* attached to overt parenting signals.
It is gender-blind, hidden in single scores, exposed in comparisons, and
amplified when a job ad makes the ideal-worker norm salient. **Layer 2** is a
thin, vendor-specific gender layer that surfaces mainly when gender is made
explicit — one model's pro-woman preference, another's mother-specific penalty
and pregnancy abstention.

## 2. Design

### 2.1 Models and governance

Four deployed consumer models via OpenRouter, pinned to dated slugs and single
endpoints (never `*-latest`; first-party endpoints except DeepSeek, pinned to
DeepInfra fp8 after first-party routing was blocked by account guardrails —
QUESTIONS.md §2b). Configuration: reasoning disabled, JSON mode, no system
prompt (consumer default), temperature default. **Population of inference**:
high-volume, low-cost screening configurations; real HR tools typically add
system prompts (often with fairness instructions) and may use larger models —
phase 4 tests two fairness system prompts (§4.6); larger models are untested. Every call is logged with provider attribution; plans
are deterministic and resumable; the ledger is append-only under a hard $200
budget (reserve $20). Total across all phases: 616,419 logged calls, $188.52,
plus $0.66 for rationale coding (§4.2).

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
| `parent_gap` | " + cover note of `parent` | 8-month *Parental leave* entry inserted; later dates shifted |
| `parent_committed` | " + cover note of `parent` | `parent` + objective commitment bullets |
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
and implicitly (pronoun congruence in rationales; below). Direct woman-vs-man
choice pairs (same family status both sides, roles and positions rotated)
measure gender preference at L0–L2.

**Perception check: asked vs. used.** Asked directly, models differ in willingness to state gender; using it implicitly, they all read names perfectly. The direct check ("most likely
gender of this applicant? female/male/unknown") shows explicit fields answered
perfectly (100% at L1/L2, n = 336 each) and names answered "unknown" often —
by Luna (34%) and Haiku (58%). But in free-text E1 rationales, whenever a
model uses a gendered pronoun at L0–L2 it matches the name/field **100%** of
the time (usage 5–26% at L0; 0.7–7.9% at L2); under blind rendering gendered
pronouns nearly vanish (≤ 0.6%). The direct question therefore measures
*willingness to state* gender — itself an alignment behavior — not legibility.
L1/L2 certify knowledge the models already have at L0; L3 genuinely removes it.

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

**Confirmatory tests** (specified in SPEC.md / SPEC_PHASE3.md before the runs):
parent-cue penalties in E1/E2/E3 per model and gender; mother-minus-father
differences; E3 impact ratios; E4 wording contrasts; phase-3 cue-level
penalties, placebo decomposition, direct gender contrasts, abstention rates,
drift anchors; phase-4 H-B1/H-B2/H-B3 system-prompt arms and H-C1 neutral
gap labels (pre-specified in SPEC_PHASE4.md §6 before the runs). **Equivalence**: "no difference" claims use TOST at a
pre-stated smallest effect of interest of ±5pp with 90% CIs. **Small-cluster
robustness**: O8 tests (16 pairs) and E4 (32 résumé clusters) are re-checked
with wild cluster bootstrap p-values. **Regression check**: cluster-mean
t-tests are re-estimated as LPMs with position, paraphrase, and name controls.
Everything else is exploratory and labeled. **Scope of inference**: these are
four pinned model versions in high-volume, low-cost screening configurations
(consumer default, no system prompt), tested on résumés like ours;
cross-model comparisons are descriptive (n = 4 models).

## 3. Preregistration status

Designs and analysis plans (SPEC.md, SPEC_PHASE3.md) were specified in advance
in the project proposal and committed before each paid run; two documented
deviations (DeepSeek endpoint substitution; replacement of clinical
psychologists — CPS female share suppressed — with health-services managers)
were researcher-approved before execution. Phase 4 (SPEC_PHASE4.md) specified
hypotheses H-B1–H-B3 and H-C1, their tests, and the ±5pp equivalence bound
before any phase-4 call. One analysis choice was not pre-specified: the ±5pp
smallest effect of interest for the phase-3 equivalence tests (§4.2, §4.4) was
chosen after phase-3 data collection, before those tests were run. This is a
prospective internal audit, not an OSF-registered report; exploratory analyses
are labeled.

## 4. Results

Sections 4.1–4.3 establish Layer 1: where the penalty appears (4.1), what it
is about (4.2), and that it does not depend on gender (4.3). Sections 4.4–4.5
document the thin, vendor-specific gender layer (explicit gender, abstention).
Section 4.6 tests whether fairness instructions remove either layer, and 4.7
translates the gender-blind penalty into a gender gap under realistic signal
prevalence. Sections 4.8–4.10 report secondary outcomes and moderators;
4.11 collects robustness checks.

### 4.1 The penalty appears only in comparison (Q1)

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

Three checks address the possibility that forced choice merely *amplifies*
small score differences (a tie-breaker) or that the integer scoring scale is
too coarse. **(a) Cue amplification vs. quality amplification.** E2 choices
track ordinary quality differences (the two résumés' E1 `none` fit gap, roles
counterbalanced) at 13–18pp of choice probability per fit point. The family
cues, in choice terms, act like quality losses of 0.9–2.0 fit points — 3.5× to
38× their actual score effects in DeepSeek, Luna, and Qwen (ratios are largest
where score effects are near zero, e.g. Qwen's −0.02 parent fit gap) — and for Haiku the sign reverses: it *scores*
parents higher (+0.34) yet chooses them 23% of the time. No amplification of
scores can produce a sign reversal (Figure 9). **(b) Noise model.** Converting
each model's E1 fit gap into a predicted choice share via a probit with the
within-résumé fit SD (σ × √2 for a difference of draws) and bootstrapping over
résumé pairs: choices are significantly *below* prediction in 7 of 8 model×cue
cells (observed − predicted −5 to −52pp, bootstrap 95% CIs excluding zero);
the one exception is DeepSeek's leave-gap cue, whose choice penalty is
consistent with score amplification (−0.2pp [−3.6, +3.1]). **(c) Tie-breaker
split.** The choice penalty is larger when the two résumés' pretest qualities
are near-ties (all eight model×cue cells, t = −0.9 to −4.0), consistent with
tie-breaking — but remains 9–32pp in clear-gap pairs. Scoring differences,
thresholded or amplified, do not explain the comparative penalties.

### 4.2 What the penalty is about (Q2): interruption + family bundle, not gender

**A matched-occupation placebo decomposition (primary estimand: O20, L1+L2
pooled, 40 pairs, mothers) with the six-set robustness in the appendix:**

| component (comparator) | DeepSeek | Haiku | Luna | Qwen |
| --- | --- | --- | --- | --- |
| interruption itself (P(`gap_travel`) vs .50) | −10.5pp (t −8.0) | −18.4pp (t −8.5) | **−26.0pp** (t −7.3) | −22.4pp (t −8.9) |
| parenthood net of disclosure (`parent` − `personal`) | −10.4pp [−12.8, −8.0] (t −8.5) | **−19.2pp** [−23.4, −15.0] (t −8.9) | −12.1pp [−16.3, −7.9] (t −5.6) | −7.3pp [−10.3, −4.3] (t −4.7) |
| caregiving label (`gap_parental_only` − `gap_travel`) | +1.7pp [+0.5, +2.9] (t 2.7) | −1.1pp [−3.2, +0.9] (t −1.1) | +6.5pp [+3.7, +9.2] (t 4.6) | +6.7pp [+4.9, +8.5] (t 7.3) |
| family bundle (`parent_gap` − `gap_parental_only`) | −10.6pp [−12.7, −8.6] (t −10.0) | **−17.4pp** [−20.2, −14.5] (t −11.8) | −11.5pp [−15.4, −7.5] (t −5.7) | −12.1pp [−14.7, −9.5] (t −9.2) |

(Every cell [95% CI] on the primary estimand; Haiku's interruption estimate was
misreported as −25.6pp in drafts ≤ 5.2.) Disclosure alone has a small effect of
either sign: `personal` costs 2.9–3.5pp in DeepSeek, Luna, and Qwen (t −4.2 to
−4.4) but *raises* Haiku's choice share by 3.7pp (t 3.9) — which is why the
parenthood row nets it out. The interruption itself — an 8-month break labeled
*travel* — costs 10.5–26.0pp. The *label*
never adds a penalty: Haiku's estimate is statistically equivalent to zero at
±5pp (TOST 90% CI [−2.9, +0.7]pp; the table shows the 95% CI); DeepSeek shows a tiny positive (+1.7pp); Luna and
Qwen treat *Parental leave* as 6–7pp *less* costly than the same dates labeled
travel. The family bundle adds a further 10.6–17.4pp *on top of* a labeled
parental leave. In the six-set robustness (O8 at L0–L3, O20 at L1/L2
separately), parenthood and bundle survive Holm in 23 of 24 tests each; the
label is null for Haiku and positive for Luna (5/6 sets) and Qwen (6/6)
(Figure 10).

**Removing gender information leaves the penalty unchanged.** Pair-matched tests on O8
(16 pairs): P(parent chosen), names (L0) minus blind (L3): DeepSeek +.006
(t 0.3), Haiku −.005 (t −0.3), Luna −.013 (t −1.2), Qwen +.003 (t 0.2); the
leave-gap cue likewise. Because non-rejection is not evidence of absence, we run
TOST at a ±5pp smallest effect of interest (chosen after data collection but
before running the equivalence tests; phase-4 hypotheses pre-specify it
prospectively): the blind-names
difference is statistically equivalent to zero at ±5pp in **7 of 8 model×cue
cells** (90% CIs all within ±5pp; the eighth, DeepSeek's leave-gap, grazes it
at [0.0, +5.6]); minimum detectable effects are 3.0–5.4pp (Figure 11).
Wild-cluster bootstrap (Rademacher, by occupation) does not change any
conclusion. Explicit gender *fields* partially offset the plain-parent penalty
for Haiku (+7.4pp, t 7.7; wild p = .006) and Luna (+3.4pp, t 3.0; wild
p = .015), with no effect on DeepSeek or Qwen. E3 ranking replicates the
invariance (top-3 ratios across L0–L3: .64/.66/.66/.65 DeepSeek;
.15/.19/.17/.16 Haiku; .70/.72/.70/.71 Luna; .68/.71/.74/.71 Qwen).

**What the models say (exploratory).** To see whether the reasons models
give track this decomposition, an LLM coder (DeepSeek V4.1 Flash, temperature
0) coded E2 rationales for eight reason codes; a second coder (Qwen 3.8 Flash)
re-coded 638 rationales not written by Qwen. All rationales come from the
primary-estimand condition (O20, explicit gender field, no system prompt).
Six codes reach κ ≥ .70 overall (.71–.93) and are used; two (qualifications,
κ .02; gender, κ .31) are not. Agreement is lower on rationales written by
models other than DeepSeek for availability (κ .68) and family (κ .63), so
those two codes are noisier for Haiku, Luna, and Qwen. Among rationales in
which the cued candidate lost, the employment gap is cited in 24–91% of losses
for the three interruption cues and in at most 4% for parent cues without a
gap; family is cited in 12–64% of losses for parent cues and never for the
travel gap or the disclosure placebo; availability concerns are common for
DeepSeek and Qwen (39–52% of interruption losses) but rare for Haiku and Luna
(≤ 15%). All twelve pre-stated alignment contrasts (gap and availability:
interruption vs parent cues; family: family vs non-family cues) go in the
predicted direction and survive Holm (Figure 15). Rationales for losing
parents often call family information irrelevant to the decision (parent and
committed cues: Qwen 90%, Haiku 69%, Luna 56%, DeepSeek 53%). For Haiku and
Luna such statements are about as common when the parent wins (64%, 50%); for
DeepSeek and Qwen they are concentrated in losses (19% and 42% when the parent
wins). Code shares do not differ by candidate gender, with one exception
(Haiku mentions protected characteristics 12pp more often for mothers, Holm
p = .02). These are stated reasons, conditional on the outcome and coded by an
LLM without human validation; they describe how the models justify choices,
not why they make them (Appendix E′).

### 4.3 No fatherhood bonus; where a mother-specific penalty exists

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
Tested directly across the same pairs, Haiku's mother-father choice gap
differs from all three other models (−2.6 to −4.4pp, t −2.1 to −2.9,
p < .05) — "only Haiku" is a tested difference, not an asymmetry of
significance.

### 4.4 Explicit gender: vendor-specific preferences

**Qwen is within ±5pp of parity everywhere; DeepSeek has a small robust pro-woman tilt;
Luna's pro-woman preference appears only when gender is explicit; Haiku's
disappears.** Direct woman-vs-man choices (same family status both sides;
parity .50; 56 unordered pairs; Holm over six cells per model; phase 3):

| model | cell | names (L0) | field (L1) | initials+field (L2) |
| --- | --- | --- | --- | --- |
| Qwen | childless / parent | .505 / .503 | .493 / .513 | **.518** / .491 |
| DeepSeek | childless / parent | .514 / **.535** | **.540 / .540** | **.538 / .548** |
| Luna | childless / parent | **.522 / .577** | **.587 / .647** | **.575 / .634** |
| Haiku | childless / parent | **.528 / .544** | .526 / .498 | .513 / .471 |

(bold = Holm-corrected difference from parity; Figure 12.) Qwen's near-parity is
not merely non-rejection: TOST confirms equivalence at ±5pp in every cell
(largest 90% CI [+0.8, +2.9]pp, childless at L2, the one Holm-significant cell). The vendor differences are tested directly,
pair-matched across the same 56 résumé pairs: Luna's field response exceeds
Qwen's by +7.0pp (childless) and +5.8pp (parent-vs-father) and DeepSeek's by
+3.9 to +6.4pp (t 2.5–4.5); Haiku's field response on the parent contrast is
−5.0 to −5.6pp *below* both (t −3.0 to −3.7) — the two vendors move in
opposite directions. Haiku's L0 tilt (.544 pro-mother) falls to .498 and .471
with explicit gender. Explicit gender fields — standard in many markets — are
not neutral: they activate vendor-specific preferences that name-only
screening conceals.

### 4.5 Abstention: withholding offers as a discrimination margin

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

### 4.6 Does a fairness instruction remove it? (phase 4, confirmatory)

**No — a generic EEO system prompt leaves the caregiver penalty in place,
with vendor-signed effects: one vendor improves, one backfires; a targeted
no-gap-penalty instruction reduces the interruption penalty but not the
family-signal penalty.** Three system-prompt arms (none / generic EEO /
EEO + "do not penalize caregiving gaps"; user prompts identical; pre-specified
H-B1–H-B3), 48,000 calls. P(cued chosen), women (none → fair → gap):

| model | parent | parent + leave gap |
| --- | --- | --- |
| DeepSeek | .361 → .325 → .369 | .317 → .301 → **.386** |
| Haiku | .266 → .332 → .342 | **.074 → .195 → .217** |
| Luna | .307 → .357 → .376 | .195 → .188 → **.286** |
| Qwen | .381 → **.333 → .351** | .234 → **.181 → .279** |

**(H-B1) Generic fairness prompt.** Effects on the penalty: DeepSeek ≈ 0;
Luna +5.0pp (parent) / −0.7pp (gap); **Haiku +6.6/+12.2pp** (reduced, t = 2.9/
5.6); **Qwen −4.7/−5.3pp** (deepened, t = −2.3/−3.4). Layer 1 survives the
standard mitigation everywhere — and the direction is vendor-specific,
including a fairness *backfire*. **(H-B2) Layer 2 responds.** Luna's
mother-vs-father preference replicates (.640 vs phase-3's .647) and falls to
.557 under the fairness prompt; Haiku's moves from .498 to .457. **(H-B3)
Targeted instruction.** Adding "do not penalize employment gaps taken for
caregiving" cuts the interruption penalty by 4–14pp in all four models —
while the family-*signal* penalty is essentially untouched (DeepSeek +0.8pp
n.s., Qwen −3.0pp n.s.), and no arm approaches parity. Instructions can
reach the availability-inference component; the normative bundle resists.

**Neutral gap labels (H-C1).** "Job search after company closure" and
"Full-time certification program" (same dates) were not more costly
than "Career break — extended travel": no neutral label is significantly
more costly than travel after Holm; Qwen penalizes travel 4.3–5.4pp *more*
than both neutral labels (Holm p < .01); 7 of the other 12 label × gender
contrasts are equivalent at ±5pp; the largest opposite-direction estimate is
DeepSeek's certification label for women (−4.0pp, Holm p = .14). Travel was not a stigmatized reference; the
label conclusion of §4.2 stands and strengthens.

### 4.7 From caregiver penalty back to a gender gap (scenario)

Layer 1 is gender-blind, but caregiving gaps and family signals are not
gender-neutrally distributed among real applicants. Applying each model's
measured penalties (E3 résumé-FE ratios) to simulated pools with
gender-specific signal prevalence: at the 20%-women / 5%-men scenario no
model crosses the four-fifths line (implied women/men selection ratios
.88–.96), but the **crossing thresholds** are the result: Haiku's gender-
blind penalty produces a four-fifths violation once women's signal
prevalence exceeds **31%** (men at 5%); DeepSeek 73%, Qwen 84%, Luna 93%
(Figure 14). Prevalence inputs are scenario parameters (public
gender-specific gap-prevalence estimates were not sourceable within the
study); the thresholds are prevalence-free. A formally gender-neutral rule
reproduces a gendered outcome at plausible prevalence asymmetries — exactly
the disparate-impact structure §5.1 describes.

### 4.8 Salary and the human benchmark

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

### 4.9 Job-ad wording (E4)

**Greedy availability language amplifies the leave-gap penalty; diversity
language does nothing.** Varying only the JD's closing paragraph (résumé-FE
DiD, 32 résumé clusters): *greedy* wording — "This is a fast-paced role.
Candidates must be available after hours and on weekends as needed, and travel
up to 40% of the time." — adds a significant extra interview penalty to
leave-gap mothers for DeepSeek (−2.7pp, t = −2.3) and, combined with
family-friendly language, for DeepSeek both genders (−5.2/−6.0pp) and Haiku
mothers (−8.0pp, t = −2.8). Family-friendly sentences alone never
significantly help; EEO boilerplate has no effect in any model.

### 4.10 Occupational moderation (exploratory)

With 28 occupations and female share separable from task composites (24
uncorrected tests across 4 models × 6 regressors), female share carries a
positive sign in all four models but is nominally significant only for
DeepSeek (+.057, p = .025); nothing else approaches correction. Hypothesis-
generating only.

### 4.11 Robustness

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
**Regression check**: LPMs with pair-clustered SEs and position, paraphrase,
and name controls reproduce the cluster-mean tests (e.g., leave-gap
coefficient −.047/−.125/−.106/−.161, t −3.7 to −9.4; gender interactions ≈ 0).
**Table sources**: §§4.1, 4.3, 4.5, 4.8–4.10 use the main run (phase-1/2
prompts); the decomposition, invariance, and direct-gender analyses (§§4.2,
4.4) use phase 3; §§4.6–4.7 use phase 4. **Repair-saved
responses** are excluded from all choice-based analyses: the repair template
carries the prior response, not the original candidates, so repaired `chosen`
fields are not experimental responses (impact quantified: historical Qwen E2
cells shift ≤ 0.8pp, within the previously reported strict-validity bounds;
phase-4 exclusion ≈ 1% of rows).

## 5. Discussion

### 5.1 A two-layer account

**Layer 1: a caregiving/ideal-worker penalty, common to all four vendors in
sign, with two parts.** The *generic interruption penalty* (10.5–26.0pp for an
8-month gap regardless of label or gender) behaves like availability inference
(Phelps 1972; Kroft et al. 2013; Weisshaar 2018) — anyone with a gap is
treated as an availability risk, and caregivers carry most gaps. The
*caregiver-specific family-signal penalty* (7.3–19.2pp net of disclosure, plus
10.6–17.4pp for the bundle on top of a labeled leave) attaches to overt
parenting signals as such, is resistant to commitment evidence that only
partly restores parity, and behaves like the normative discrimination Benard &
Correll (2010) describe. Both parts are invariant to gender information,
hidden in single scores, exposed in comparisons, and amplified when the job ad
makes the ideal-worker norm salient (E4). Together they are Acker's (1990)
ideal worker rendered as a selection rule: gender-neutral in form, but
gendered in effect, because caregiving gaps and PTA-type signals are carried
overwhelmingly by women in real applicant pools — a textbook disparate-impact
/ indirect-discrimination structure. That fathers who *signal* caregiving are
also penalized matches the human flexibility-stigma literature (Rudman &
Mescher 2013; Williams et al. 2013); what differs from the human benchmark is
the absence of the plain-cue fatherhood bonus.

**Layer 2: a thin, vendor-specific gender layer** (Figures 12–13). It appears when gender is
made salient: Luna's pro-woman preference switching on with explicit fields;
Haiku's mother-specific penalty in same-gender comparisons, its refusal to
*state* gender while demonstrably using it, and its pregnancy abstention. We
conjecture — this study has no unaligned models to compare against — that
alignment training shapes overt gender behavior while leaving Layer 1 intact:
vendors differ precisely in the behaviors most directly trained against. Because four vendors realize four different preference structures
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
opposite directions; and vendor choice matters — the same leave-gap cue costs
19.0pp (DeepSeek) to 39.0pp (Haiku) of choice probability (≈2×), and the
shortlist shortfall ranges from .22 (Luna) to .75 (Haiku) (≈3.4×).

### 5.3 Limitations

The label contrast uses "extended travel" as its unrecognized-gap reference —
a recognized but leisure-coded reason. Phase 4 fielded "job search after company
closure" and "full-time certification program" with the same dates; neither
was significantly more costly than travel (§4.6), so travel is not a stigmatized
reference, but other gap reasons remain untested. Cues are deliberately strong and explicit; real-world signals
(gaps, volunteer lines, references) are weaker, and the leave gap is the most
ecologically valid. Materials are US-market, English, text-only, race held
constant — nothing identified about intersections. "Pregnancy" has no male
analogue. Salary and interview are recommendations, not negotiated outcomes
or callbacks. Four low-cost tiers; main analyses use no system prompt (phase 4 tests two
fairness prompts, §4.6); larger models untested. Occupational moderation is
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
  Journal of Economics*, 128(3), 1123–1167.
- Phelps, E. (1972). The statistical theory of racism and sexism. *American
  Economic Review*, 62(4), 659–661. ◆
- Rozado, D. (2025). Gender and positional biases in LLM-based hiring
  decisions. arXiv:2505.17049.
- Rudman, L. A., & Mescher, K. (2013). Penalizing men who request a family
  leave: Is flexibility stigma a femininity stigma? *Journal of Social
  Issues*, 69(2), 322–340.
- Veldanda, A. K., et al. (2023). Investigating algorithmic hiring bias in
  the era of ChatGPT. arXiv:2310.05135. ◆
- Weisshaar, K. (2018). From opt out to blocked out: The challenges for
  labor market re-entry after family-related employment lapses. *American
  Sociological Review*, 83(1), 34–60.
- Williams, J. C. (2000). *Unbending Gender: Why Family and Work Conflict and
  What to Do About It*. Oxford University Press.
- Williams, J. C., Blair-Loy, M., & Berdahl, J. L. (2013). Cultural schemas,
  social class, and the flexibility stigma. *Journal of Social Issues*,
  69(2), 209–234.
- Wilson, K., & Caliskan, A. (2024). Gender, race, and intersectional bias in
  resume screening via language model retrieval. AIES.
- Yin, L., Alba, D., & Nicoletti, L. (2024). OpenAI's GPT is a recruiter's
  dream tool. Tests show there's racial bias. *Bloomberg*.

## Appendices

- **A. Occupation design (O8)**: `docs/report/occupation_design.md`.
- **B. Perception checks**: `docs/phase3/manipulation_check.md` (direct);
  pronoun congruence in `round3_stats.json` (implicit; summarized §2.4).
- **C. Decomposition robustness**: six matched sets × four models with t and
  Holm — `round3_stats.json`; primary estimand with CIs — `round5_stats.json`.
- **D. Main-run tables**: `docs/report/tables.md` (programmatic).
- **E. Reproducibility**: pinned slugs/configs, frozen materials,
  deterministic plans, append-only logs and ledger ($189.18 incl. coding; per-phase totals in `docs/final/study_totals.md`); regenerate with
  `uv run audit reproduce` (all statistics, tables, figures, claims check).
  Decisions and deviations: QUESTIONS.md.
- **E′. Rationale coding**: per-cell shares with pair-clustered CIs,
  losing-vs-won and gender contrasts, coder agreement (overall and by
  rationale author), and the original (unharmonized) sample for comparison —
  `docs/final/coding_tables.md`, `coding_stats.json`.
- **F. Figures** (`docs/report/figures/`). Main text: fig9 task dependence
  (§4.1), fig10 decomposition (§4.2), fig11 cue-level invariance (§4.2), fig12
  direct-gender divergence (§4.4), fig13 abstention (§4.5), fig14
  disparate-impact thresholds (§4.7); fig15 rationale-code shares (§4.2). Appendix figures (main run, supporting §§4.1, 4.3, 4.8–4.10): fig1
  design, fig2 E2 forest plot, fig3 E1 cells, fig4 E3 impact ratios, fig5 E4
  job-ad contexts, fig6 quality slopes, fig7 human benchmark, fig8 moderators.
  Figures are renumbered in order of appearance for the typeset version.
  Phase-4 results: `docs/phase4/PHASE4_RESULTS.md`; study totals:
  `docs/final/study_totals.md`; claims registry: `docs/report/CLAIMS.md`.
