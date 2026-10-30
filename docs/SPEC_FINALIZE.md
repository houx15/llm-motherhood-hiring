# SPEC_FINALIZE — final analyses before write-up

*Reviewer, 2026-10-30, HEAD fea0faf. No new model calls (all items use
existing logs). Part 1 is for opencode (analysis + code only; no edits to report.md
prose). Part 2 is the writing/organization pass, done by the researcher/reviewer
after Part 1's outputs exist. Part 3 is researcher-only.*

All outputs go to `docs/final/` unless stated. Every number written to JSON; no
hand-typed numbers. Cluster by unordered résumé pair (`pair_cluster()`) as elsewhere.

## Part 1 — analyses for opencode

### F1. Rationale coding (phase 4 Part A) — make it reportable
Context: primary coder = DeepSeek V4.1 Flash (temp 0) on all 8,000; reliability =
Qwen on 800 non-Qwen rationales. Issues to address:

a. **Self-coding check.** DeepSeek codes its own rationales. Recompute κ (DeepSeek vs
   Qwen) separately for DeepSeek-written vs other-model-written items; report per code
   with n. If κ differs by > .10 for any retained code, flag it.
b. **Retained codes.** Substantive analyses use only codes with κ ≥ .70 overall *and*
   in (a): gap, availability, family, disclosure_irrelevant, gap_reason_quality,
   protected_mention (subject to a). `qualifications` (κ .01, ≈1.0 everywhere) and
   `gender` (κ .20) are reported in the reliability table only.
c. **Shares with uncertainty.** For each model × contrast: share of losing-cued
   rationales invoking each retained code, with pair-clustered 95% CIs and n.
d. **Baseline comparison.** The share among losing cued candidates is selected on the
   outcome; give a comparator: the same code shares in rationales where the cued
   candidate *won* (does the winner's rationale also mention the gap/family?), and the
   `personal` placebo as the no-family baseline. Report differences (losing − won;
   contrast − personal) with CIs.
e. **Decomposition alignment test.** Pre-state and test: gap/availability codes
   higher for interruption contrasts (gap_travel, gap_parental_only, parent_gap) than
   for parent/parent_committed; family code higher for family contrasts than for
   gap_travel/personal. Per model, Holm across models.
f. **"Irrelevant but penalized."** For parent and parent_committed: share of losing
   rationales coded disclosure_irrelevant, with CI, by model; and the same share among
   rationales where the cued candidate won. Descriptive only.
g. **Gender.** Do code shares differ by candidate gender (female vs male cued)?
   Per model × retained code, difference with CI, Holm.
Outputs: `docs/final/coding_stats.json`, `docs/final/coding_tables.md`, one figure
(model × contrast × {gap, availability, family, disclosure_irrelevant}; dot + CI;
axis labels and one-line in-figure note on what a share means).

### F2. Human validation — DEFERRED (researcher, 2026-10-30)
Not run now. Leave `docs/phase4/human_coding.csv` as is. Reliability rests on the
DeepSeek–Qwen κ (F1a); the report states that rationale codes are LLM-coded and not
human-validated.

### F3. Study totals (replace stale "602,093 calls, $160.48")
From ledger + logs: calls and cost per phase (pilot/pretest, materials, main run,
phase 3, phase 4 experiment, phase 4 coding, repairs), valid rate per phase, and
grand totals. Output `docs/final/study_totals.json` + a markdown table.

### F4. Claims check (enforces "no hand-typed numbers")
`docs/report/claims.yaml`: one entry per number in the short abstract, extended
summary (Findings 1–5), and §§4.10–4.11 tables: id, section, rendered string,
source file + JSON key, rounding rule. `tests/test_claims.py` asserts each rendered
string appears in report.md and matches the source after formatting. Generate
`docs/report/CLAIMS.md` (claim → estimate → CI/test → source → figure). Report any
mismatches found; do not edit report.md to fix them — list them.

### F5. Figures
Regenerate figures so all have axis labels + one-line in-figure note (check
fig2–fig8, which predate that rule). Keep current filenames; renumbering happens in
Part 2.

### F6. One-command reproduction
`uv run audit reproduce`: rebuilds stats.json, tables.md, phase-3/4 stats, coding
stats, study totals, CLAIMS.md, all figures in fixed order; then
`git diff --stat docs/` and exit non-zero if any generated file changed.

## Part 2 — writing & organization (not opencode)

- report.md: add mechanism paragraph from F1 (exploratory, stated reasons ≠ causes,
  not human-validated; F2 deferred); update header (Draft 6), totals from F3, §3 to include
  SPEC_PHASE4 pre-specification and the phase-3 post-hoc ±5pp; cite or move figs 1–8.
- Reorder results along the two-layer argument: comparison-only → interruption +
  family bundle (+ mechanism) → gender-invariance / no fatherhood bonus → thin gender
  layer (explicit gender, abstention) → fairness instructions → disparate-impact
  scenario → secondary outcomes (salary, JD, occupation) → robustness. Move current
  §4.1 (manipulation check) into §2.4. Main figures: 1, 9–14; others to appendix.
- Appendices A–H as short sections (occupation design, perception checks,
  decomposition robustness, main-run tables, rationale coding, phase-4 tables,
  reproducibility & spend, deviations log incl. repair incident).
- README: phase table (question, spec, calls, cost, results doc) + reproduce command.
- Banner on historical docs (pilot, phase1–2, phase3 SHORT_REPORT and per-model
  reports, SPEC_E2_EXTENSION): superseded; numbers predate repair-exclusion fix.
- docs/DATA_RELEASE.md: archive contents, size, sha256 manifest, exclusions,
  provider terms on redistributing outputs.

## Part 3 — researcher

- (Deferred) human validation of rationale codes — if revived, build a blinded file first;
  the current human_coding.csv shows machine codes.
- Verify ◆ references (Frermann et al. 2023; Phelps 1972; Veldanda et al. 2023).
- Choose venue (affects figure count) and release platform.

---

## Round 9 review of da5eeec–b2b7741 (2026-10-30) — fix before Part 2

**R9-1 (MUST) Main-run stats regression in `report_stats.py`.** The new
`run_id.str.contains("phase3|phase4")` filter corrupted `docs/report/stats.json`:
- `e3_fe` is now **identical for all four models** (F .633 / M .653) — Table 3 shows
  the same numbers in every column. Old (fea0faf) values differed (Haiku .248/.231,
  DeepSeek .708/.704, Luna .776/.809, Qwen .752/.798).
- Haiku and Qwen E2 now use **more clusters than exist in O20** (Haiku 43, Qwen 56 vs
  40): rows from other runs leak in — almost certainly `repair2-*` runs that repaired
  phase-3 calls (run_id has no "phase3"; 40 + 16 O8 pairs = 56). Qwen's
  parent_committed mother–father gap jumps −.023 → −.085, leave-gap −.026 → +.024.
Fix: select main-run rows by the original call's plan/experiment (or call_id ∈ main
plans), never by run_id substring; apply the repair-saved exclusion via the
`from_repair` flag. Then show a diff of every stats.json leaf vs fea0faf; the only
allowed changes are repair-exclusion shifts (expected ≤ ~1pp, Qwen largest). Assert in
a test that per-model e3_fe values are not all equal and n_clusters ≤ 40 (E2, O20).

**R9-2 (MUST) Disparate impact inherits R9-1.** `docs/phase4/disparate_impact.md`,
`disparate_impact_stats.json` and fig14 now report one set of numbers for all models
(crossing 59% everywhere). Regenerate after R9-1. The claims checker's "mismatches"
`abs_share_max` (77% vs 37%), `di_haiku_cross` (31% vs 59%), `di_scenario_low`
are artifacts of this bug, not stale report text — re-run the checker after R9-1.

**R9-3 (MUST) Holm bug in `finalize_coding.py` (F1e).** `fam_p[...] = r["p"] or 1`
turns p = 0.0 into 1.0, so the strongest results (t = 16–25) get Holm p = 1.0 and the
weakest one (Claude availability, t = 4.2) is reported as the only survivor — the
commit message's "Haiku availability survives Holm" is inverted. Use
`1.0 if p is None else p`, and pass unrounded p-values (compute from t, don't round
to 4 dp before Holm). Re-generate tables; all alignment tests with |t| ≥ 4 should
survive.

**R9-4 (SHOULD) Share CIs below 0.** Several share CIs have negative lower bounds
(e.g. −0.03). Clip to [0,1] or use a cluster-bootstrap percentile CI; note in the
table that [0.00, 0.00] means no occurrences in the sample.

**R9-5 (SHOULD) Phase-3 stats regenerated.** round3/5/6, phase3_key_stats and
CROSS_MODEL changed in da5eeec. Provide a one-table diff (key, old, new) and confirm
every change is from the repair-saved exclusion (e.g. Qwen parenthood −.068 → −.073).
Then the checker's remaining phase-3 mismatches (`f2_*`, `abs_amplification` 31× →
38×) are genuine text updates for Part 2.

**R9-6 (process).** `audit reproduce` exists to catch unintended diffs; the run that
changed 27 generated files was committed without inspecting them. After R9-1–R9-5,
run `audit reproduce` from a clean tree and include its `--stat` output in the commit
message.

### Notes for Part 2 (no action for opencode)
- Self-coding: protected_mention κ .44 on DeepSeek-written items; family κ .67 on
  other-written items (below .70). Mechanism text must say family-code reliability is
  lower for non-DeepSeek rationales and avoid resting claims on protected_mention.
- F1f: "irrelevant" is also common when the parent *wins* (Claude .70, Luna .56), so
  for those two it is boilerplate; the losing-vs-won gap is large only for DeepSeek
  (.49 vs .16) and Qwen (.89 vs .38). Phrase accordingly.

## Round 10 check (2026-10-30) — R9 fixes verified
Verified in the working tree: main-run stats.json matches fea0faf exactly (E3 per
model restored; E2 n_clusters = 40 for all models); disparate impact back to
DeepSeek 73% / Haiku 31% / Luna 93% / Qwen 84%; Holm fixed (all alignment tests
survive); phase-3 old-vs-new table shows max |Δ| = .005 (repair exclusion only).
Remaining small items before committing:
1. Commit (nothing since b2b7741 is committed); include `audit reproduce` --stat.
2. Add the R9-1 guard test (per-model e3_fe not all equal; main-run E2
   n_clusters ≤ 40) — no test references e3_fe/n_clusters yet.
3. Display Holm p < .001 as "<.001", not "0.0"; clip share CI upper bound at 1.
4. `_main_run_call_ids()` reads data/plans/*.parquet, which is git-ignored: make
   `audit reproduce` regenerate plans first (deterministic) or fail loudly if missing.
