# SPEC — Phase 3: explicit gender, placebo decomposition, occupational diversity

> Addendum to `docs/SPEC.md`. Supersedes `docs/SPEC_E2_EXTENSION.md` (kept for history).
> Written 2026-10-16 after the rev. 3 report and review.
> Ground rules unchanged: budget-capped, every call logged, resumable, deterministic,
> all reported numbers generated from stats files (no hand-typed numbers).

## 0. Decisions

| Item | Decision |
| --- | --- |
| Explicit gender cue | **Add to the main experiments** (E1, E2, E3) as a 2 × 2 cue design (§2) |
| Placebo conditions | **Add** to E1 and E2 (§3) |
| Direct gender comparisons | **Add** woman-vs-man choices to E2 and gender-balanced pools to E3 (§4) |
| Occupational diversity | **Add 8 occupations** chosen with O\*NET task scores to break the care × female-share confound (§5) |
| Names | Expand to 6 per gender, rotated (§2.3) |
| Lawyer résumés | Replace the two unqualified lawyer résumés (§5.4) |
| Unaligned / base-model ladder | **Dropped.** The study is about the preferences of deployed models. Do not implement. |
| Photo experiment | **Later.** Design note only (§9); do not implement now. |

---

## 1. Why these changes

1. **Gender is only implicit.** All main-run results come from first names. In US practice this is
   realistic (résumés rarely state gender), but in many markets (China, Germany) résumés state
   gender, age, marital status, and include a photo. We also cannot currently separate "the name"
   from "knowing the gender".
2. **A small pro-female tilt exists but was never tested directly.** In E1, childless women
   receive +0.07 to +0.12 fit points (all four models, t ≈ 3–5). E2 compared only same-gender pairs.
3. **The parent cue is a compound treatment.** It adds a personal disclosure and a résumé line;
   the leave-gap cue adds an employment interruption. One DeepSeek rationale explicitly prefers
   the candidate without a "personal disclosure". Placebos separate these components.
4. **Occupations confound care with gender.** Across the 20 occupations, the O\*NET care score
   correlates 0.55 with female share; all physical occupations are male-dominated; there is no
   male-dominated care occupation and no female-dominated physical one.

---

## 2. Gender cue design (all phase-3 experiments)

### 2.1 Four cue levels

| Level | Code | Name shown | Gender field | Notes |
| --- | --- | --- | --- | --- |
| L0 | `name` | gendered first name + surname | none | identical to the main run |
| L1 | `name_field` | gendered first name + surname | "Gender: Female" / "Gender: Male" | |
| L2 | `initial_field` | first initial + surname (e.g. "J. Baker") | "Gender: Female" / "Gender: Male" | isolates the explicit field from the name |
| L3 | `blind` | first initial + surname | none | gender-blind baseline; no gender split |

- The gender field is one line in the résumé header, directly under the name, in every condition
  where it appears. Wording identical across genders.
- L3 has no gender: family conditions that reveal gender (`pregnant`) are excluded there.
- Initials: draw from letters that are not strongly gendered as initials (e.g. J., M., K., R., T., D.)
  and rotate them like names.

### 2.2 Manipulation check (before the main run; budgeted)

For each model, ask "What is the most likely gender of this applicant? Answer female, male, or
unknown." on 1 résumé per occupation × each name / initial × L0–L3 (~1,000 calls per model).
Report the share answering correctly for L0–L2 and the share answering "male" / "female" /
"unknown" for L3. A male default under L3 is itself a reportable result.

### 2.3 Names

- 6 per gender, White-coded and frequency-matched, from the Bertrand & Mullainathan (2004) list
  (validated in Gaddis 2017). Keep the current 3 and add 3:
  - female: Emily, Sarah, Anne, Allison, Laurie, Meredith
  - male: Greg, Matthew, Todd, Brad, Geoffrey, Neil
  - Researcher to confirm in `QUESTIONS.md`; remove the "pending approval" note from
    `config/names.yaml` once confirmed.
- Shared surnames as now. **Rotate** names by a balanced hash (one name per call; each name
  appears equally often within every cell), so adding names does not add calls.
- E2 name pairs: two different names of the same gender, drawn from the rotation.

---

## 3. Placebo conditions

| Code | Résumé change | Cover-note line | Placebo for |
| --- | --- | --- | --- |
| `personal` | Volunteer: "Volunteer Coordinator, Riverside Animal Shelter (2022–present)" | "Outside work, I enjoy distance running and recently completed my third marathon." | `parent` (disclosure + extra line, no family) |
| `gap_travel` | "Career break — extended travel (Jan 2024 – Sep 2024)", later dates shifted exactly as in `parent_gap` | neutral note | the employment gap |
| `gap_parental_only` | "Parental leave (Jan 2024 – Sep 2024)", dates shifted | neutral note (no PTA, no children line) | caregiving reason, without the rest of the parent bundle |

- Match character length of `personal` lines to `parent` lines within ±10%.
- Reuse `parent_gap` date arithmetic exactly for both gap conditions.
- Run the phrase validator: no family cues in `personal` / `gap_travel`.
- Wording must be approved in `QUESTIONS.md` ("APPROVED: phase3 wording") before any paid run.

---

## 4. Experiments

Résumés: 4 per occupation (E1/E2), 6 per occupation (E3), as in the main run.
"O20" = original occupations; "O8" = new occupations (§5).

### 4.1 E1-v3 — isolated scoring

- Family codes: `none`, `parent`, `parent_gap`, `personal`, `gap_travel`, `pregnant` (female only;
  not in L3). (`married` and `parent_committed` are not repeated.)
- Cells per résumé: gendered levels 2 × 5 + 1 = 11; L3: 5.
- Reps per cell per résumé: 6 (names rotated).

| Block | Levels | Cells | Calls per model |
| --- | --- | --- | --- |
| O20, new cue levels | L1, L2, L3 | 11 + 11 + 5 | 20 × 4 × 27 × 6 = 12,960 |
| O20, new placebo codes at L0 | L0 | 2 genders × 2 codes | 20 × 4 × 4 × 6 = 1,920 |
| O20, drift anchor (`none`, `parent`, both genders) | L0 | 4 | 20 × 4 × 4 × 2 = 640 |
| O8, all levels | L0–L3 | 11 + 11 + 11 + 5 | 8 × 4 × 38 × 6 = 7,296 |
| **Total** | | | **22,816** |

### 4.2 E2-v3 — pairwise choice

Same-gender contrasts (childless `none` vs treatment): `parent`, `parent_gap`, `parent_committed`,
`personal`, `gap_travel`, `gap_parental_only`.

Direct gender contrasts (different-gender pairs, same family status on both sides):
`gender_none` (childless woman vs childless man) and `gender_parent` (mother vs father).
"Role" = which résumé of the pair carries the female name. Outcome: P(woman chosen).
Direct gender contrasts run only at L0–L2.

Per cell per occupation: 2 pairs × 2 roles × 2 positions × 3 name pairs × 2 samples = 48 calls.

| Block | Cells | Calls per model |
| --- | --- | --- |
| O20, L0 (new contrasts only): 3 placebos × 2 genders + 2 direct | 8 | 7,680 |
| O20, L1 and L2: 6 contrasts × 2 genders + 2 direct, each | 28 | 26,880 |
| O20, L3: 6 contrasts (no gender) | 6 | 5,760 |
| O20, drift anchor: `parent`, L0, both genders, 1 sample | 2 | 960 |
| O8, all levels (14 + 14 + 14 + 6) | 48 | 18,432 |
| **Total** | | **59,712** |

Keep the existing E2 prompt templates, JSON schema, parser, and repair protocol (including the
Qwen out-of-range repair pass).

### 4.3 E3-v3 — ranking (redesigned pools)

Fix the main-run confounds (`_e3_pool`): **rotate the parent role over all 6 résumés** (6 draws, not 4)
and **rotate gender across résumés** with a Latin square, so no résumé has a fixed gender or role.

| Composition | Pool |
| --- | --- |
| a | 1 mother + 5 childless (3 women / 3 men overall) |
| b | 1 father + 5 childless (3 / 3) |
| c | 3 parents + 3 childless, gender-balanced within each group |
| e (new) | 6 childless, 3 women / 3 men — gender preference in ranking |

Composition d (all parents) is dropped. At L3 only composition a is run (token parent, no gender).
Per composition per occupation: 6 draws × 6 rotations × 1 sample = 36 calls.

| Block | Calls per model |
| --- | --- |
| O20, L0, L1, L2 × compositions a, b, c, e | 20 × 3 × 4 × 36 = 8,640 |
| O20, L3 × composition a | 20 × 36 = 720 |
| **Total** | **9,360** |

(O8 occupations are not included in E3, to save budget.)

### 4.4 Lawyer correction

Regenerate `lawyer_00` and `lawyer_01` as qualified attorneys (J.D., state bar admission, matching
experience length), run the validator and pretest, and rerun the main-run L0 lawyer cells for E1
(original 11 cells) and E2 (original 3 contrasts) so lawyer estimates use consistent materials.
About 1,500 calls per model.

### 4.5 E4

Not repeated in phase 3.

---

## 5. New occupations (O8)

### 5.1 Goal

Reduce the correlation between female share and (a) care/interpersonal work and (b) physical work,
and add highly paid female-dominated analytic work.

### 5.2 Procedure

1. Compute four O\*NET 31.0 work-activity scores (importance scale, z-scored against all O\*NET
   occupations) — the same definitions as in the review:
   - physical: Performing General Physical Activities; Handling and Moving Objects; Operating
     Vehicles, Mechanized Devices, or Equipment
   - care: Assisting and Caring for Others; Performing for or Working Directly with the Public
   - analytic: Analyzing Data or Information; Thinking Creatively; Processing Information
   - manage: Guiding, Directing, and Motivating Subordinates; Coordinating the Work and
     Activities of Others
   Fix the SOC matching for the 3 current occupations that did not match (warehouse supervisor,
   financial analyst, pharmacist — SOC code vintage differences).
2. Fill female share (BLS CPS Table 11) and median wage (BLS OEWS) for the candidates below.
   Verify every value from the files; do not use remembered figures.
3. Choose 8 occupations that minimize |corr(female share, care)| and |corr(female share, physical)|
   across the resulting 28, subject to the quotas.

| Quota | Candidates (verify SOC and female share) |
| --- | --- |
| ≥ 2 female-dominated, physical | Maids and housekeeping cleaners; Home health and personal care aides; Childcare workers |
| ≥ 2 male-dominated, care / interpersonal | Firefighters; Police and sheriff's patrol officers; EMTs and paramedics |
| ≥ 2 female-dominated, high-wage analytic | Veterinarians; Clinical and counseling psychologists |
| ≥ 1 male-dominated, skilled trade | Electricians |
| optional | Security guards; Janitors |

Write the final selection, with all scores, to `data/materials/occupations_phase3.csv` and the
before/after correlation matrix to `docs/report/occupation_design.md`.

### 5.3 Materials

4 base résumés per new occupation (E1/E2 only), same rules as the main run. **Licensed
occupations must show the license or credential** (e.g. EMT certification, state license for
psychologists and veterinarians, journeyman/master electrician). Pretest with merit check:
mean fit ≥ 5 for every base résumé before any paid run. One JD per occupation from O\*NET.

### 5.4 Lawyer fix

See §4.4.

---

## 6. Run order and gates

1. Materials: new occupations, résumés, lawyer fix, names, cue rendering, placebo wording,
   E3 pool redesign. Unit tests:
   - female vs male versions differ only in name (and the field line where present)
   - L2 vs L1 differ only in the name line
   - placebo vs `none` differ only in the specified lines
   - E3 pools: every résumé appears with each gender and each role equally often
2. Dry run: sample prompts for every new cell → researcher approves wording.
3. Manipulation check (§2.2), all four models.
4. Pilot: DeepSeek, 2 occupations (1 from O20, 1 from O8), all cells, 1 sample. Check parse
   rates, refusals and salary withholding by cue level (explicit gender may trigger more
   abstention), position bias.
5. DeepSeek full phase 3 → short report → researcher approval → other three models.

---

## 7. Budget

Actual per-call costs from the main run (ledger, 2026-10-16), applied to the phase-3 call counts:

| Model | E1-v3 (22,816) | E2-v3 (59,712) | E3-v3 (9,360) | Lawyer fix (~1,500) | Total |
| --- | --- | --- | --- | --- | --- |
| DeepSeek V4.1 Flash | $2.21 | $9.32 | $2.13 | $0.20 | $13.86 |
| Claude Haiku 5.5 | $5.50 | $25.08 | $7.10 | $0.50 | $38.18 |
| GPT-6 Luna | $3.13 | $9.26 | $2.14 | $0.20 | $14.73 |
| Qwen3.8 Flash | $2.49 | $10.87 | $2.77 | $0.25 | $16.38 |
| **Total** | | | | | **$83.15** |

- Plus manipulation check and pilot: about $2.
- With DeepSeek peak pricing (×2 on its share) and the 1.15 safety factor: about **$112**.
- Spent so far: $38.51 (experiments) plus repairs/materials. Projected total ≈ $155, under the
  $180 usable cap (cap $200 − reserve $20).
- If budget is tight, in this order: (1) run Haiku E2-v3 with 1 sample instead of 2 (saves ≈ $12);
  (2) drop O8 from E2 (saves ≈ $17 across models).

---

## 8. Analysis plan (additions to the rev. 3 analyses)

Inference: E1 clustered by résumé; E2 by résumé pair (40 pairs for O20, 16 for O8); E3 with résumé
and position fixed effects, clustered by occupation. Holm correction within each family of tests.
All tables generated programmatically into `docs/report/tables.md`.

1. **Gender preference by cue level.** P(woman chosen) in `gender_none` and E3 composition e; the
   E1 woman − man gap for childless applicants; each at L0, L1, L2. Compare L1 vs L0 (adding an
   explicit field) and L2 vs L1 (removing the name).
2. **Parent penalty by cue level.** Mother and father penalties at L0–L2 and the gender-free parent
   penalty at L3. Key test: if the L3 penalty equals the gendered penalties, the penalty is about
   caregiving and not gender.
3. **Placebo decomposition.**
   - parenthood net of disclosure = `parent` − `personal`
   - caregiving net of gap = `gap_parental_only` − `gap_travel`
   - bundle on top of a caregiving gap = `parent_gap` − `gap_parental_only`
   Report as a decomposition table per model and cue level.
4. **Mother vs father by outcome.** One table per model: choice, salary (withheld excluded),
   commitment, competence, likability, interview, withholding. (In the main run, mothers'
   extra penalty appears mainly in salary and perceived commitment, not in choice, for most models.)
5. **Occupations.** Appendix table of all 28 occupations: female share, wage, four O\*NET scores,
   parent penalty, mother − father gap, woman − man gap. Regress occupation-level effects on the
   standardized scores jointly (care and female share now separable). Exploratory.
6. **Abstention.** Salary withholding and refusal rates by cue level, family code, and model.
7. **Drift.** Compare drift-anchor cells with the main run; flag |Δ| > 0.03 in choice probability.

---

## 9. Later: photo experiment (design note only — do not implement)

- Add a headshot to the application, varying perceived gender while holding other face
  attributes constant.
- Faces: a validated database with norming data (e.g. Chicago Face Database: perceived age,
  attractiveness, race; check license terms) or generated matched pairs that differ only in
  perceived gender.
- Realistic mainly for markets where photo résumés are standard (China, Germany); pair with a
  Chinese-language version of the materials.
- Requires image-capable models; confirm each model's image support at the time.
- Main confounds to control: race, age, attractiveness, image quality.

---

## 10. Dropped

- Alignment-stage / base-model comparisons (OLMo ladder, base models): not part of this study.
  OpenRouter offered no routable base models as of 2026-10-16 in any case.
