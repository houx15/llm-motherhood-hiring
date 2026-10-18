# Phase 3 — DeepSeek short report (§6.5 gate)

Full tables: `docs/phase3/report_deepseek.md` (regenerate: `uv run audit phase3-report
--model deepseek_v41_flash`). Manipulation check: `docs/phase3/manipulation_check.md`.
Run: 91,844/91,888 valid (99.95% after one repair pass, 158 recovered), 0 refusals,
$24.34. Ledger total $66.85 of $180 usable.

## Headline findings (DeepSeek)

1. **The parent penalty is about caregiving, not gender — the phase-3 key test.**
   P(parent chosen) is essentially identical when gender is explicit or absent:
   parent cue .353 (L0) / .357 (L1) / .364 (L2) / **.354 (L3 blind)**; leave-gap
   .241–.297 gendered vs **.295 blind**. Whatever drives the penalty survives
   complete removal of gender information.
2. **Placebo decomposition (E2, spec §8.3, L0 mothers):**
   - personal disclosure alone costs almost nothing (`personal` .458 vs .5);
     **parenthood net of disclosure = −.107**.
   - **the employment gap, not its caregiving label, does the damage**:
     `gap_travel` .385 vs `gap_parental_only` .402 → caregiving label ≈ **+.017**
     (n.s.); the 8-month interruption itself costs ~−.11.
   - the family bundle on top of a parental gap costs another **−.156**
     (PTA/children line over and above "Parental leave").
   Same pattern at L1/L2/L3 — robust to cue level.
3. **No explicit-gender amplification.** Direct woman-vs-man choices barely move
   with cue level (P(woman) .515 L0 → .540 L1 → .538 L2; childless salary +$285
   → −$191 → +$425). The small pro-female tilt from the main run is unchanged by
   making gender explicit — and does not reverse.
4. **Mother-father differences stay ≈ 0 on choice** (all |M−F| ≤ .018), with the
   familiar pattern of slightly larger mother penalties in likability/salary only.
5. **Abstention: none.** Salary withholding ≤ 1.3% in every cue-level × family
   cell; explicit gender does not trigger abstention in DeepSeek.
6. **Occupation gradients (§8.5, joint regression, n=28, care ⊥ female share):**
   mothers' leave-gap penalty is *smaller* in female-dominated occupations
   (z_female_share +.057, p=.025); care/physical/analytic/manage themselves are
   all n.s. — the moderation runs through gender composition, not task content.
7. **Drift (§8.7):** phase-3 anchors run +2.4 to +3.5pp interviews above the main
   run (one cell crosses the 0.03 flag). Mild upward drift, likely prompt-version
   context; does not affect within-run phase-3 comparisons.
8. **Lawyer fix (§4.4):** with qualified attorneys, E2 penalties become measurable
   (P(parent) .21 mothers / .08 fathers vs near-arbitrary .38/.43 with the old
   failing résumés). E1 fit 3.3 → 9.2.

## Budget

Spent $66.85; remaining $113.15 (cap $180 usable). Remaining phase-3 runs:
Haiku $27 + Luna $27 + Qwen $31 (est., incl. safety) ≈ $85 → projected total
≈ $152, inside budget with ~$28 headroom. (Endpoint throughput, not budget, is
the schedule risk — DeepSeek needed ~29h at ~1 call/s.)

## Gate

Per SPEC_PHASE3 §6.5: researcher approval requested to run Claude Haiku 5.5,
GPT-6 Luna, and Qwen 3.8 Flash through the same phase-3 plan (manip checks for
all four models already done). Answer in QUESTIONS.md §11.5.
