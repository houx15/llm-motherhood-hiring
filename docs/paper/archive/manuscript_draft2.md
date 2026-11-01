# From Motherhood Penalty to Caregiver Penalty: How Large Language Model Résumé Screeners Treat Family Signals

Yuxin Hou, Princeton University

*Manuscript draft 2 (2026-10-31). Numbers are taken from the claim-checked report;
values in Section 4.1 that depend on the amplification and noise-model analyses are
pending a code fix (SPEC_FINALIZE Round 14).*

---

## Abstract

Large language models (LLMs) now screen job applicants. We ask whether they
reproduce the motherhood penalty and, if so, what they penalize. On a résumé,
motherhood is a bundle of three signals that human hiring cannot pull apart: the
applicant is a woman, she has family responsibilities, and she has often been out of
work. We unbundle these signals in an audit of four widely used models (616,419
decisions, 28 occupations), adding and removing each one from otherwise identical
résumés, removing all gender information, and observing four decision margins:
scoring one applicant, choosing between two, shortlisting from a pool, and declining
to decide. The models do not penalize being a woman. They penalize caregiving. The
penalty is invisible when applicants are scored one at a time but large when they are
compared: a mother returning from parental leave wins a head-to-head choice against
an equally qualified childless woman 11 to 31 percent of the time. It is unchanged
when gender information is removed, falls on fathers as much as on mothers, and
consists of a penalty for interrupted employment plus a further penalty for family
signals. Gender-specific behavior exists only as a thin layer that differs by vendor.
Fairness instructions reduce the interruption penalty but not the family-signal
penalty. We interpret the pattern as the ideal-worker norm rendered as a formally
gender-neutral rule, which can reproduce a gendered outcome because women carry
caregiving signals more often than men.

---

## 1. Introduction

Mothers pay a price in the labor market that fathers do not. They earn less than
comparable childless women (Budig and England 2001), and in audit and laboratory
studies employers rate them as less competent and committed, recommend them for hire
less often, and offer them lower salaries, while fathers are not penalized (Correll,
Benard, and Paik 2007). The penalty persists when mothers present direct evidence of
commitment, which suggests that it rests on norms about what mothers should do as
well as on inferences about what they can do (Benard and Correll 2010).

Hiring is now partly delegated to software. Résumé screening is among the most common
commercial uses of large language models, and among the most regulated: US selection
procedures are judged by their disparate impact on protected groups, and the European
Union classifies AI systems used in recruitment as high-risk (EEOC 1978; European
Union 2024). Whether these systems reproduce the motherhood penalty is therefore a
pressing question. This paper argues that it is also an opportunity to answer an older
one: *what, exactly, is penalized when mothers are penalized?*

On a résumé, motherhood is not a single signal. It bundles three: the applicant is a
woman; she has family responsibilities, which applications reveal through mentions of
children, parenting activities, or caregiving leave; and she has often been out of
work. Each component corresponds to a distinct explanation of the penalty. If
employers penalize women as presumed caregivers, the gender component matters. If
they penalize anyone who departs from the norm of the fully available "ideal worker"
(Acker 1990; Williams 2000), the family and interruption components matter, whoever
carries them. In human hiring the components travel together, and they are hard to
separate: an employer who sees a mother's name sees her gender, and audits cannot
remove gender while keeping the family situation visible. An LLM screener can be shown
the same résumé thousands of times with one component added or removed at a time,
including with every trace of gender removed. That makes it possible to unbundle the
motherhood signal.

Figure 1 lays out the framework that organizes the paper. We treat the motherhood
signal as three separable components (left), ask which of them an LLM screener
penalizes and whether it needs to know the applicant's gender to do so (center), and
observe the result at four decision margins (right): scoring a single applicant,
choosing between two finalists, shortlisting from a pool, and declining to decide.
Three questions follow. *Where* does a family-status penalty appear? *What* part of
the signal is penalized? And *with what consequences*—for remedies that developers
and employers rely on, and for women and men as groups?

Our answers are as follows. The penalty appears only when applicants are compared;
single-applicant scores barely move. It is a penalty on caregiving rather than on
gender: it is unchanged when the model cannot know the applicant's gender, it falls on
fathers as much as on mothers, and it has two parts—a penalty for any interruption in
employment and a further penalty for overt family signals. Gender-specific behavior
does exist, but as a thin layer that differs from vendor to vendor. Fairness
instructions reach the interruption penalty but not the family-signal penalty. And
because women carry caregiving signals more often than men, a rule that is
gender-blind in form can produce a gendered outcome.

The paper makes three contributions. Substantively, it separates components of the
motherhood penalty that human hiring confounds and shows which survive in automated
screening. Theoretically, it suggests that when gender is the category developers
train against, discrimination may persist through correlated signals that are not
protected as such, consistent with the ideal-worker account. Methodologically, it
shows that audit design determines what is found: audits that score single
applicants, discard non-answers, or manipulate gender only through names would certify
these systems as fair.

## 2. Background

### 2.1 Three components, three accounts

Explanations of the motherhood penalty can be read as claims about which component of
the signal does the work (Figure 1, center).

*Gender-statistical accounts* hold that employers treat motherhood as a proxy for
lower expected availability and productivity, and that the inference is gendered:
mothers, not fathers, are expected to reduce their commitment (Phelps 1972; Correll,
Benard, and Paik 2007). A normative variant holds that mothers violate expectations
of devotion to family, so that evidence of commitment does not erase the penalty
(Benard and Correll 2010). Both predict a penalty specific to mothers, which requires
the evaluator to know the applicant's gender.

*Ideal-worker accounts* locate the penalty in the organization of work. Organizations
are built around an abstract worker who is fully available and free of outside
obligations (Acker 1990); the norm is gender-neutral in wording but was modeled on men
whose care work was done by others (Williams 2000; Blair-Loy 2003). On this view the
penalty attaches to signs of competing obligations and to departures from continuous
employment, whoever shows them. Two strands of evidence support the distinction. Men
who signal caregiving are penalized too (Rudman and Mescher 2013; Williams, Blair-Loy,
and Berdahl 2013), and employment gaps are penalized whatever their reason (Kroft,
Lange, and Notowidigdo 2013; Weisshaar 2018). Because women take most caregiving
leaves (Goldin 2014), such a penalty is gendered in its consequences even when it is
not gendered in its application.

*An alignment account* is specific to the machine setting. Commercial LLMs are
trained and evaluated to avoid differential treatment of protected groups, and audits
of automated hiring have mostly asked whether outcomes differ by protected attributes
signaled through names (An et al. 2025; Armstrong et al. 2024; Rozado 2025; Wilson
and Caliskan 2024), following the logic of anti-discrimination law (Barocas and
Selbst 2016). Systems may therefore be scrutinized and corrected along the gender
dimension while correlated signals that are not themselves protected go unexamined.
This account predicts little direct gender bias, bias that varies with each
developer's choices, and untouched penalties on unprotected correlates.

### 2.2 Expectations

Mapped onto the framework, the accounts make distinguishable predictions. The
gender-statistical account predicts that the gender component carries the penalty:
mothers are penalized more than fathers, and the penalty shrinks when gender
information is removed. The ideal-worker account predicts that the family and
interruption components carry it: fathers are penalized as much as mothers, removing
gender information changes nothing, and both an unexplained gap and overt family
signals are costly. The alignment account predicts a weak and vendor-specific gender
component that responds to instructions. The last two can hold together. We state
these as orienting expectations; the confirmatory tests specified before data
collection are listed in Section 3.5.

The framework also implies where to look. Selection decisions are comparative, and a
penalty that reflects relative judgments about availability may surface only when
applicants compete. If audits measure only single-applicant scores, they may miss it.

## 3. Design

The study is a correspondence-style audit (Bertrand and Mullainathan 2004) carried out
on LLMs rather than employers. Its design follows Figure 1: one set of manipulations
unbundles the signal, a second controls what the model knows about gender, a third
varies the decision margin, and a fourth tests remedies. Every estimate compares a
résumé with itself, with and without a component, so that applicant quality is held
constant by construction.

### 3.1 Unbundling the signal

Table 1 lists the signals. Every application includes a short cover note, so that
conditions differ only in what the note and the résumé say. The *parent* signal adds
"married with two children" to the note and a parent-teacher association line to the
résumé. *Parent with leave* adds an eight-month "Parental leave" entry to the work
history. Three placebo signals separate the components. A *travel gap* inserts an
eight-month "Career break—extended travel" with the same dates, isolating the
interruption from any family content. *Parental leave only* inserts the leave entry
without children or parenting activity, isolating the caregiving label. A *personal*
placebo adds a length-matched non-family line, isolating the cost of disclosing
anything personal. Comparing these conditions yields four components: the
interruption (travel gap against equal treatment), its caregiving label (parental
leave only minus travel gap), family signals on top of a labeled leave (parent with
leave minus parental leave only), and parenthood without a gap net of disclosure
(parent minus personal). Because "extended travel" may itself be stigmatized, a later
phase replaces it with two neutral labels for the same dates—"Job search after company
closure" and "Full-time certification program." Two further signals probe the normative
account: *parent with commitment evidence* adds objective commitment bullets, and a
*pregnancy* signal, for women only, states that the applicant is pregnant.

The signals are deliberately explicit, which favors identification over realism. The
parental-leave gap is the most realistic of them and anchors the decomposition.

### 3.2 Controlling gender information

In the main run, gender is conveyed by first names: six per gender from Bertrand and
Mullainathan (2004), all coded as White to hold race constant (Gaddis 2017), rotated
within every condition. A second phase varies gender information at four levels: the
name alone; the name plus a header line stating "Gender: Female/Male"; a gender-neutral
initial plus that line; and initials only, which removes gender entirely. If the
penalty is about gender, it should change across these levels. The same phase includes
direct choices between a woman and a man with the same family status, which measure
gender preference as such. A perception check confirms that the manipulation works.
Asked directly, models stated the gender in explicit header lines correctly in every
case but often answered "unknown" for names (Luna 34 percent, Haiku 58 percent); yet
whenever a model used a gendered pronoun in an explanation, it matched the name or
header in every case, and gendered pronouns all but disappeared under initials only.
The models read gender from names; the direct question measures their willingness to
say so.

### 3.3 Observing decision margins

Each signal is evaluated at four margins. In *scoring*, the model evaluates one
applicant: fit on a ten-point scale, an interview recommendation, a salary, and
ratings of competence, commitment, likability, and promotability. In *pairwise
choice*, it picks one of two finalists of the same gender, one with the signal and one
without, with résumé roles and screen positions counterbalanced; under equal treatment
the applicant with the signal is chosen half the time. In *shortlisting*, it selects
three of six applicants, one of whom carries the signal; the outcome is that
applicant's shortlisting rate relative to the same résumé without the signal, an
impact ratio comparable to the four-fifths rule. *Declining to decide*—withholding a
salary offer or refusing to answer—is recorded as an outcome rather than discarded.

### 3.4 Testing remedies

A final phase asks whether the instructions that deployers typically add remove the
penalty. The same pairwise tasks are run under three system prompts: none (the default
elsewhere in the study), a generic equal-employment-opportunity prompt, and the same
prompt plus "do not penalize employment gaps taken for caregiving." The second prompt
names the interruption but not the family signals, which lets us ask whether the two
components respond differently. A further analysis translates each model's measured
penalty into group outcomes for women and men under different prevalences of
caregiving signals.

### 3.5 Models, materials, and inference

We audit four widely available, low-cost models—DeepSeek V4.1 Flash, Claude Haiku
5.5, GPT-6 Luna, and Qwen 3.8 Flash—pinned to dated versions and single provider
endpoints, with extended reasoning disabled, structured output, and no system prompt
except in the remedies phase. They stand for high-volume screening configurations;
larger models are not tested. The materials comprise 154 résumés validated as
qualified for 28 occupations: 20 spanning the joint distribution of occupational
female share (4.7 to 97.1 percent) and median wage, and 8 selected to weaken the
correlation between female share and care work (from .53 to .32). Résumés have
continuous eight-to-twelve-year histories and no gender or family wording. Data were
collected in four phases between October 14 and 30, 2026 (616,419 logged calls; total
cost $188.52 plus $0.66 for coding model explanations).

Standard errors are clustered at the units of the design: pairwise choices by the
unordered pair of résumés compared (40 pairs in the main occupations, 16 in the added
ones), with cluster-level degrees of freedom; scores by résumé; shortlists by
occupation with résumé and position fixed effects. Effective sample sizes are thus set
by résumé pairs, not by calls. We apply the Holm correction within each family of
tests, test claims of no difference for equivalence against a smallest effect of
interest of five percentage points (two one-sided tests), check few-cluster tests with
wild cluster bootstrap p-values, and re-estimate the main tests as linear probability
models with controls for position, prompt wording, and name. Responses produced by
repair passes after invalid output are excluded from choice analyses; validity was
99 to 100 percent.

The designs and confirmatory tests—penalties by margin, model, and gender;
mother–father differences; impact ratios; the placebo decomposition; gender-information
contrasts; direct gender choices; withholding; and the remedy and gap-label
hypotheses—were specified in analysis plans committed before each paid run. The
five-point equivalence bound for the second phase was chosen after its data were
collected but before the tests were run; it was specified in advance for the remedies
phase. The study was not registered externally. Other analyses are labeled
exploratory, and cross-model comparisons are descriptive.

## 4. Results

The results follow the three questions of Figure 1. Section 4.1 asks where the
penalty appears. Sections 4.2 to 4.4 ask what is penalized: the interruption and
family components (4.2), the gender component (4.3), and the gender-specific behaviors
that remain (4.4). Sections 4.5 and 4.6 ask about consequences. Differences are in
percentage points ("points").

### 4.1 Where: the penalty appears when applicants are compared

If a screener penalized family signals the way a human rater might, the penalty should
be visible in the scores it assigns. It is not. Relative to the same résumé without the
signal, the parent signals change women's fit ratings by at most 0.35 points on a
ten-point scale and interview recommendations by at most 1.5 percentage points. Claude
Haiku even rates mothers 0.34 points *higher* than the same applicants without
children.

The same signals are costly when applicants compete (Table 2). In pairwise choice,
parents are chosen less than half the time in every model and every condition. A
mother returning from parental leave is chosen against an equally qualified childless
woman 31 percent of the time by DeepSeek, 23 percent by Qwen, 19 percent by Luna, and
11 percent by Haiku—the model that scores her higher. In shortlisting, the same mothers
reach the shortlist at 71 (DeepSeek), 75 (Qwen), and 78 (Luna) percent of the rate
they achieve without the signal, each below the four-fifths threshold, and at 25
percent with Haiku.

Comparison does not merely magnify small score differences. Choices respond to
ordinary differences in résumé quality at 13 to 18 points of choice probability per
fit point; by that yardstick the family signals act like quality losses of 0.9 to 2.0
fit points, many times their effect on scores. A noise model that converts each model's
score gap into a predicted choice probability predicts far smaller penalties than
observed in seven of eight model-signal combinations (Figure 2); the exception is
DeepSeek's leave signal. The penalty is larger when résumés are close in quality, as
tie-breaking would imply, but remains 9 to 32 points among pairs with clear quality
differences. For Haiku, whose score effect is positive, no magnification of scores can
produce the observed choice penalty.

The first answer, then, is that the penalty lives at the comparative margins where
selection actually happens. The remaining analyses measure it there.

### 4.2 What: interruptions and family signals

Table 3 and Figure 3 decompose the parent-with-leave penalty in pairwise choice, for
mothers in the main occupations with gender stated explicitly (40 résumé pairs). The
decomposition answers the ideal-worker account's two claims in turn.

*Interruption.* An eight-month gap labeled as travel, with no family content, costs
10.5 (DeepSeek) to 26.0 points (Luna). Calling the same gap parental leave adds
nothing: the label is statistically equivalent to zero for Haiku and is 1.7 to 6.7
points *less* costly than travel for the other three models. Travel was not an unusually
stigmatized reference. When it was replaced by company closure or certification, no
neutral label was significantly more costly than travel after correction; Qwen
penalized travel 4.3 to 5.4 points more than either neutral label, and seven of the
other twelve comparisons were statistically equivalent (the largest estimate in the
other direction was DeepSeek's certification label for women, 4.0 points, Holm
p = .14). What is penalized is time out of work, not its stated reason.

*Family signals.* Adding children and parenting activity to a résumé that already
carries a labeled parental leave costs a further 10.6 to 17.4 points, and parenthood
without any gap, net of the personal placebo, costs 7.3 to 19.2 points. Disclosure as
such is not the issue: the placebo costs about 3 points in three models and slightly
helps applicants with Haiku (3.7 points). Commitment evidence only partly offsets the
parent penalty (Table 2), as the normative account of the human penalty would lead one
to expect. The family-signal and parenthood contrasts survive Holm correction in 23 of
24 tests each across six alternative samples of occupations and gender information.

*Norm salience.* If the interruption penalty reflects an availability norm, making the
norm salient should deepen it. Job descriptions with "greedy" availability language
("must be available after hours and on weekends as needed, and travel up to 40% of the
time") add to the leave penalty for DeepSeek mothers (2.7 points) and, combined with
family-friendly language, for DeepSeek applicants of both genders and Haiku mothers
(5.2 to 8.0 points); family-friendly language alone never significantly helps.

*What the models say (exploratory).* Model explanations follow the decomposition. An
LLM coder (DeepSeek V4.1 Flash, temperature zero) classified the reasons given in
pairwise-choice explanations; a second coder (Qwen 3.8 Flash) re-coded 638 explanations
not written by Qwen. Six codes reached acceptable agreement (κ = .71 to .93); agreement
was lower for availability (.68) and family (.63) on explanations not written by
DeepSeek. When the applicant with the signal lost, the gap was cited in 24 to 91
percent of explanations for the three gap signals and in at most 4 percent for parent
signals without a gap; family was cited in 12 to 64 percent for parent signals and
never for the travel gap or the personal placebo (Figure 4). All twelve pre-stated
contrasts went in the predicted direction and survived Holm correction. Availability
concerns were common for DeepSeek and Qwen (39 to 52 percent of gap-signal losses) but
rare for Haiku and Luna (15 percent or less). Explanations for losing parents often
called family information irrelevant (Qwen 90 percent, Haiku 69, Luna 56, DeepSeek
53); for DeepSeek and Qwen such statements were concentrated in losses (19 and 42
percent when the parent won), for Haiku and Luna they were about as common either way
(64 and 50 percent). These are stated reasons, conditional on the outcome and coded
without human validation; they describe justifications, not causes.

### 4.3 What: the gender component

The gender-statistical account makes two predictions: the penalty should shrink when
the model cannot know the applicant's gender, and mothers should be penalized more
than fathers. Neither holds.

*Removing gender.* In the added occupations, the parent penalty with gendered names
differs from the penalty under initials only by +0.6 (DeepSeek), −0.5 (Haiku), −1.3
(Luna), and +0.3 points (Qwen), and the leave penalty likewise. In seven of eight
model-signal combinations the difference is statistically equivalent to zero within
±5 points; in the eighth, DeepSeek's leave signal, the interval reaches 5.6 points
(Figure 5). The design could detect differences of 3.0 to 5.4 points. Shortlisting
replicates the result: ratios barely move across the four levels of gender information
(for example, .64/.66/.66/.65 for DeepSeek and .15/.19/.17/.16 for Haiku).

*Fathers.* Fathers are chosen below equal treatment in every cell of every model; a
father returning from parental leave is chosen 31 (DeepSeek), 26 (Qwen), 18 (Luna),
and 13 percent (Haiku) of the time against a childless man (Table 2). There is no
fatherhood bonus. Mother–father differences on the same résumé pairs are small and,
in three models, not significant after correction (Table 4). Haiku is the exception: it
chooses mothers 4.4 points less often than fathers (Holm p = .02) and rates them lower
on commitment, and its mother–father gap differs significantly from each of the other
models.

The penalty, in short, does not require the model to know that the applicant is a
woman. It falls on caregivers.

### 4.4 The gender layer: thin and vendor-specific

What remains of gender is a set of behaviors that differ by vendor and surface mainly
when gender is made explicit. In direct choices between a woman and a man with the
same family status (Table 5, Figure 6), Qwen stays within five points of parity at
every level, as equivalence tests confirm (its largest deviation is a 1.8-point tilt
toward childless women under initials). DeepSeek shows a small preference for women
(.535 to .548 for mothers). Luna's preference for women is modest under names (.522
childless, .577 parents) and grows when gender is stated explicitly (.587 and .647).
Haiku moves the other way: its slight preference for mothers under names (.544)
disappears with an explicit gender line (.498; .471 with initials). Explicit gender
fields are therefore not neutral; they activate preferences that differ in direction
across vendors.

One vendor's gender layer also appears at the fourth margin. Asked for a salary, Haiku
proposes none for 19.8 percent of pregnant applicants in the main run—against 3.1
percent of childless women and 7.3 percent of married women—and for 27.5 percent when
gender is stated explicitly; other models withhold for pregnancy far less often (at
most 5.8 percent) (Figure 7). Haiku's explanations frame withholding as protective.
Its consequence is not: pregnant applicants without an offer are recommended for
interview 29.9 percent of the time, against every time when an offer is made, a net
interview penalty of 9.4 points relative to childless women. Among the offers that are
made, no model shows a meaningful pregnancy salary penalty. An audit that drops missing
salaries would conclude that pregnancy is not penalized.

### 4.5 Consequences: remedies reach one component, not the other

Deployers often add fairness instructions to a screener's system prompt. Table 6
reports the remedies phase (48,000 calls). The generic equal-opportunity prompt left
the caregiver penalty in place in every model, and its effect depended on the vendor:
none for DeepSeek, a reduction of the plain parent penalty for Luna (5.0 points) but not
of the leave penalty, substantial reductions for Haiku (6.6 and 12.2 points), and a
*deepening* of both penalties for Qwen (4.7 and 5.3 points). The targeted instruction
not to penalize caregiving gaps reduced the interruption penalty by 4 to 14 points in
all four models but left the family-signal penalty essentially unchanged except in
Haiku. No arm brought any model to equal treatment. The gender layer responded more
readily: Luna's preference for mothers over fathers fell from .640 to .557 under the
generic prompt.

The two components of the caregiver penalty thus behave differently. The interruption
penalty, which resembles an inference about availability, responds when an
instruction names it. The family-signal penalty, which no instruction names and which
resembles a norm, does not.

### 4.6 Consequences: a gender-blind rule, a gendered outcome

The caregiver penalty is blind to gender, but caregiving signals are not evenly
distributed. Applying each model's measured shortlisting penalty to applicant pools in
which more women than men carry a caregiving signal shows how the two combine (Figure
8). With men's prevalence fixed at 5 percent, Haiku produces an aggregate
women-to-men shortlisting ratio below the four-fifths line once more than 31 percent
of women carry the signal; the thresholds are 73 percent for DeepSeek, 84 for Qwen,
and 93 for Luna. At a prevalence of 20 percent among women, no model crosses the line
(ratios .88 to .96). We could not source gender-specific estimates of how many
applicants carry such signals, so prevalence is a scenario parameter; the thresholds
do not depend on it. The analysis illustrates the mechanism and shows how much the
answer depends on the vendor.

### 4.7 Additional analyses

In paired salary recommendations, models offer mothers 1.7 to 2.3 percent less than
otherwise identical childless women (1.2 to 4.1 percent after a leave)—smaller than
the roughly 7 percent gap among human evaluators in Correll, Benard, and Paik (2007),
although the designs are not comparable. Across 28 occupations, the penalty shows no
robust association with occupational female share, wages, or task composition. Linear
probability models with controls reproduce the main tests (leave coefficients −.047 to
−.161); wild cluster bootstrap p-values change no conclusion; estimates on a repeated
anchor condition drifted by 0.8 to 2.4 points between phases, within the pre-specified
tolerance; and screen-position preferences are balanced by design.

## 5. Discussion

### 5.1 The framework revisited

Figure 9 returns to the framework with the findings in place. Of the three components
of the motherhood signal, the two that the ideal-worker account emphasizes—time out of
work and visible family responsibility—carry the penalty, for women and men alike. The
component the gender-statistical account emphasizes—being a woman—carries little, and
what it carries differs by vendor, as the alignment account would lead one to expect.
The penalty appears at the comparative margins where selection happens and is
invisible in single-applicant scores.

We therefore describe the screeners' behavior as two layers. The first is a caregiver
penalty, shared by all four models in sign, with two parts. The *interruption penalty*
behaves like an inference about availability (Phelps 1972; Kroft, Lange, and
Notowidigdo 2013; Weisshaar 2018): any eight-month gap is costly whatever it is called,
availability language in a job ad deepens it, and an instruction that names it reduces
it. The *family-signal penalty* behaves like a norm. It attaches to children and
parenting activity, persists on top of a gap already labeled as parental leave, is
only partly offset by evidence of commitment, and does not respond to instructions. In
these respects it resembles the normative component of the human motherhood penalty
(Benard and Correll 2010), except that it is applied to fathers too. The second layer
consists of gender-specific behaviors that appear mainly when gender is made salient
and differ in direction across vendors.

A plausible reading, which our design cannot test directly, is that alignment training
reshapes the behaviors it targets—overt differential treatment by gender—and leaves
untouched the correlated judgments it does not target. Two models' explanations are
suggestive: they declare family information irrelevant precisely in the decisions in
which the parent loses. Without unaligned versions of these models, this remains a
conjecture.

### 5.2 Gender-neutral in form, gendered in effect

The first layer is formally gender-neutral, but that does not make it neutral for
gender equality. Caregiving interruptions and visible family responsibilities are
carried disproportionately by women (Goldin 2014), so a rule that penalizes them
reproduces a gender gap through the distribution of signals rather than the treatment
of individuals—the structure that disparate-impact doctrine was designed to capture,
and the long-standing argument that the ideal-worker norm disadvantages women without
naming them (Acker 1990; Williams 2000). What is new here is the norm in its most
abstract form: applied by systems that can read gender, have been trained not to use
it, and penalize caregiving anyway.

The finding speaks to a broader question about how discrimination responds to its own
regulation. When a protected category is policed, decisions can shift toward
correlated signals that are not protected as such, as research on bans of
criminal-record questions has shown (Agan and Starr 2018). The present case differs—the
models are not substituting a proxy for a gender judgment they would otherwise
make—but the consequence is similar: scrutiny organized around the protected category
leaves the penalty on caregivers in place.

### 5.3 Implications for auditing

The framework also explains why standard audits would miss these patterns. Audits
must be *comparative*, because the penalty lives in choices and shortlists, not in
scores. They must *count non-answers*, because the largest pregnancy effect is a refusal
to price that carries a denial of interviews. They should *measure gender knowledge
implicitly*, because direct questions measure a model's willingness to state gender,
not its ability to read it. And they must *look beyond protected categories*: a
four-fifths comparison of women and men will miss a penalty that is gender-neutral in
form, so audits need to compare applicants with and without caregiving signals.
Because vendors differ widely—the same leave signal costs about twice as much choice
probability with Haiku as with DeepSeek—an audit of one model says little about
another, and the remedies phase cautions against relying on instructions: a generic
fairness prompt moved the penalty in different directions for different vendors, and
a targeted one removed only the component it named.

### 5.4 Limitations

The family signals are explicit, and real résumés carry weaker ones; the
parental-leave gap is the most realistic. The materials are US-oriented, in English,
text-only, and hold race constant, so the study is silent on how caregiver penalties
intersect with race or class. Pregnancy has no male counterpart. Salary and interview
outcomes are recommendations, not offers or callbacks. The models are four low-cost
versions at fixed dates, used without system prompts except in the remedies phase;
larger models and commercial products may behave differently, and versions change.
Pools and pairs are constructed, so the design identifies the effect of a signal, not
hiring rates. Group outcomes rest on scenario values for signal prevalence. The coding
of explanations relies on LLM coders without human validation. Effective sample sizes
are set by résumé pairs (40 or 16 per comparison), not by the number of calls.

## 6. Conclusion

Asked whether LLM résumé screeners penalize mothers, our answer is that the models we
studied penalize caregivers. Unbundling the motherhood signal shows that they penalize
time out of work and visible family responsibility, regardless of the applicant's
gender, and that they do so only when applicants are compared. On this the four
vendors agree. What differs among them is a thin gender layer and one vendor's
practice of withholding decisions about pregnant applicants. Because the caregiver
penalty is gender-neutral in form, it can pass fairness checks organized around gender
while reproducing the motherhood penalty in effect.

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

---
