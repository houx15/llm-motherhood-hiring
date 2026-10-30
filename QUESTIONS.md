# QUESTIONS.md — open questions & decisions for the researcher

Ground rule (spec §0.7): ambiguities land here instead of being invented silently.
The agent updates this file as decisions are made; researcher replies/approvals are
recorded verbatim below each item.

---

## 1. Names (approval needed before Phase 1, spec §4.4)

Proposed final list (in `config/names.yaml`), following Bertrand & Mullainathan (2004)
/ Gaddis (2017) validated, strongly gendered, White-coded, high-frequency names, race
held constant:

- Female: **Emily, Sarah, Anne** (paired surnames: Baker, Walsh, Murphy)
- Male:   **Greg, Matthew, Todd** (same surnames, index-aligned)
- Surnames: **Baker, Walsh, Murphy**

Pilot (Phase 0) runs with these; **APPROVED?** (researcher: reply below)

> RESEARCHER REPLY:

---

## 2. Data vintages & access workarounds (2026-10-14)

`bls.gov` is Akamai-blocked from this network (403 even with browser headers). The
pipeline therefore uses **Wayback Machine copies of the same official BLS files**:

- CPS Table 11 (2025 annual averages; snapshot of cpsaat11.htm, last modified 2026-02-20)
- OEWS national file **May 2025** (oesm25nat.zip)

O*NET is the official **31.0 Excel database** (August 2026 release) from onetcenter.org.

Notable coding decisions:

- **Pharmacist** is SOC 29-1251 in the 2022 SOC but 29-1051 in the OEWS-2025/O*NET-31.0
  vintages; `config/occupations.yaml` carries `soc_aliases: ["29-1051"]`.
- **Financial analysts (13-2051)** and **warehouse supervisors (53-1047)** have no exact
  O*NET Work Context row; `time_demands` uses the mean of the same 6-digit SOC family
  (13-205x, 53-104x).
- **Physician** female share uses the CPS "Other physicians" row (0.417) — CPS 2025
  splits physicians into specialty rows with no family-medicine line.
- O*NET 31.0 has **no "Spend Time Traveling" Work Context item**; per spec §4.1
  ("if available") the `time_demands` composite uses the other three items
  (Duration of Typical Work Week, Work Schedules, Time Pressure).
- **Surprise**: O*NET rates software engineers *low* on time demands (standard 40-h
  week; z = −0.76), so the spec's "male-dominated high-time-demand e.g. software
  engineer" assumption doesn't hold in O*NET terms. The 4 highest time-demand
  occupations are heavy_truck_driver, construction_laborer, warehouse_supervisor,
  marketing_manager; the 4 lowest are preschool_teacher, receptionist,
  software_engineer, medical_assistant.

---

## 2b. OpenRouter routing: first-party DeepSeek blocked by account guardrails (2026-10-14)

Requests pinned to `provider: {order: ["DeepSeek"], allow_fallbacks: false}` fail with
404: *"Filter by Guardrails removed deepseek (Paid model training violation (account
settings))"* — the key's account excludes the first-party endpoint. The same model slug
routes fine to third-party endpoints. **Decision:** pin the single endpoint **DeepInfra**
(fp8, $0.14 in / $0.42 out per Mtok) with `allow_fallbacks: false` for cross-condition
consistency; `provider_served` is logged on every call and any drift is flagged in
analysis. Actual per-call cost comes from OpenRouter `usage.cost`.

Caveat: fp8 third-party serving may differ from first-party DeepSeek behavior; acceptable
because the audit compares conditions *within* one fixed endpoint. If the researcher
prefers first-party serving, the account guardrail setting must be changed (or a different
key provided) — flag this before Phase 1.

---

## 3. Pilot scope decisions (2026-10-14)

- **Pilot E4**: per spec §5 ("if both are in_e4; else skip"), only `software_engineer`
  is `in_e4` among the two pilot occupations → pilot E4 runs for software_engineer
  only (1,800 calls at samples=5).
- **Pilot E4 samples trimmed to 3** in `config/experiments/pilot.yaml` to stay under
  the $5 pilot phase cap under conservative (peak) pricing. E1–E3 keep samples=5.
- **Pretest models**: spec §4.3 says 2 cheap models; per the "DeepSeek-only at this
  stage" instruction, the pretest runs DeepSeek V4.1 Flash only (5 samples), since
  Claude Haiku slug would need verification. To revisit if desired.

---

## 4. Résumé sourcing plan (2026-10-14)

Kaggle `snehaanbhawal/resume-dataset` categories map cleanly to only some occupations.
Plan (documented, validator-enforced):

- For each occupation: up to 2 base résumés **derived from Kaggle source text** —
  LLM-assisted conversion to the structured schema with strict anonymization and
  normalization (8–12 yrs, no gaps, no cues), then frozen.
- Remaining base résumés + 2 E3 "extra" résumés per occupation: **synthetic**,
  generated once by DeepSeek V4.1 Flash grounded in O*NET tasks/skills for the SOC,
  then frozen (generation prompt + output stored in `data/materials/`).
- All outputs pass the PII/family-cue/gendered-word validator; build fails on any hit.

Kaggle category mapping (used for source selection):

| Occupation | Kaggle categories |
| --- | --- |
| software_engineer | INFORMATION-TECHNOLOGY (developer keywords) |
| financial_analyst | FINANCE (analyst keywords) |
| mechanical_engineer | ENGINEERING (mechanical) |
| lawyer | ADVOCATE (law/court/attorney keywords) |
| marketing_manager | BUSINESS-DEVELOPMENT, PUBLIC-RELATIONS, DIGITAL-MEDIA (marketing) |
| retail_store_manager | SALES, BUSINESS-DEVELOPMENT (retail/store manager) |
| restaurant_manager | CHEF (restaurant/food-service manager) |
| customer_service_representative | BPO, ADVOCATE, HR (customer-service text) |
| registered_nurse | HEALTHCARE (RN/nurse) |
| hr_manager | HR (manager/senior) |
| accountant | ACCOUNTANT |
| administrative_assistant | HR, various (administrative assistant keywords) |
| preschool_teacher | TEACHER (preschool/early-childhood/elementary) |
| medical_assistant | HEALTHCARE (medical assistant) |
| others (5) | synthetic only |

---

## 5. E3 pool construction ("reuse with different names" option, spec §5 E3)

Pool = 6 unique résumés per occupation (4 base + 2 synthetic extras). The spec's
"4 résumé draws" from a fixed 6-pool is implemented as 4 draws that (a) rotate which
base résumé plays the token parent in compositions (a)/(b) (draws 0–3 → résumés 0–3)
and (b) rotate name assignment across draws. Documented choice per spec's own
"or reuse with different names" allowance.

---

## 6. Prompt paraphrases

The 3 paraphrases per template are hand-written in recruiter/task style. The proposal's
plan to derive them from WildChat/LMSYS logs is deferred — flagged for the researcher:
OK for pilot, or supply logs for Phase 1?

---

## 7. Phase gates (spec §13)

- Phase D (pilot) complete → **STOP for researcher review.**
- Phase E (DeepSeek full E1–E4) requires the researcher to write
  **"APPROVED: phase E"** below.
- Phase F (other models) requires **"APPROVED: phase F"** below.

---

## 8. Pilot (Phase 0) result summary — 2026-10-14

Run `20261014-223507-pilot-deepseek_v41_flash`: 4,416 calls, $0.57, parse 99.9%,
0 refusals. Read: `docs/pilot/interpretation.md` (+ report.md, figures).

- E1 shows near-zero direct scoring penalties (ceiling: 98% interview=yes).
- E2 shows parenthood penalties for BOTH genders, strongest for parent_gap
  (P(parent chosen) 0.33 women / 0.32 men); no fatherhood bonus visible.
- E3 token-parent penalty: mothers' top-3 impact ratio 0.59 (four-fifths violation),
  fathers' 0.57; parity in all-parent pools.
- E4: greedy JD wording cuts parent interview rates (mothers 80.6%, fathers 66.7%);
  family-friendly sentence does not repair; EEO boilerplate does nothing (H7 pattern).
- Large position biases (E2 chosen=A 0.83; E3 top-1 C1 0.34 → C6 0.06) —
  counterbalancing is essential and verified.
- Phase 1 estimate from measured tokens: ~$14–16 (E1–E4, 20 occupations) at
  DeepInfra prices, vs $35 phase cap; total spent to date $1.4.

**Per spec §13 Phase D: STOPPED here pending researcher review.**

---

## 9. Phase 1 (E) completed — 2026-10-15

Runs `20261015-012900` (E1), `20261015-023251` (E2), `20261015-040328` (E3),
`20261015-042916` (E4). **47,760/47,760 valid (99.91%), 0 refusals, $5.76.**
Acceptance criteria met (parse ≥ 98% ✓, spend ≤ estimate+20% ✓).
Read `docs/phase1/interpretation.md`. Highlights: relational discrimination
(E1 ≈ 0, E2 P(parent)=0.31–0.42, E3 token-parent impact ratio 0.53–0.56);
no fatherhood bonus; leave-gap cue dominates; greedy JD wording triples the
parent-gap penalty and doubles it for mothers; EEO boilerplate null; occupation
time-demand gradient null (H3 fails observationally but E4 supports the mechanism
experimentally); female_share *amplifies* the mother competence gap (opposite H4,
exploratory). Budget remaining $192.91.

> RESEARCHER REPLY (phase E): **APPROVED — via conversation, 2026-10-15: "1. yes. run"** (executed same day; see §9)

> RESEARCHER REPLY (phase F): **APPROVED — via conversation, 2026-10-15: "use claude haiku 5.5, gpt-6 luna, qwen 3.8 flash"**
>
> Note: "gpt-6 luna" resolved to the pinned dated slug `openai/gpt-6-luna` (never
> the `gpt-luna-latest` alias, spec §0.3). All three verified live on OpenRouter
> (first-party endpoints Anthropic/OpenAI/Alibaba, reasoning off, JSON mode OK).

## 10b. Phase F completed — 2026-10-16

All four models done (191,087 calls total, $40.94 cumulative). Cross-model table:
`runs/pooled/model_comparison.csv`; read `docs/phase2/interpretation.md`.
Robust across all models: parenthood penalty in every comparative cell (no
fatherhood bonus anywhere), leave-gap cue always worst, mother salary penalty
band −$1.3k–$1.9k, four-fifths violations for token parents in all models.
Outliers: Haiku (2× penalty, E3 impact ratio 0.14, −$18.8k pregnancy salary cut,
only refuser, opposite position bias); Luna (committed parents penalized MORE
than plain parents — normative-discrimination signature; most position-neutral);
Qwen (scale-overflow toward childless candidates). Phase F spend ~$33.85 within
the $140 cap; weekly spend 20.5% of $200.

---

## 10. Qwen3.8 Flash E2 scale-overflow — decision (2026-10-15)

Qwen emits **out-of-range ratings (mostly 8, sometimes 9) on 1–7 scales in ~23% of
E2 calls**, condition-correlated: parent_gap ~32% > parent ~26% > committed ~21%,
and the overflow lands on the **childless candidate 3:1** (position-counterbalanced).
E1 is unaffected (0.65% invalid). Reading: differential enthusiasm that breaks the
scale precisely when a childless candidate is compared against a leave-gap parent —
listwise deletion would bias Qwen's estimated parenthood penalty toward zero.

Decisions:
1. Primary analysis keeps strict validity (spec §9: clamp nothing).
2. A **targeted second repair pass** (`audit repair`) re-asks invalid non-refusal
   calls with an explicit field-level correction; repairs are logged with
   `repair_of` links and counted in the ledger. (Test batch: 25/25 repaired.)
   This exceeds spec §9's "one automatic repair attempt" — documented deviation.
3. A **winsorized robustness re-parse** (8→7, 9→7 on ratings only) will be reported
   alongside, to show both bounds (strict deletion vs recovered data).
4. Claude Haiku 5.5 shows ~1% condition-correlated soft refusals (valid JSON with
   all-zero scores + "protected characteristic" rationale), concentrated in
   family-cue cells; analyzed as refusal-rate-by-condition per spec §10.

---

## 11. Phase 3 (SPEC_PHASE3.md) — decisions & approval gate (2026-10-16)

### 11.1 PENDING APPROVAL — wording gate before any paid phase-3 run

> **APPROVED: phase3 wording — researcher, 2026-10-16** (chat approval during the
> phase-3 build session; scope: names, cue levels, placebo wording incl. the Pet
> Shelter length fix, E2 direct-contrast naming, E3-v3 pools, O8 selection incl.
> the health-services-manager substitution. Run scope approved through the
> DeepSeek full run; the other three models wait for the short-report gate §6.5.)

Per SPEC_PHASE3 §3/§6.2, the following need "APPROVED: phase3 wording" before the
manipulation check / pilot / materials generation. Sample prompts for every new
cell type: `docs/phase3/samples.md` (`uv run audit phase3-samples`).

1. **Names (6 per gender).** Keeping the main-run three and adding, per §2.3:
   female + Allison, Laurie, Meredith; male + Brad, Geoffrey, Neil. Surnames
   unchanged (Baker, Walsh, Murphy), rotated by index mod 3 so each name appears
   equally often within every cell (no new calls).
2. **Cue levels.** L1/L2 gender field is one header line directly under the name:
   `Gender: Female` / `Gender: Male`, identical wording across genders. L2/L3
   initials rotate over J., M., K., R., T., D. L3 renders `J. Baker` with no
   gender info anywhere.
3. **Placebo wording** (config/family_cues.yaml):
   - `personal` résumé line: "Volunteer Coordinator, Riverside Pet Shelter
     (2022-present)" — spec's example said "Riverside Animal Shelter" but that
     line is 12.7% longer than the PTA line; the spec also requires ±10% length
     match, so "Pet Shelter" (59 vs 55 chars, +7%) is used instead.
   - `personal` cover note: spec's exact sentence ("Outside work, I enjoy
     distance running and recently completed my third marathon."). NOTE: the
     parent cover note ("I am married with two children.") is much shorter;
     note length is confounded with the placebo by design (spec-fixed wording).
   - `gap_travel` leave label: "Career break — extended travel" (Jan 2024 –
     Sep 2024, identical date arithmetic to `parent_gap`).
   - `gap_parental_only`: "Parental leave" label + neutral cover note, no PTA
     line, no children line.
4. **E2 direct gender contrasts.** Pairs are always two different full names
   with different surnames (e.g., Emily Baker vs Matthew Walsh); role = which
   résumé of the pair is the woman; position = screen slot of the woman.
5. **E3-v3 pools.** Composition d dropped; a/b/c redesigned + new e. Margin-
   balanced so every résumé is each gender exactly 18/36 pools and parent role
   6/36 (a/b) or 18/36 (c: 12 mother + 6 father). Unit-tested
   (tests/test_phase3.py::test_e3_pool_balance).

### 11.2 Documented deviations (spec §5.2 fidelity rule: verify, never remember)

1. **Clinical and counseling psychologists (CPS share suppressed).** CPS Table
   11 (2025) reports "-" for the 19k-employed row, so the female share cannot
   be verified from the spec's source. **Substitute for the female_analytic
   quota: Medical and Health Services Managers** (75.3% women, $123,860 median,
   analytic z +0.97 — verifiable). Will switch back if a verified share is
   found before materials freeze.
2. **O*NET SOC vintage fixes** (13-2051/53-1047/29-1251 absent in O*NET 31.0):
   financial_analyst → 13-2099.01 (Financial Quantitative Analysts);
   warehouse_supervisor → mean(53-1042, 53-1043); pharmacist → 29-1051 (alias
   already in registry). All verified against Work Activities.xlsx titles.
3. **EMT/paramedic female share** = count-weighted combination of the two CPS
   rows (35.1%): 29-2040 for wages, 29-2043 for O*NET scores.
4. **Physical-confound limitation.** Every quota-feasible O8 deepens
   |corr(female share, physical)| (best ≈ −0.32 vs −0.26 at baseline) because
   the male-dominated care/trade occupations are all above-average physical.
   The design still achieves separability (O28 contains female-physical and
   male-care occupations; O20 had none). Full frontier:
   docs/report/occupation_design.md.
5. **Lawyer fix call count** is 474/model (E1 11 cells × 3 names × 5 samples ×
   2 résumés + E2 3 contrasts × main-run geometry), not the spec's rough
   "~1,500" — cheaper and matches the main-run replication exactly.
6. **Lawyer résumé regeneration replaces lawyer_00/01** in
   data/materials/base_resumes/lawyer.json (02-05 kept). Phase-2 logs still
   reference the old drafts; the lawyer_fix rerun provides the L0 baseline on
   the new materials. E3 lawyer cells use the new drafts for phase-3 pools.

### 11.3 Plan verification (deterministic, committed)

- phase3_main: e1 22,816 / e2 59,712 / e3 9,360 per model — matches spec §4
  tables exactly. Estimates (ledger-calibrated tokens ×1.15): DeepSeek $32,
  Haiku $27, Luna $27, Qwen $31 ≈ $117 total + manip ~$1.5 + pilot ~$1 +
  lawyer ~$2. Spent $37.48; projected total ≈ $160 < $180 usable.
- phase3_manip: 28 occs × 42 variants = 1,176/model.
- Run order after approval: materials (O8 résumés + lawyer fix + pretest,
  merit gate mean fit ≥ 5) → manipulation check (4 models) → DeepSeek pilot
  (software_engineer + emt_paramedic, 1 sample) → DeepSeek full → short
  report → researcher approval → other three models.

### 11.4 Execution log

| step | result | cost |
| --- | --- | --- |
| wording gate | APPROVED (§11.1) | — |
| O8 résumés + lawyer regen | 34/34 valid, licenses shown | $0.01 |
| pretest (merit gate ≥ 5) | all new résumés 8.2–10.0 | $0.05 |
| manipulation check ×4 | 4,701/4,704 valid; docs/phase3/manipulation_check.md | $0.55 |
| DeepSeek pilot (2 occs) | 2,513/2,513 valid, 0 refusals, 0 withholding | $0.64 |
| lawyer rerun (DeepSeek) | 474/474 valid | $0.06 |
| DeepSeek phase3_main | DONE: 91,844/91,888 valid (99.95%, one repair pass +158), 0 refusals | $24.34 |

### 11.7 Phase 3 COMPLETE (2026-10-21) — integrated report written

All four models finished phase3_main + lawyer rerun + repair chains. Final
validity (any-success per call): main run 99.91/98.99/98.95/99.83%;
phase 3 100/100/100/99.98%. Total spend $160.48 of $180 usable. Cross-model
report `docs/phase3/CROSS_MODEL.md`; key stats `phase3_key_stats.json`
(generated by `audit.analysis.phase3_key_stats`). Integrated academic report
rewritten at `docs/report/report.md` (draft 4.0) covering main run + phase 3
with the comparator-naming discipline throughout.

### 11.6 Remaining models — execution mode (2026-10-18)

§6.5 gate approved (§11.5). Throughput diagnosis: the cap is PER MODEL
(~0.6–0.8 calls/s each; concurrency-invariant, latency just inflates), so
Haiku/Luna/Qwen run in PARALLEL as detached nohup chains
(runs/nohup/phase3_<model>.log): per model phase3_main → straggler retry →
phase3_lawyer → targeted repair. Projected ~40h wall time for all three
(DeepSeek needed ~29h solo; the parallel streams coexist at ~0.6/s each).

### 11.5 PENDING APPROVAL — §6.5 gate: other three models

DeepSeek short report: `docs/phase3/SHORT_REPORT.md`; full tables
`docs/phase3/report_deepseek.md`. Key results: penalty is gender-blind (L3 =
gendered levels), decomposition shows the *interruption* + *family bundle* (not
the caregiving label) drive the penalty, no explicit-gender amplification, no
abstention, drift ≤ +3.5pp. Spend $66.85/$180; remaining three models est $85.

> **APPROVED: run Haiku / Luna / Qwen through phase-3 main + lawyer rerun —
> researcher, 2026-10-18** (chat approval during session; scope: phase3_main +
> phase3_lawyer per model, sequential, with post-run repair passes; projected
> spend ≈ $85 within the $180 usable cap.)




## 12. Phase 4 (SPEC_PHASE4) — wording gate

1. **System prompts (§B.1)**: exact spec text in `config/phase4_system_prompts.yaml`
   (sp_fair generic EEO instruction; sp_gap adds the targeted no-gap-penalty
   sentence). sp_none = no system prompt.
2. **Neutral gap labels (§C)**: the spec's example entries "Job search following
   company closure" / "Full-time professional certification program" exceed the
   spec's own ±15% length match to "Career break — extended travel" (+19%/+42%).
   Proposed (within ±6%/+3%): **"Job search after company closure"** and
   **"Full-time certification program"**. Same dates (Jan–Sep 2024), neutral
   cover note, no family content; validator + tests pass.
3. Plan verified: 12,000 calls/model (B 10,080 + C 1,920), 48,000 total,
   estimate ≈ $16 peak / ~$11 actual; phase4 cap $18; $19.52 usable remains.

> **APPROVED: phase4 wording — researcher, 2026-10-24** (chat approval; scope:
> system prompts as in §B.1, the two adjusted neutral labels above. Run order:
> DeepSeek first, parse/refusal check, then the other three.) — APPROVED via
> question form same day.

### 12.1 Budget clarification — researcher, 2026-10-29

> The operative budget cap is the **weekly** OpenRouter cap ($200/wk; current
> week ≈ $13). The $20 reserve line in budget.yaml is not a spending stop for
> phase 4. Researcher explicitly approved `--allow-reserve` for the remaining
> ~8,700 phase-4 calls (est. $2–6; lifetime total stays ≈ $182–186 < $200).

> Addendum (same day): per researcher instruction the lifetime budget guard is
> CANCELLED (total_cap raised to non-binding, reserve set to 0). Only the
> weekly cap (enforced on the OpenRouter key) and the per-run kill switch
> remain.
