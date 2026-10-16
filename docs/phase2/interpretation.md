> **SUPERSEDED NOTICE (2026-10-16):** parts of this document were corrected after independent review — see `docs/report/report.md` (rev. 2). Key corrections: rev.2 of docs/report/report.md corrects: Haiku's −$18.7k pregnancy salary cut is a withholding artifact (excluding $0 offers: −$693, −0.8%); E2/E3 inference now résumé-pair clustered with FE-adjusted ratios; pooled/meta figures updated.

# Phase F results — the audit across four models

Runs of 2026-10-15/16: `deepseek/deepseek-v4.1-flash` (DeepInfra), `anthropic/claude-haiku-5.5`
(first-party), `openai/gpt-6-luna` (first-party), `qwen/qwen3.8-flash` (Alibaba). Same
frozen materials, same plans, same pins. **191,087 calls logged, $40.9 total spend**
(of the $200 cap). Effective validity after the one-pass repair protocol: Haiku 98.5%,
Luna 99.0%, Qwen 99.8%, DeepSeek 99.9%. Per-model reports: `runs/pooled_<model>/`,
cross-model table: `runs/pooled/model_comparison.csv`.

## 1. What replicates everywhere (the robust findings)

| | DeepSeek V4.1F | Claude Haiku 5.5 | GPT-6 Luna | Qwen3.8F |
| --- | --- | --- | --- | --- |
| E2 P(parent chosen), mothers / fathers | 0.36 / 0.35 | **0.23 / 0.28** | 0.30 / 0.30 | 0.39 / 0.40 |
| E2 P(chosen) leave-gap, mothers / fathers | 0.31 / 0.31 | **0.11 / 0.13** | 0.19 / 0.19 | 0.23 / 0.26 |
| E2 salary penalty (mother, PTA cue) | −$1,854 | −$1,332 | −$1,548 | −$1,775 |
| E3 token-parent top-3 impact ratio (m / f) | 0.56 / 0.53 | **0.14 / 0.15** | 0.59 / 0.60 | 0.57 / 0.59 |
| E4 greedy-JD extra penalty on gap-mothers | −3.3pp | −3.1pp | −0.8pp | −1.7pp |

1. **Every model penalizes parents in comparative decisions** — P(parent chosen) is
   below 0.5 in all 24 contrast × gender × model cells. No model shows the human
   fatherhood bonus; in most cells fathers fare *worse* than mothers.
2. **The caregiving cue (leave gap) always hurts more than parenthood itself** —
   ordered `parent_gap < parent < parent_committed` (worse) in every model.
3. **Recommended-salary penalties for mothers cluster in a tight band (−$1.3k to
   −$1.9k)** across four very different models — a robust ~1.5–2% motherhood pay
   penalty in paired evaluation.
4. **Every model violates the four-fifths rule for token parents in ranking pools**
   (impact ratios 0.14–0.60; only Luna/Qwen mothers come close to the 0.80 line at
   0.59 — still failing).
5. E1 single-résumé scoring stays near-flat for all models (surface fairness), and
   greedy-JD wording activates or amplifies the gap in all four.

## 2. Model-specific signatures

**Claude Haiku 5.5 — the severe outlier.** Roughly 2× the pairwise penalty of the
next model (leave-gap mothers chosen 11% of the time) and a catastrophic 0.14
impact ratio for token parents — mothers essentially disappear from shortlists.
It is also the only model that (a) *refuses* (0.5%, concentrated in family-cue
cells: "pregnancy disclosure is a protected characteristic"), (b) shows a unique
**second-position preference** in E2 (P(A)=0.39; the other three favor first
position, 0.53–0.83), and (c) levies a **pregnancy salary penalty of −$18,834
(p<0.001)** in E1 — an order of magnitude beyond every other model
(DeepSeek −$852, p=0.025; Luna −$1,074 n.s.; Qwen n.s.). Haiku is simultaneously
the most "safety-trained" responder and the strongest discriminator — safety
behavior and fair ranking are orthogonal here.

**GPT-6 Luna — the normative-discrimination prototype.** Uniquely, *high-commitment
parents do worse than plain parents* (mothers 0.235 vs 0.299): objective evidence of
devotion doesn't just fail to repair the penalty, it deepens it — exactly the
Benard-Correll normative signature (H6), and Luna is also the most position-neutral
model (P(A)=0.53), showing its penalties are not order artifacts. Its E4 greedy
effects are the smallest (−0.8pp), so its discrimination is cue-driven rather than
job-context-driven.

**Qwen3.8 Flash — bias visible in its rule-breaking.** Its ratings overflow the 1–7
scale ("8", "9") in E2 disproportionately for **childless candidates** (3:1, most in
leave-gap contrasts) — enthusiasm that breaks the instrument. After the documented
repair + strict-validity protocol its estimates land mid-pack (0.39/0.23). The
overflow itself is a measurable form of differential evaluation.

**DeepSeek V4.1 Flash — the reference pattern** (Phase 1 report): moderate
everywhere, mother-specific leave-gap penalty in pay (−$1,271 more than fathers),
greedy-JD sensitivity strongest.

## 3. What this means

- **Monoculture risk is asymmetric.** A recruiter using Haiku for shortlisting gets
  near-total exclusion of token mothers; the same résumés under Qwen lose ~40% of
  top-3 appearances. Same applicants, four deployed systems, four different labor
  market outcomes — and all four illegal under the four-fifths rule.
- **Safety refusals ≠ fairness.** Haiku both refuses most AND discriminates most.
- **The leave gap is the universal mechanism.** Across models, the penalty ranks
  cue-types identically; policies that let candidates omit caregiving gaps (or ban
  their inference) address the largest single component.
- **Prompt-level fixes are weak.** EEO boilerplate did nothing anywhere; greedy
  wording hurt everywhere it mattered; family-friendly sentences partially repaired
  rankings only for some models. Model choice dominates prompt choice.

## 4. Data quality notes (for the paper's methods section)

- Parse validity ≥ 98.5% for all models after ≤1 targeted repair pass
  (repair protocol + Qwen scale-overflow analysis in QUESTIONS.md §10).
- Refusals as outcome: 230 (Haiku only), concentrated in family-cue cells
  (E2 parent-gap women 1.9%).
- Position bias: E2 P(A) = 0.83 (DeepSeek), 0.53 (Luna), 0.39 (Haiku);
  E3 top-1 C1→C6 decays monotonically in all models. All comparisons remain
  position-counterbalanced.

**Spend ledger:** $40.94 total · pilot+materials $1.33 · DeepSeek Phase 1 $5.76 ·
Phase F ~$33.85 · repairs ~$0.44. Weekly cap $200 — 20.5% used.
