# Pilot interpretation — DeepSeek V4.1 Flash, 2 occupations (Phase 0)

Run: `20261014-223507-pilot-deepseek_v41_flash` · 4,416 calls · $0.57 actual ·
99.9% parse success · 0 refusals · full tables in `report.md`.

Occupations: software_engineer (male-dominated, high wage) and administrative_assistant
(female-dominated, low wage). These are **pilot** reads on 2 of 20 occupations — treat
effect sizes as provisional; the design's moderator tests (H3/H4) need the full grid.

## Headline: surface fairness, deep bias — already visible in the pilot

**E1 (scoring one résumé alone) shows almost no penalty.** Interview rates sit at
95–100% in every cell; fit scores differ by ≤0.2 points; the motherhood salary effect
(−$3.7k on ~$92k, p≈0.10) is the only hint of a gap. On the direct, individual
audit the model looks unbiased — exactly the "surface fairness" the proposal predicts.

**E2 (choose between two identical candidates) shows a clear parenthood penalty.**
P(parent chosen) < 0.5 in *every* contrast, for *both* genders:

| contrast | women | men |
| --- | --- | --- |
| parent (PTA cue + "married with two children") | 0.42 | 0.36 |
| parent_committed (top performer) | 0.44 | 0.42 |
| parent_gap (8-month parental leave) | **0.33** | **0.32** |

Within-pair salary and rating differences are negative almost everywhere. The leave
gap is the killer: paired commitment difference −0.84 (women) / −0.98 (men), competence
−0.26 / −0.40, salary −$2.5k / −$3.3k — all p < 0.05. This matches Frermann et al.
(2023): the *cue* that matters is the leave gap, not parenthood per se, and it hits
fathers too.

**Notably: no fatherhood bonus, and the penalty is gender-symmetric in the pilot.**
The classic human result (mothers penalized, fathers not) does *not* (yet) show up as a
gendered pattern; if anything men's parent-choice rates are lower than women's. The
mother-specific prediction (H1 vs H2) is undecided at this sample size — this is one of
the key questions for Phase 1.

**E3 (rank a pool of six) shows the largest effects.** A lone mother among childless
candidates: top-1 rate 0.076 vs 0.260 for otherwise-identical childless women
(top-3: 0.35 vs 0.60; four-fifths impact ratio **0.59** — far below the 0.80
adverse-impact threshold). A lone father: 0.076 vs 0.215 (ratio 0.57). In mixed pools
(composition c) parents rank at parity, and in all-parent pools (d) mothers actually
lead fathers (top-1 0.285 vs 0.049). So the penalty is strongest for the *token* parent
— a pool-composition effect that single-résumé audits cannot see (a design contribution
of this study).

**E4 (JD wording moves the penalty — H7 supported in the pilot).** For the
software-engineer JD, interview rates by variant for `parent_gap`:

| JD variant | women | men |
| --- | --- | --- |
| base | 91.7% | 100% |
| eeo (boilerplate) | 94.4% | 91.7% |
| family_friendly | 91.7% | 94.4% |
| greedy | **80.6%** | **66.7%** |
| greedy_ff | **72.2%** | 80.6% |

Greedy wording ("after hours, weekends, 40% travel") cuts parents' interview rates and
salaries (~−$16k for mothers, −$20k for fathers vs childless under `greedy`).
A one-sentence family-friendly policy added to the *same* greedy JD does not repair it
(72–81%). EEO boilerplate does nothing. Consistent with Correll's organization-context
hypothesis and Goldin's greedy-jobs logic — and the manipulation is experimental here,
unlike observational occupation contrasts.

## Diagnostics the researcher should weigh before Phase 1

1. **Position bias is large and must stay counterbalanced.** E2: P(chosen=A)=0.83.
   E3: top-1 rate falls monotonically C1=0.34 → C6=0.06. All comparisons are
   position-counterbalanced by design, but any change to presentation order between
   arms would be fatal; the Latin-square rotation is doing real work.
2. **Ceiling effects.** Interview=yes for 98% of E1 responses; fit 9–10 common in
   several occupations (pretest). E1's outcome scale is compressed — one reason E1
   looks "fair". Salary and the E2/E3 designs carry the discriminative variance.
   Consider reporting interview-rate effects only where ceiling is not binding (E4
   greedy cells) and leaning on salary/ratings/ranking outcomes.
3. **Rationales leak the manipulation differently by cue.** Family words appear in
   97.5% of `pregnant` rationales, 61% of `parent_gap`, but only ~2.5% of `parent`
   (E1). Pregnancy disclosure is overtly discussed; the PTA cue acts silently — the
   silent cues are the ones that still move E2/E3 outcomes, which is itself evidence
   of implicit rather than explicit reasoning.
4. **Parse robustness.** 99.9% valid JSON; residual failures are 1–7 scales answered
   with 8, "strong", or prose. One automatic repair recovers most; refusals: zero
   (including `pregnant`), so refusals-as-outcome will have no variance on this model.
5. **`married` dip.** The relocation-with-spouse note costs ~−0.7 commitment points
   for both genders (p<0.001) — a relocation signal, not a gendered one, but worth
   remembering when interpreting the `married` cell.
6. **Cost model.** Actual spend $0.57 vs $2.63 conservative estimate; measured tokens
   (E1 812/110, E3 3206/83 in/out) put **full Phase 1 (E1–E4, 20 occupations) at
   ≈ $14–16** at current DeepInfra pricing — comfortably inside the $35 phase cap and
   the $200 total cap (≈$1.4 spent so far).

## Go/no-go items for Phase 1 (researcher)

- Names approval (QUESTIONS.md §1) and the DeepInfra-endpoint decision (§2b).
- Whether to keep the spec's exact E1 interview question given the 98% ceiling.
- Confirm Phase 1 launch: **"APPROVED: phase E"** in QUESTIONS.md §7.
