# LLM Hiring Audit — Motherhood Penalty Pipeline

Reproducible pipeline that audits LLMs for motherhood penalties and fatherhood
bonuses in hiring. It constructs résumé variants (gender × family status ×
occupation × job-description wording), calls models through OpenRouter, logs
every response, enforces a hard budget, and produces analysis-ready datasets.

- Spec: `docs/SPEC.md`
- Research proposal: `docs/proposal.md`
- Open questions / decisions needing researcher approval: `QUESTIONS.md`

## Quickstart

```bash
uv sync                     # set up environment
cp .env.example .env        # add OPENROUTER_API_KEY=... (never commit .env)

uv run audit --help
uv run audit materials build       # occupations, résumés, JDs, validators
uv run audit plan --experiment pilot
uv run audit budget
uv run audit run --plan data/plans/pilot.parquet --model deepseek_v41_flash --dry-run
uv run audit run --plan data/plans/pilot.parquet --model deepseek_v41_flash
uv run audit report --run <run_id>
```

## Ground rules (from spec §0)

1. Hard budget cap USD 200 total; weekly cap USD 200 (OpenRouter key).
2. Pilot (Phase 0) before scale; full runs need explicit researcher approval.
3. Only pinned model slugs from `config/models.yaml` — never `*-latest`.
4. Every API call is logged; raw logs are append-only.
5. Runs are resumable by `call_id`; reruns never re-pay completed calls.
6. Materials and call plans are deterministic (fixed seeds / hashes).
7. Ambiguities go to `QUESTIONS.md`, not invented behavior.
8. `OPENROUTER_API_KEY` comes from `.env` / environment — git-ignored.

## Layout

```
config/          experiment + materials configs (YAML)
data/raw/        downloaded source data (git-ignored)
data/materials/  frozen base résumés, JDs, pretest outputs (committed)
data/plans/      generated call plans
prompts/         Jinja2 prompt templates (3 paraphrases each)
src/audit/       pipeline code
runs/            per-run logs, manifests, reports (git-ignored)
tests/           pytest suite
```
