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

> RESEARCHER REPLY (phase E):

> RESEARCHER REPLY (phase F):
