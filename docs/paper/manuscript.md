# Protection Follows the Label: How Large Language Model Résumé Screeners Turn the Motherhood Penalty into a Caregiver Penalty

Yuxin Hou, Princeton University

*Working paper, draft 3 (2026-11-01). Study 1 is complete; Study 2 is planned. Numbers
come from the claim-checked report. Values in Section 4.1 from the amplification and
noise-model analyses and the refusal rates in Section 4.2 are pending code fixes
(SPEC_FINALIZE Rounds 14–15).*

---

## Abstract

Large language models (LLMs) now screen job applicants, and their developers train
them not to treat people differently by gender. We ask what such systems do with the
signals that make up the motherhood penalty. On a résumé, motherhood bundles a
protected category (being a woman) with signals that are correlated with gender but
not protected as such: an interruption in employment and visible family
responsibilities. We propose that in aligned models, *protection follows the label*:
the more directly a signal names a protected category, the more carefully models
handle it, while correlated signals are penalized freely. Study 1, an audit of four
widely used models (616,419 decisions, 28 occupations), unbundles the signal on
otherwise identical résumés and places each component along this gradient. Signals
of caregiving carry a large penalty, for mothers and fathers alike, visible only when
applicants are compared: a parent returning from leave wins a head-to-head choice
against an equally qualified childless applicant 11 to 31 percent of the time. The
penalty is unchanged when all gender information is removed. Explicitly named gender
elicits small, vendor-specific behavior—correction toward women, parity, or
refusal—rather than a penalty. An instruction that names caregiving gaps reduces the
gap penalty but not the penalty on family signals it leaves unnamed. Study 2, planned,
tests whether the gradient emerges with alignment by comparing the same open-weight
model before and after post-training. Because women carry caregiving signals more
often than men, a screener that protects the label can reproduce the motherhood
penalty in effect.

---

## 1. Introduction

Mothers pay a price in the labor market that fathers do not. They earn less than
comparable childless women (Budig and England 2001), and in audit and laboratory
studies employers rate them as less competent and committed, recommend them for hire
less often, and offer them lower salaries, while fathers are not penalized (Correll,
Benard, and Paik 2007). The penalty persists when mothers present direct evidence of
commitment, which suggests that it rests on norms about what mothers should do as
well as on inferences about what they can do (Benard and Correll 2010).

Hiring is now partly delegated to large language models, and these are not neutral
copies of the texts they learned from. Developers train them, through instruction
tuning and preference optimization, to avoid treating people differently by protected
characteristics such as gender, and evaluate them on whether outputs change when a
protected attribute changes. This raises a question that audits of human employers
could not pose: what happens to a form of discrimination when the decision-maker has
been trained against its category but not against its correlates?

The motherhood penalty is a natural case, because on a résumé motherhood is a bundle.
It combines a protected category—the applicant is a woman—with signals that are
correlated with gender but not protected as such: time out of work, and visible family
responsibilities such as children, parenting activities, or a caregiving leave. In
human hiring these components travel together, and audits cannot remove gender while
keeping the family situation visible. An LLM screener can be shown the same résumé
thousands of times with one component added or removed, including with every trace of
gender removed, so the bundle can be taken apart.

We propose that in aligned models *protection follows the label*. Signals differ in
how directly they refer to a protected category (Figure 1): an explicit statement of
gender names it; a gendered first name implies it; a caregiving gap or a line about
children is merely correlated with it. If alignment teaches models to handle named
categories carefully, behavior should differ along this gradient: careful,
developer-specific treatment where gender is named, weaker effects where it is only
implied, and unchecked penalties where the signal is a correlate that no one has
trained against. The same logic predicts how remedies work: an instruction should
protect what it names and leave untouched what it does not.

Study 1 tests these expectations in an audit of four widely used models. It unbundles
the motherhood signal on identical résumés, varies how directly gender is conveyed,
observes the result at the decision margins where selection happens, and tests the
fairness instructions that deployers commonly add. The findings line up with the
gradient. Caregiving signals carry a large penalty that falls on fathers as much as on
mothers, is unchanged when gender information is removed, and appears only when
applicants are compared. Explicitly named gender elicits small and vendor-specific
behavior—correction toward women in one model, parity in another, refusal in a
third—rather than a penalty. An instruction that names caregiving gaps reduces the
gap penalty but not the penalty on family signals. Study 2, which we describe as a
planned design, asks where the gradient comes from by comparing the same open-weight
model before and after post-training.

The argument contributes to three conversations. For the sociology of gender and work,
it separates components of the motherhood penalty that human hiring confounds and shows
that, in these systems, the ideal-worker components survive while the gendered one does
not (Acker 1990; Williams 2000). For research on discrimination and its regulation, it
identifies a mechanism—protection that attaches to labels rather than consequences—by
which discrimination can persist through correlated signals once a category is
policed, a pattern with parallels in studies of employers who lose access to a signal
(Agan and Starr 2018). For algorithmic auditing, it shows that audits organized
around protected categories, single-applicant scores, or answered questions only would
certify these systems as fair.

## 2. Background

### 2.1 The motherhood bundle

Explanations of the motherhood penalty can be read as claims about which part of the
bundle does the work. *Gender-statistical accounts* hold that employers treat
motherhood as a proxy for lower availability and that the inference is gendered:
mothers, not fathers, are expected to reduce their commitment (Phelps 1972; Correll,
Benard, and Paik 2007), and a normative variant holds that mothers violate expectations
of devotion to family (Benard and Correll 2010). Both predict a penalty specific to
mothers, which requires the evaluator to know the applicant's gender. *Ideal-worker
accounts* locate the penalty in the organization of work around an abstract worker
who is fully available and free of outside obligations (Acker 1990; Williams 2000;
Blair-Loy 2003). On this view the penalty attaches to departures from continuous
employment and to signs of competing obligations, whoever shows them. Men who signal
caregiving are penalized too (Rudman and Mescher 2013; Williams, Blair-Loy, and
Berdahl 2013), and employment gaps are penalized whatever their reason (Kroft, Lange,
and Notowidigdo 2013; Weisshaar 2018). Because women take most caregiving leaves
(Goldin 2014), such a penalty is gendered in its consequences even when it is not
gendered in its application.

### 2.2 Alignment and the label

Commercial LLMs are trained after pretraining to follow instructions and to produce
outputs that raters and written principles prefer, including outputs that do not
treat people differently by protected attributes. Audits of automated hiring have
likewise asked mostly whether outcomes differ by protected attributes signaled through
names (An et al. 2025; Armstrong et al. 2024; Rozado 2025; Wilson and Caliskan 2024),
following the logic of anti-discrimination law, which asks whether outcomes differ
across protected categories (Barocas and Selbst 2016). Both practices are organized
around the category. Neither directly targets signals that are correlated with a
category but not named by it. If models learn from this kind of training to recognize
and handle protected categories when they are named, their behavior toward a signal
should depend on how directly it names one. Training against a category could produce
caution—equal treatment, correction in favor of the protected group, or refusal—where
the category is explicit, while leaving judgments about correlated signals as
pretraining left them.

### 2.3 Expectations along the gradient

Figure 1 arranges the components of the motherhood signal by how directly they refer
to gender and states what the label account expects at each position.

- *Named gender* (an explicit "Gender: Female/Male" line): careful, developer-specific
  handling—parity, correction toward women, or refusal—rather than a penalty.
- *Implied gender* (a gendered first name): read, but acted on weakly; removing it
  should change little.
- *Correlated signals* (an employment gap; children and parenting activities):
  penalized, for anyone who carries them, as the ideal-worker account predicts.
- *Remedies*: an instruction protects the signal it names and not the ones it leaves
  unnamed.

The gender-statistical account makes contrary predictions: a penalty for mothers but
not fathers, which shrinks when gender is removed. The framework also says where to
look. Selection is comparative, and a penalty that reflects relative judgments about
availability may surface only when applicants compete, so the expectations are tested
at several decision margins. We state these as orienting expectations; the tests
specified before data collection are listed in Section 3.4.

## 3. Study 1: Design

Study 1 is a correspondence-style audit (Bertrand and Mullainathan 2004) of LLM
screeners. Every estimate compares a résumé with itself, with and without a signal,
so applicant quality is held constant by construction.

### 3.1 Unbundling the correlated signals

Table 1 lists the signals. Every application includes a short cover note, so
conditions differ only in what the note and résumé say. The *parent* signal adds
"married with two children" to the note and a parent-teacher association line to the
résumé; *parent with leave* adds an eight-month "Parental leave" entry. Three placebos
separate the components: a *travel gap* with the same dates isolates the interruption;
*parental leave only*, without children, isolates the caregiving label; and a
length-matched *personal* line isolates disclosure. The comparisons yield four
components: the interruption (travel gap against equal treatment), its caregiving
label (parental leave only minus travel gap), family signals on top of a labeled
leave (parent with leave minus parental leave only), and parenthood without a gap
net of disclosure (parent minus personal). Because travel might itself be stigmatized,
a later phase substitutes two neutral labels with the same dates ("Job search after
company closure," "Full-time certification program"). *Parent with commitment
evidence* and a *pregnancy* signal, for women only, complete the set. The signals are
deliberately explicit; the parental-leave gap is the most realistic and anchors the
decomposition.

### 3.2 Moving along the gradient: how gender is conveyed

Gender information is varied at four levels that correspond to positions in Figure 1:
the first name alone (implied); the name plus a header line stating "Gender:
Female/Male" (named); a gender-neutral initial plus that line (named, without the name);
and initials only (gender removed). Names are six per gender from Bertrand and
Mullainathan (2004), all coded as White to hold race constant (Gaddis 2017), rotated
within every condition. Direct choices between a woman and a man with the same family
status measure gender preference as such. A perception check confirms that models read
implied gender: whenever a model used a gendered pronoun in an explanation, it matched
the name or header in every case, and gendered pronouns all but disappeared under
initials only. Asked directly, however, models often answered "unknown" for names
(Luna 34 percent, Haiku 58 percent) while stating explicit headers correctly in every
case—an early sign that what models *say* about gender is itself a trained behavior.

### 3.3 Decision margins and remedies

Signals are evaluated at four margins: *scoring* one applicant (fit on a ten-point
scale, interview recommendation, salary, four ratings); *choosing* between two
finalists of the same gender, one with the signal and one without (counterbalanced;
equal treatment = 50 percent); *shortlisting* three of six applicants, one with the
signal (impact ratio relative to the same résumé without it, comparable to the
four-fifths rule); and *declining to decide*—refusing or withholding a salary—recorded
as an outcome. A remedies phase repeats the pairwise tasks under three system prompts:
none, a generic equal-employment-opportunity prompt, and that prompt plus "do not
penalize employment gaps taken for caregiving," which names the gap but not the family
signals.

### 3.4 Models, materials, and inference

We audit four widely available, low-cost models—DeepSeek V4.1 Flash, Claude Haiku 5.5,
GPT-6 Luna, and Qwen 3.8 Flash—pinned to dated versions and single endpoints, with
reasoning disabled, structured output, and no system prompt except in the remedies
phase. The materials are 154 résumés validated as qualified for 28 occupations, 20
spanning occupational female share (4.7 to 97.1 percent) and wages and 8 chosen to
weaken the correlation between female share and care work. Data were collected in
four phases between October 14 and 30, 2026 (616,419 logged calls).

Standard errors are clustered at the design's units: pairwise choices by the unordered
pair of résumés (40 pairs in the main occupations, 16 in the added ones), scores by
résumé, shortlists by occupation with résumé and position fixed effects. Effective
sample sizes are set by résumé pairs, not calls. Tests use the Holm correction within
families; claims of no difference are tested for equivalence at ±5 percentage points;
few-cluster tests are checked with wild cluster bootstrap; and main tests are
re-estimated as linear probability models with controls. Responses produced by repair
passes are excluded from choice analyses, and refusals and unusable answers are
analyzed as outcomes and bounded (Section 4.4). Designs and confirmatory tests were
specified in analysis plans committed before each paid run; the ±5-point bound for the
second phase was chosen after its data were collected but before the tests were run,
and was specified in advance for the remedies phase. The study was not registered
externally; other analyses are labeled exploratory, and cross-model comparisons are
descriptive.

## 4. Study 1: Results

We begin at the correlated end of the gradient, where the label account expects the
largest effects, then move to named gender and to remedies. Differences are in
percentage points ("points").

### 4.1 Correlated signals: a caregiver penalty

*It appears where selection happens.* Family signals barely move the scores models give
a single applicant: relative to the same résumé without the signal, the parent signals
change women's fit ratings by at most 0.35 points on a ten-point scale and interview
recommendations by at most 1.5 percentage points, and Haiku rates mothers 0.34 points
*higher*. When applicants compete, the same signals are costly (Table 2). A mother
returning from parental leave is chosen against an equally qualified childless woman
31 percent of the time by DeepSeek, 23 by Qwen, 19 by Luna, and 11 by Haiku—the model
that scores her higher. In shortlisting, mothers reach the shortlist at 71, 75, and 78
percent of their childless rate with DeepSeek, Qwen, and Luna, each below the
four-fifths threshold, and at 25 percent with Haiku. Choices are not magnified scores:
a noise model built from each model's own rating variability predicts far smaller
penalties than observed in seven of eight model-signal combinations (Figure 2), and
the penalty remains 9 to 32 points among résumé pairs with clear quality differences.

*It consists of the interruption and the family signals, not the label.* Table 3 and
Figure 3 decompose the parent-with-leave penalty (mothers, explicit gender, 40 résumé
pairs). An eight-month gap labeled travel costs 10.5 to 26.0 points. Calling it
parental leave adds nothing—the label is equivalent to zero for Haiku and 1.7 to 6.7
points *less* costly than travel for the other models—and travel was not unusually
stigmatized: no neutral label was significantly more costly than travel after
correction, Qwen penalized travel 4.3 to 5.4 points more than either neutral label,
and the largest estimate in the other direction was DeepSeek's certification label for
women (4.0 points, Holm p = .14). Adding children and parenting activity to a résumé
that already carries a labeled leave costs a further 10.6 to 17.4 points, and
parenthood without a gap, net of the personal placebo, costs 7.3 to 19.2 points.
Commitment evidence does not restore equal treatment (Table 2). The family-signal and
parenthood contrasts survive Holm correction in 23 of 24 tests across six alternative
samples, and "greedy" availability language in job ads deepens the leave penalty for
some model–gender combinations, as an availability norm would imply (Section 4.4).

*It does not depend on gender.* Moving from implied gender to no gender at all changes
nothing. In the added occupations, the parent penalty with gendered names differs from
the penalty under initials only by +0.6 (DeepSeek), −0.5 (Haiku), −1.3 (Luna), and
+0.3 points (Qwen); in seven of eight model-signal combinations the difference is
statistically equivalent to zero within ±5 points, and in the eighth (DeepSeek's leave
signal) the interval reaches 5.6 (Figure 4). Shortlisting ratios likewise barely move
across the four levels of gender information. Fathers are chosen below equal treatment
in every cell of every model—a father returning from leave is chosen 31, 26, 18, and
13 percent of the time by DeepSeek, Qwen, Luna, and Haiku—and there is no fatherhood
bonus. Mother–father differences are small and not significant after correction in
three models (Table 4); Haiku chooses mothers 4.4 points less often than fathers
(Holm p = .02).

*The models' explanations follow the decomposition (exploratory).* In LLM-coded
explanations of pairwise choices (DeepSeek V4.1 Flash coder, Qwen 3.8 Flash second
coder; κ = .71 to .93 for the six codes used, lower for availability and family on
non-DeepSeek explanations), the gap was cited in 24 to 91 percent of losses for the gap
signals and at most 4 percent for parent signals without a gap, and family was cited
for parent signals but never for the travel gap or the personal placebo; all twelve
pre-stated contrasts survived Holm correction (Supplementary Figure S1). Explanations
for losing parents often called family information irrelevant—for DeepSeek and Qwen
much more often when the parent lost than when the parent won (53 vs. 19 and 90 vs. 42
percent). These are stated justifications, coded without human validation, not causes.

At the correlated end of the gradient, then, the models apply a caregiver penalty: a
penalty on time out of work and on visible family responsibility, shared by all four
vendors in sign, borne by women and men alike.

### 4.2 Named gender: careful, vendor-specific handling

At the named end, the label account expects caution rather than a penalty, and
behavior shaped by each developer. That is what we observe (Table 5, Figure 5). In
direct choices between a woman and a man with the same family status, naming gender
explicitly moves models in different directions. Luna's mild preference for women under
names (.522 childless, .577 parents) grows with an explicit gender line (.587 and
.647). Haiku's slight preference for mothers under names (.544) disappears with an
explicit line (.498; .471 with initials). DeepSeek shows a small, stable preference
for women (.535 to .548 for mothers). Qwen stays within five points of parity at every
level, as equivalence tests confirm (its largest deviation, a 1.8-point tilt toward
childless women under initials, is significant after correction). None of these is a
penalty on women; two are corrections toward or past parity.

Caution also takes the form of declining to decide, concentrated in one vendor and in
the cells where gender or family is salient. Haiku refused to choose in roughly 5
percent of mother-versus-father and parent-with-leave comparisons, against about 0.1
percent for the placebo signals. It withheld any salary for 19.8 percent of pregnant
applicants (3.1 percent for childless women), and for 27.5 percent when gender was
stated explicitly (Figure 6). Haiku's explanations frame withholding as protective,
but it has a cost: pregnant applicants without an offer were recommended for interview
29.9 percent of the time, against every time when an offer was made, a net interview
penalty of 9.4 points relative to childless women. Caution, in other words, does not
guarantee equal treatment; it relocates the decision.

### 4.3 Remedies: an instruction protects what it names

The label account also predicts how remedies work. Table 6 reports the remedies phase
(48,000 calls). A generic equal-opportunity prompt, which names gender but not
caregiving, left the caregiver penalty in place in every model, with effects that
depended on the vendor: none for DeepSeek, a reduction of the plain parent penalty
for Luna (5.0 points), substantial reductions for Haiku (6.6 and 12.2 points), and a
*deepening* for Qwen (4.7 and 5.3 points). Adding "do not penalize employment gaps
taken for caregiving" reduced the interruption penalty—the signal it names—by 4 to 14
points in all four models, but left the family-signal penalty essentially unchanged
except in Haiku. No arm reached equal treatment. Named gender behavior responded more
readily: Luna's preference for mothers over fathers fell from .640 to .557 under the
generic prompt. Naming a signal moved it toward protection; leaving it unnamed did not.

### 4.4 Robustness and supplementary results

Refusals and unusable answers cannot explain the caregiver penalty. Even if every
missing choice had gone to the parent, the share of mothers with leave chosen in the
main run could rise at most to about .32 (DeepSeek), .13 (Haiku), .22 (Luna), and .39
(Qwen); Qwen's wider bound reflects its higher rate of unusable output, which is also
higher in parent cells (Round 15 formalizes these bounds). Linear probability models
with controls reproduce the main tests; wild cluster bootstrap p-values change no
conclusion; estimates drifted 0.8 to 2.4 points between phases, within tolerance.
Supplementary results: paired salary offers are 1.7 to 2.3 percent lower for mothers;
greedy availability language in job ads adds to the leave penalty for DeepSeek
mothers (2.7 points) and, combined with family-friendly language, for DeepSeek
applicants and Haiku mothers (5.2 to 8.0 points), while family-friendly language alone
never helps; and the penalty shows no robust association with occupational female
share, wages, or task composition.

## 5. Study 2 (planned): Where does the gradient come from?

Study 1 shows that behavior lines up with the gradient; it cannot show that alignment
produced it. The four audited models are aligned commercial systems without
unaligned counterparts, and their developers' training choices are not observed.
Study 2 tests the mechanism directly by holding the model fixed and varying only its
stage of training.

*Models.* Open-weight model families that release checkpoints from successive training
stages—a pretrained base model, an instruction-tuned model, and a preference-tuned
model—allow the same network to be compared before and after each stage (for example,
the OLMo family, which publishes its post-training checkpoints and data). We will use
two or more such families, at sizes that run on a single 80GB GPU, so that conclusions
do not rest on one developer.

*Measurement.* Base models do not reliably follow instructions or produce structured
output. We therefore measure choices from the models' probabilities rather than their
text: for each pairwise prompt, the log-probability of answering "A" versus "B,"
averaged over both orderings of the candidates. The same quantity is computed for
every checkpoint, so stages are compared on one scale. The Study 1 materials and
conditions are reused: the placebo ladder at the correlated end, names versus initials
at the implied position, and explicit gender lines and direct woman-versus-man pairs at
the named end.

*Predictions.* If protection follows the label because of alignment, then (1) named
gender effects should be present in base models and shrink, or reverse toward women,
after instruction and preference tuning; (2) the caregiver penalty should be present at
every stage and change little; and (3) the gap between the named and correlated ends
should widen across stages. Evidence against the account would be a caregiver penalty
that emerges only after alignment, or named-gender effects that are already absent in
base models.

*Extension.* Because the models are open, Study 2 can also ask what changes inside
them: whether the representation of gender that a model forms from a résumé differs
across training stages, and whether caregiving signals activate that representation.
Steering experiments that suppress or amplify a gender direction would test whether
the caregiver penalty depends on it.

## 6. Discussion

### 6.1 The framework revisited

Figure 7 returns to the framework with Study 1's findings in place. At the correlated
end, caregiving signals carry a large penalty for anyone who shows them. At the
implied position, models read gender but act on it little: removing it changes nothing.
At the named end, gender elicits small and vendor-specific handling—correction, parity,
or refusal—rather than a penalty. And an instruction protects what it names. The
gender-statistical account, which places the penalty on mothers as women, does not fit;
the ideal-worker account describes the penalty that remains; and the label account
describes why the remaining penalty takes the form it does.

The caregiver penalty itself has two parts with different characters. The
interruption penalty behaves like an inference about availability (Phelps 1972; Kroft,
Lange, and Notowidigdo 2013; Weisshaar 2018): any gap is costly whatever it is called,
availability language deepens it, and naming it in an instruction reduces it. The
family-signal penalty behaves like a norm: it attaches to children and parenting
activity, persists on top of a gap already labeled as parental leave, is not offset by
evidence of commitment, and does not respond to instructions—like the normative
component of the human motherhood penalty (Benard and Correll 2010), except that it is
applied to fathers too.

### 6.2 Gender-neutral in form, gendered in effect

Protection that follows the label leaves the consequences of correlated signals
unprotected. Caregiving interruptions and visible family responsibilities are carried
disproportionately by women (Goldin 2014), so a rule that penalizes them reproduces a
gender gap through the distribution of signals rather than the treatment of
individuals. Figure 8 shows how quickly this can happen: applying each model's
measured shortlisting penalty to pools in which more women than men carry a caregiving
signal, Haiku's gender-blind penalty produces a women-to-men shortlisting ratio below
the four-fifths line once more than 31 percent of women carry the signal (men at 5
percent); the thresholds are 73, 84, and 93 percent for DeepSeek, Qwen, and Luna.
Prevalence is a scenario parameter here, but the structure is the one disparate-impact
doctrine was designed to capture, and the one the ideal-worker literature has long
described: a norm that disadvantages women without naming them (Acker 1990; Williams
2000).

The broader implication concerns how discrimination responds to its regulation. When
a protected category is policed, decisions can continue through correlated signals
that are not protected as such, as research on bans of criminal-record questions has
shown (Agan and Starr 2018). Alignment adds a twist: here the system itself has been
trained around the category, and that training appears to make it attentive to how a
signal is labeled rather than to what the signal does.

### 6.3 Implications for auditing

The framework explains why standard audits would miss these patterns. Audits keyed to
protected categories compare women and men and find little; they need to compare
applicants with and without caregiving signals. Audits that score single applicants
find small effects; the penalty lives in choices and shortlists. Audits that drop
non-answers miss the largest pregnancy effect, a refusal to price that carries a denial
of interviews. And audits that ask models about gender measure what models are willing
to say, not what they use. For deployers, the remedies phase cautions that fairness
instructions protect what they name and can backfire for some vendors.

### 6.4 Limitations

The family signals are explicit, and real résumés carry weaker ones. The materials are
US-oriented, English, text-only, and hold race constant. Pregnancy has no male
counterpart. Outcomes are recommendations, not offers or callbacks. The models are four
low-cost versions at fixed dates; larger models and commercial products may differ.
Pools and pairs are constructed, so the design identifies the effect of a signal, not
hiring rates. The disparate-impact analysis uses scenario prevalence values. The coding
of explanations relies on LLM coders without human validation. Effective sample sizes
are set by résumé pairs (40 or 16 per comparison). Above all, Study 1 shows that
behavior is consistent with the label account; Study 2 is needed to show that alignment
produces it.

## 7. A Research Agenda

The label account generates questions beyond this paper. We list those we consider most
informative, roughly in order of how directly they test the account.

1. *Rewording the signal.* If protection follows the label, wording that names a
   protected category should be treated differently from wording that does not, even
   when the underlying fact is the same. Candidate contrasts: "maternity leave" and
   "paternity leave" versus "parental leave"; "pregnancy leave" versus "medical leave";
   gender-coded activities (a women's sports team, a sorority) versus neutral ones.
2. *Other protected categories along the same gradient.* Age offers a clean test:
   stated age (named) versus graduation year (correlated); disability: "disability
   leave" versus "medical leave" versus an unexplained gap; race: stated race versus
   names versus neighborhoods or institutions. The account predicts the same ordering
   in each case.
3. *Refusal as an outcome.* Where and why models decline to decide—by category, by
   explicitness, and by vendor—and what happens to applicants they decline.
4. *Representations and steering.* In open models, whether caregiving signals activate
   internal gender representations, how alignment changes those representations, and
   whether steering them changes decisions (Study 2 extension).
5. *Human comparison.* The same unbundling design with human evaluators, to compare
   which components humans and models penalize on identical materials—the clearest way
   to say whether models reproduce, transform, or exceed the human penalty.
6. *Realistic signals and deployed systems.* Weaker, naturally phrased caregiving
   signals; larger models; commercial screening products with their own system prompts;
   and other labor markets and languages, including markets in which explicit gender
   and age fields are standard.
7. *Group consequences with real prevalence.* Estimates of how often women and men
   applicants carry caregiving signals, from household surveys, to turn the
   disparate-impact scenario into an estimate.

## 8. Conclusion

Asked whether LLM résumé screeners penalize mothers, Study 1's answer is that the models
we studied penalize caregivers. They penalize time out of work and visible family
responsibility regardless of gender, and only when applicants are compared, while
handling explicitly named gender with care that differs from vendor to vendor. We have
argued that this is what protection that follows the label looks like: systems trained
around a protected category treat the category carefully and its correlates freely.
Because the correlates of motherhood are carried mostly by women, such systems can pass
fairness checks organized around gender while reproducing the motherhood penalty in
effect. Whether alignment is the cause is the question Study 2 is designed to answer.

---

## References

Items marked ◆ are to be checked against the source before submission; items marked
† were added in the manuscript and are not yet in the report's verified list.

- Acker, Joan. 1990. "Hierarchies, Jobs, Bodies: A Theory of Gendered Organizations." *Gender & Society* 4(2):139–158.
- Agan, Amanda, and Sonja Starr. 2018. "Ban the Box, Criminal Records, and Racial Discrimination: A Field Experiment." *Quarterly Journal of Economics* 133(1):191–235. †
- An, Jiafu, Difang Huang, Chen Lin, and Mingzhu Tai. 2025. "Measuring Gender and Racial Biases in Large Language Models: Intersectional Evidence from Automated Resume Evaluation." *PNAS Nexus* 4(3):pgaf089.
- Armstrong, Lena, Abbie Liu, Stephen MacNeil, and Danaë Metaxa. 2024. "The Silicon Ceiling: Auditing GPT's Race and Gender Biases in Hiring." arXiv:2405.04412.
- Barocas, Solon, and Andrew D. Selbst. 2016. "Big Data's Disparate Impact." *California Law Review* 104(3):671–732. †
- Benard, Stephen, and Shelley J. Correll. 2010. "Normative Discrimination and the Motherhood Penalty." *Gender & Society* 24(5):616–646.
- Bertrand, Marianne, and Sendhil Mullainathan. 2004. "Are Emily and Greg More Employable than Lakisha and Jamal?" *American Economic Review* 94(4):991–1013.
- Blair-Loy, Mary. 2003. *Competing Devotions: Career and Family among Women Executives*. Cambridge, MA: Harvard University Press. †
- Budig, Michelle J., and Paula England. 2001. "The Wage Penalty for Motherhood." *American Sociological Review* 66(2):204–225. †
- Correll, Shelley J., Stephen Benard, and In Paik. 2007. "Getting a Job: Is There a Motherhood Penalty?" *American Journal of Sociology* 112(5):1297–1338.
- EEOC. 1978. Uniform Guidelines on Employee Selection Procedures. 43 FR 38290.
- European Union. 2024. Regulation (EU) 2024/1689 (Artificial Intelligence Act).
- Frermann, Lea, Sheilla Njoto, Marc Cheong, and Leah Ruppanner. 2023. "Gender Bias and Parental-Leave Gaps in ChatGPT Résumé Ranking." University of Melbourne. ◆
- Gaddis, S. Michael. 2017. "How Black Are Lakisha and Jamal? Racial Perceptions from Names Used in Correspondence Audit Studies." *Sociological Science* 4:469–489.
- Goldin, Claudia. 2014. "A Grand Gender Convergence: Its Last Chapter." *American Economic Review* 104(4):1091–1119. †
- Kroft, Kory, Fabian Lange, and Matthew J. Notowidigdo. 2013. "Duration Dependence and Labor Market Conditions: Evidence from a Field Experiment." *Quarterly Journal of Economics* 128(3):1123–1167.
- Phelps, Edmund S. 1972. "The Statistical Theory of Racism and Sexism." *American Economic Review* 62(4):659–661. ◆
- Rozado, David. 2025. "Gender and Positional Biases in LLM-Based Hiring Decisions." arXiv:2505.17049.
- Rudman, Laurie A., and Kris Mescher. 2013. "Penalizing Men Who Request a Family Leave: Is Flexibility Stigma a Femininity Stigma?" *Journal of Social Issues* 69(2):322–340.
- Veldanda, Akshaj Kumar, et al. 2023. "Investigating Algorithmic Hiring Bias in the Era of ChatGPT." arXiv:2310.05135. ◆
- Weisshaar, Katherine. 2018. "From Opt Out to Blocked Out: The Challenges for Labor Market Re-entry after Family-Related Employment Lapses." *American Sociological Review* 83(1):34–60.
- Williams, Joan C. 2000. *Unbending Gender: Why Family and Work Conflict and What to Do About It*. New York: Oxford University Press.
- Williams, Joan C., Mary Blair-Loy, and Jennifer L. Berdahl. 2013. "Cultural Schemas, Social Class, and the Flexibility Stigma." *Journal of Social Issues* 69(2):209–234.
- Wilson, Kyra, and Aylin Caliskan. 2024. "Gender, Race, and Intersectional Bias in Resume Screening via Language Model Retrieval." AIES.
- Yin, Leon, Davey Alba, and Leonardo Nicoletti. 2024. "OpenAI's GPT Is a Recruiter's Dream Tool. Tests Show There's Racial Bias." *Bloomberg*.
