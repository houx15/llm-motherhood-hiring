> **SUPERSEDED NOTICE (2026-10-16):** parts of this document were corrected after independent review — see `docs/report/report.md` (rev. 2). Key corrections: rev.2 of docs/report/report.md corrects: E2/E3 significance re-estimated with résumé-pair clustering and résumé fixed effects, and several E4/naïve figures updated.

# Phase 1 results — DeepSeek V4.1 Flash, full E1–E4, 20 occupations

Pooled runs 2026-10-15 (`e1_scoring`, `e2_paired`, `e3_ranking`, `e4_jd_context`) ·
**47,760/47,760 calls valid (99.91%) · 0 refusals · $5.76 actual spend** (vs $20.27
conservative estimate; $7.09 cumulative on the key). Full tables: `docs/phase1/report.md`.

**Model**: `deepseek/deepseek-v4.1-flash` served by the pinned DeepInfra endpoint
(fp8). Occupation moderators: BLS CPS 2025 female share, OEWS May 2025 median wage,
O*NET 31.0 time demands. Résumé FE + name FE everywhere; SEs clustered by résumé.

## 1. The core finding: surface fairness, deep bias (H8, gatekeeper side)

Same résumés, three tasks, one model:

| Task | Mother (parent cue) vs childless woman | Father vs childless man |
| --- | --- | --- |
| **E1** score alone | interview −1.1pp (93.1 vs 92.0%), salary −$1.3k (n.s.) | +1.7pp, −$1.2k (n.s.) |
| **E2** choose between two | **P(chosen) 0.356** (parent), **0.310** (leave gap) | 0.349 / 0.307 |
| **E3** token in pool of 6 | **top-1 0.105 vs 0.229; top-3 impact ratio 0.56** | 0.089 vs 0.200; ratio 0.53 |

When the model grades a résumé in isolation it looks fair; the moment a *comparison*
is forced, identical parents lose about two-thirds of the time. The magnitude doubles
from E1 to E2 and doubles again from E2 to E3 — the discrimination is relational,
not absolute, which is precisely the "invisible gatekeeper" pattern: no single score
looks discriminatory, yet the shortlist changes.

## 2. Cue types: the leave gap dominates; commitment signals half-repair it (H5, H6)

E2 paired differences (parent − childless, both genders pooled behavior is similar):

| contrast | P(parent chosen) | salary diff | commitment diff |
| --- | --- | --- | --- |
| parent (PTA + note) | 0.356 | −$1,854*** | −0.15*** |
| parent_committed (top performer) | 0.419 | −$892*** | **+0.17**** |
| parent_gap (8-mo leave) | **0.310** | **−$2,464****** | **−0.84****** |

- **H5 supported**: the *caregiving* signal (leave gap) is penalized far more than
  parenthood itself — and equally for fathers, replicating Frermann et al. (2023).
- **H6 (normative discrimination)**: adding objective high-commitment evidence
  (top-performer award, volunteered for extended-hours project) recovers about half
  the penalty (0.31→0.42) but nowhere near eliminates it, and it does not repair the
  leave gap at all. Consistent with Benard & Correll (2010): penalties persist when
  statistical uncertainty is removed.
- No fatherhood bonus anywhere (H2 rejected for this model): fathers are penalized
  at nearly the same rate as mothers in every comparative task.

## 3. The motherhood-specific penalty shows up in ratings and pay (H1)

Pooled E1 regressions (family × gender, résumé FE; terms at occupation-mean Z):

- **Mother-minus-father gap in commitment: −0.09 (p = 0.002)** — mothers are rated
  less committed than fathers by a tenth of the scale, holding résumés constant.
- **Leave-gap gender gap: commitment −0.12 (p = 0.0001), salary −$1,271 (p = 0.015)**
  — the leave gap costs mothers meaningfully more than fathers on both margins.
- Fatherhood salary effect −$1,157 (p = 0.08) — a *mild fatherhood penalty*, not a
  bonus. On direct salary the model treats parents similarly, then punishes mothers
  more when a leave is visible.
- The `married` relocation note depresses commitment for both genders (~−0.74, a
  relocation signal, not gendered) — worth remembering when reading the married cell.

## 4. Pool composition is a first-class driver (E3)

- **Token parents are crushed**: one mother among five childless candidates → top-3
  rate 0.341 vs 0.612 for identical childless women (**four-fifths impact ratio
  0.56** — an adverse-impact violation by NYC Local Law 144 standards); token
  fathers 0.53.
- **Mixed pools (3 parents + 3 childless)**: parents at parity or slightly favored —
  the penalty is about *being the odd one out*, not parenthood per se.
- **All-parent pools invert**: mothers' top-3 rate 0.560 vs fathers' 0.440 (top-1
  0.231 vs 0.103). When everyone is a parent, the model favors mothers — consistent
  with An et al.'s pro-female scoring shifting by context, and a caution that
  "which candidate set" can flip audit conclusions entirely.
- Screen-position bias remains huge (top-1 by label C1→C6: 0.40→0.06); the Latin
  square absorbs it, but any production use of LLM ranking with fixed order would
  inherit it.

## 5. JD wording is causal for the penalty (H7, E4 — the experiment O*NET can't give)

Interview-rate penalties (parent_gap − none, percentage points):

| JD variant | mothers | fathers |
| --- | --- | --- |
| base | −0.6pp | +0.2pp |
| eeo boilerplate | +0.8pp | +0.2pp |
| family-friendly | −1.4pp | −1.2pp |
| **greedy** | **−3.3pp** | −1.7pp |
| greedy + family-friendly | **−5.8pp** | −4.4pp |

- **Greedy wording ("after hours, weekends, 40% travel") triples the parent-gap
  penalty, and doubles it specifically for mothers** (−3.3pp vs −1.7pp). Commitment
  ratings for leave-gap parents drop ~0.5 points more than for childless candidates
  under the same sentence.
- A one-line family-friendly policy added to the greedy JD does **not** repair the
  gap (mothers −5.8pp in greedy_ff vs −3.3pp greedy); salary effects track the same
  way (mothers' parent_gap salary −$1,939 under greedy).
- EEO boilerplate does nothing (H7's null confirmed).

## 6. Occupation-level moderators: the gradient is in the JD signal, not the occupation (H3/H4)

Triple interactions (mother-minus-father parent gap × standardized Z):

- **time_demands × gap on salary: +$607 (p = 0.30)** — the O*NET time-demand
  gradient across occupations does NOT amplify the motherhood penalty in E1.
- But E4 makes greediness *experimental*: the same occupation penalizes leave-gap
  mothers −0.6pp under its base JD and −3.3pp with one greedy sentence. **The
  greedy-job effect is real but carried by the job description's signal, not by the
  occupation's average measured time demands.** Goldin's mechanism appears to
  operate through what the employer *says*.
- **female_share × leave-gap gender gap on competence: −0.057 (p = 0.017)** — the
  mother-specific competence penalty is *larger in female-dominated occupations*,
  opposite to the gender-typing prediction (H4). One interpretation: in
  female-typed jobs the leave gap is more schema-violating (the "ideal worker" is
  normatively stronger in jobs where mothers are the modal worker). Flagged for the
  paper as an unexpected, exploratory finding.
- median_wage × leave-gap gender gap on salary: −$1,006 (p = 0.097), marginal.

## 7. Diagnostics (spec §13 Phase E acceptance)

- Parse success **99.91%** ≥ 98% ✓ (E1/E3/E4 100%, E2 99.72%; repairs recovered most).
- Spend $5.76 ≤ estimate+20% ($20.27 est.) ✓ — actual tokens ran ~40% below the
  spec's assumptions (E1 812/110, E2 1,340/200, E3 3,206/83 in/out per call).
- Refusals: **zero** across all conditions including `pregnant`.
- Rationale keyword leakage: family words in ~61% of `parent_gap` and 97% of
  `pregnant` rationales, but only ~2.5% of `parent` — the silent PTA cue moves
  outcomes without surfacing in reasons (implicit processing).
- Position biases: E2 chosen=A 0.83; E3 top-1 C1 0.40 → C6 0.06 — counterbalancing
  verified effective (both arms symmetric).

## 8. Bottom line for the paper

On this widely-used open-weight model, the motherhood penalty is **real but
conditional**: near-zero in isolated scoring, severe in pairwise and ranking tasks,
amplified by greedy job-ad language, and larger for mothers than fathers mainly
through the parental-leave channel and commitment ratings. A fatherhood bonus is
absent. One sentence of EEO boilerplate does nothing; the findings give regulators
a concrete lever (job-ad wording) and a concrete risk (LLM shortlists violate the
four-fifths rule for token parents).

Remaining budget: **$192.91** — enough for Phase F (Claude Haiku 5.5 ≈ $3.4, Qwen3.8
Flash ≈ $4.5, GPT-5 Mini ≈ $12.3 at this provider's token rates) if approved.
