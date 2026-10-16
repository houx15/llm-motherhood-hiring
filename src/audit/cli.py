"""CLI (spec §11): audit materials|plan|budget|run|parse|analyze|report."""
from __future__ import annotations

from pathlib import Path

import typer

from .config import MATERIALS_DIR, RUNS_DIR, load_budget, load_experiment, load_models

app = typer.Typer(help="LLM hiring audit pipeline (motherhood penalty).")
materials_app = typer.Typer(help="Build/validate materials.")
app.add_typer(materials_app, name="materials")


@materials_app.command("build")
def materials_build(
    model: str = typer.Option("deepseek_v41_flash", help="model key for generation"),
    force: bool = typer.Option(False, help="regenerate resumes even if frozen"),
    skip_gen: bool = typer.Option(False, help="only build moderators + JDs, no resume generation"),
    pricing: str = typer.Option(None, help="peak|off-peak override for estimates"),
):
    """Occupations + moderators, JDs, resumes (Kaggle-cleaned + synthetic), validators."""
    from .materials.occupations import run_build
    from .materials.resumes import run_materials

    run_build()
    if not skip_gen:
        run_materials(model, force=force, pricing=pricing)


@materials_app.command("pretest")
def materials_pretest(
    model: str = typer.Option("deepseek_v41_flash"),
    samples: int = typer.Option(5),
    pricing: str = typer.Option(None),
):
    """Quality pretest of base resumes (anonymous rendering)."""
    from .materials.pretest import run_pretest

    run_pretest(model, samples=samples, pricing=pricing)


@materials_app.command("phase3")
def materials_phase3(
    model: str = typer.Option("deepseek_v41_flash", help="model key for generation"),
    force: bool = typer.Option(False, help="regenerate drafts even if staged"),
    pricing: str = typer.Option(None, help="peak|off-peak override for estimates"),
    gen: bool = typer.Option(True, help="run resume generation (paid) vs build registry/JDs only"),
):
    """Phase-3 materials: O8 registry + JDs, O8 resumes (4/occupation, licensed),
    and the lawyer_00/01 attorney replacement (SPEC_PHASE3 §4.4, §5)."""
    from .materials.occupations_phase3 import build_phase3, build_phase3_jds
    from .materials.resumes import build_phase3_jobs, freeze_phase3, generate_materials, validate_resume

    build_phase3(verbose=True)
    build_phase3_jds()
    if gen:
        jobs = build_phase3_jobs(force=force)
        if jobs:
            import asyncio as _aio

            _aio.run(generate_materials(model, jobs, pricing=pricing))
        problems = freeze_phase3()
        if problems:
            raise SystemExit("FREEZE PROBLEMS:\n" + "\n".join(problems))
    # validate everything phase-3 needs
    failures = []
    import json as _json

    from .config import load_occupations_built

    for occ in load_occupations_built().occupations:
        if occ.cohort != "o8":
            continue
        p = MATERIALS_DIR / "base_resumes" / f"{occ.id}.json"
        if not p.exists():
            failures.append(f"{occ.id}: base_resumes/{occ.id}.json missing")
            continue
        for r in _json.loads(p.read_text()):
            failures += [f"{r['resume_id']}: {v}" for v in validate_resume(r)]
    lw = MATERIALS_DIR / "base_resumes" / "lawyer.json"
    for r in _json.loads(lw.read_text()):
        failures += [f"{r['resume_id']}: {v}" for v in validate_resume(r)]
    if failures:
        raise SystemExit(f"PHASE-3 VALIDATOR FAILED ({len(failures)}):\n" + "\n".join(failures[:40]))
    print("[phase3-materials] all phase-3 resumes present and valid")


@app.command("phase3-samples")
def phase3_samples(out: Path = typer.Option("docs/phase3/samples.md")):
    """Render one full prompt per new cell type for researcher wording approval
    (SPEC_PHASE3 §6.2 dry run). No API calls."""
    import json

    import pandas as pd

    from .config import load_experiment
    from .plan_phase3 import expand_e1v3, expand_e2v3, expand_e3v3, expand_manip, expand_phase3
    from .runner import build_prompt

    cfg = load_experiment("phase3_main")
    e1 = pd.DataFrame(expand_e1v3(cfg, "deepseek_v41_flash", ["software_engineer"], 1))
    e2 = pd.DataFrame(expand_e2v3(cfg, "deepseek_v41_flash", ["software_engineer"], 1))
    e3 = pd.DataFrame(expand_e3v3(cfg, "deepseek_v41_flash", ["software_engineer"], 1))
    mp = pd.DataFrame(expand_manip(load_experiment("phase3_manip"), "deepseek_v41_flash"))

    def pick(df, **kw):
        sub = df
        for k, v in kw.items():
            sub = sub[sub[k] == v]
        row = sub.iloc[0].to_dict()
        row["render_ctx"] = json.loads(row["render_ctx"]) if isinstance(row["render_ctx"], str) else row["render_ctx"]
        return row

    sections: list[tuple[str, list[dict]]] = [
        ("E1-v3 (isolated scoring)", [
            pick(e1, cue_level="name", family_code="personal", gender="female"),
            pick(e1, cue_level="name", family_code="gap_travel", gender="female"),
            pick(e1, cue_level="name_field", family_code="none", gender="female"),
            pick(e1, cue_level="name_field", family_code="parent", gender="male"),
            pick(e1, cue_level="name_field", family_code="pregnant"),
            pick(e1, cue_level="initial_field", family_code="parent_gap", gender="female"),
            pick(e1, cue_level="blind", family_code="parent"),
        ]),
        ("New O8 job descriptions (licensed examples)", []),
        ("E2-v3 (pairwise choice)", [
            pick(e2, cue_level="name", family_code="personal", gender="female", contrast="personal"),
            pick(e2, cue_level="name", family_code="gap_travel", gender="male", contrast="gap_travel"),
            pick(e2, cue_level="name", family_code="gap_parental_only", gender="female", contrast="gap_parental_only"),
            pick(e2, cue_level="name", contrast="gender_none"),
            pick(e2, cue_level="name_field", family_code="parent_gap", gender="female", contrast="parent_gap"),
            pick(e2, cue_level="initial_field", contrast="gender_parent"),
            pick(e2, cue_level="blind", family_code="parent", contrast="parent"),
        ]),
        ("E3-v3 (ranking)", [
            pick(e3, cue_level="name", contrast="a"),
            pick(e3, cue_level="name_field", contrast="c"),
            pick(e3, cue_level="initial_field", contrast="e"),
            pick(e3, cue_level="blind", contrast="a"),
        ]),
        ("Manipulation check (§2.2)", [
            pick(mp, cue_level="name", gender="female"),
            pick(mp, cue_level="name", gender="male"),
            pick(mp, cue_level="name_field", gender="male"),
            pick(mp, cue_level="initial_field", gender="female"),
            pick(mp, cue_level="blind"),
        ]),
    ]

    lines = [
        "# Phase-3 dry run: sample prompts for every new cell type",
        "",
        "Generated by `uv run audit phase3-samples` (no API calls). One full prompt per",
        "new cell type: cue levels L0 `name` / L1 `name_field` / L2 `initial_field` /",
        "L3 `blind`, placebo conditions, direct gender contrasts, E3-v3 pools, and the",
        "manipulation check. Template wording is unchanged from the main run except",
        "where noted. **Approval of these samples + the wording in QUESTIONS.md §11",
        "unlocks paid phase-3 runs.**",
        "",
    ]
    for title, rows in sections:
        lines.append(f"## {title}")
        lines.append("")
        if not rows:  # O8 JD section
            for occ in ("veterinarian", "emt_paramedic"):
                jd = json.loads((MATERIALS_DIR / "job_descriptions" / f"{occ}.json").read_text())["jd"]
                lines.append(f"### JD · {occ}")
                lines.append("")
                lines.append("```")
                lines.append(jd)
                lines.append("```")
                lines.append("")
            continue
        for row in rows:
            fam = row["family_code"] if isinstance(row["family_code"], str) else None
            con = row["contrast"] if isinstance(row["contrast"], str) else None
            gen = row["gender"] if isinstance(row["gender"], str) else None
            lvl = row["cue_level"] if isinstance(row["cue_level"], str) else "name"
            tag = f"{row['experiment']} · {lvl} · {fam or con}{' · ' + gen if gen else ''}"
            text, _ = build_prompt(row)
            lines.append(f"### {tag}")
            lines.append("")
            lines.append("```")
            lines.append(text)
            lines.append("```")
            lines.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print(f"[phase3-samples] wrote {len(lines)} lines -> {out}")


@app.command("phase3-report")
def phase3_report(
    model: str = typer.Option(...),
    run: str = typer.Option(None, help="optional single run_id (pilot checks)"),
    out: Path = typer.Option(None),
):
    """Phase-3 §8 tables for one model (or pilot checks for one run)."""
    from .analysis import phase3_stats as ps

    if run:
        text = ps.pilot_checks(run)
        print(text)
        return
    parts = [f"# Phase-3 report — {model}", ""]
    parts.append("## Cue-level parent penalties (E2 P(parent chosen))")
    parts.append("")
    parts.append(ps.cue_level_penalties(model).to_markdown(index=False))
    parts.append("")
    parts.append("## Gender preference by cue level (§8.1)")
    parts.append("")
    parts.append(ps.gender_preference(model).to_markdown(index=False))
    parts.append("")
    parts.append("## Placebo decomposition (§8.3, E2)")
    parts.append("")
    parts.append(ps.placebo_decomposition(model).to_markdown(index=False))
    parts.append("")
    parts.append("## Abstention: salary withholding by cue level (E1 women, §8.6)")
    parts.append("")
    parts.append(ps.abstention(model).to_markdown())
    parts.append("")
    parts.append("## Drift anchors vs main run (§8.7)")
    parts.append("")
    parts.append(ps.drift(model).to_markdown(index=False))
    text = "\n".join(parts)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        print(f"[phase3-report] wrote {out}")
    else:
        print(text)


@app.command("phase3-manip")
def phase3_manip_summary() -> None:
    """Gender-perception manipulation check across models (spec §2.2)."""
    from .analysis.phase3_stats import manip_summary

    print(manip_summary().to_markdown(index=False))


@app.command()
def plan(
    experiment: str = typer.Option(..., help="config name in config/experiments (e.g. pilot)"),
) -> None:
    """Expand experiment config -> data/plans/<name>.parquet + cost estimate."""
    import pandas as pd

    from .budget import TOKEN_EST, estimate_cost
    from .config import load_models
    from .plan import expand_plan, write_plan

    cfg = load_experiment(experiment)
    if not cfg.enabled:
        raise typer.Exit(f"experiment config {experiment!r} is disabled (enabled: false)")
    phase3_keys = {"e1v3", "e2v3", "e3v3", "manip", "lawyer_fix"}
    if phase3_keys & set(cfg.experiments):
        from .plan_phase3 import expand_phase3

        df = expand_phase3(cfg)
    else:
        df = expand_plan(cfg)
    path = write_plan(df, experiment)
    models = load_models()
    counts = df.groupby(["experiment", "model_key"]).size()
    print(f"[plan] {path}")
    print(counts.to_string())
    print(f"[plan] total calls: {len(df)}")
    for m in models.models:
        if m.key in set(df["model_key"]):
            for peak in (True, False):
                pin, pout = m.prices(peak)
                est = estimate_cost(df[df["model_key"] == m.key], pin, pout, safety=1.15)
                print(f"[plan] estimate {'peak' if peak else 'off-peak'}: ${est:.2f} ({m.key})")


@app.command()
def budget() -> None:
    """Budget status: cap, spent, reserve, remaining."""
    from .budget import BudgetGuard

    g = BudgetGuard()
    print(g.status_line())
    df = g.ledger.load()
    if not df.empty:
        print(df.groupby(["run_id", "model_key"])["cost_usd"].sum().sort_values(ascending=False).to_string())
    cfg = load_budget()
    print("phase caps:", cfg.phase_caps)
    import pandas as pd

    from .budget import TOKEN_EST, estimate_cost

    models = load_models()
    remaining = cfg.total_cap_usd - cfg.reserve_usd - g.ledger.spent_total()
    print(f"available for new work (cap - reserve - spent): ${remaining:.2f}")


@app.command()
def run(
    plan_path: Path = typer.Option(..., "--plan"),
    model: str = typer.Option(...),
    dry_run: bool = typer.Option(False),
    max_calls: int = typer.Option(None),
    allow_reserve: bool = typer.Option(False),
    concurrency: int = typer.Option(8),
    pricing: str = typer.Option(None, help="peak|off-peak override"),
    run_id: str = typer.Option(None),
) -> None:
    """Execute a call plan (resumable; every call logged)."""
    import asyncio

    from .runner import run_plan

    asyncio.run(
        run_plan(
            plan_path,
            model,
            run_id=run_id,
            dry_run=dry_run,
            max_calls=max_calls,
            allow_reserve=allow_reserve,
            concurrency=concurrency,
            pricing=pricing,
        )
    )


@app.command()
def parse(run: str = typer.Option(..., "--run")) -> None:
    """Re-parse all raw responses for a run (validity audit)."""
    import pandas as pd

    from .analysis.build_tables import load_run_logs
    from .parse import parse_response

    logs = load_run_logs(run)
    logs = logs[logs["experiment"].isin(["e1", "e2", "e3", "e4"])]
    n_ok = n_fail = 0
    for _, r in logs.iterrows():
        parsed, ok, refusal, err = parse_response(
            r["experiment"], r.get("raw_response") or ""
        )
        n_ok += ok
        n_fail += (not ok)
    print(f"[parse] run {run}: {n_ok} valid, {n_fail} invalid of {len(logs)}")


@app.command()
def analyze(run: str = typer.Option(..., "--run")) -> None:
    """Build tidy analysis tables for a run."""
    from .analysis.build_tables import save_tables

    save_tables(run)


@app.command()
def report(
    run: str = typer.Option(..., "--run"),
    model: str = typer.Option(None, help="restrict to one model_key (e.g. for pooled per-model reports)"),
) -> None:
    """Full markdown + figures report for a run."""
    from .analysis.report import make_report

    make_report(run, model_key=model)


@app.command()
def stats() -> None:
    """Recompute every reported statistic -> docs/report/stats.json + tables.md."""
    from .analysis.report_stats import main as stats_main

    stats_main()


@app.command()
def figures(out: Path = typer.Option("docs/report/figures")) -> None:
    """Generate all report figures as vector PDFs."""
    from .analysis.figures import generate_all

    generate_all(out)


@app.command()
def compare(out: Path = typer.Option(RUNS_DIR / "pooled")) -> None:
    """Cross-model comparison table + figure (all models in the ledger)."""
    from .analysis.compare import compare_models

    table = compare_models(out)
    cols = ["model_key", "slug", "parse_ok", "refusal",
            "e2_P_parent_parent_female", "e2_P_parent_parent_male",
            "e2_P_parent_parent_gap_female", "e2_P_parent_parent_gap_male",
            "e3_impact_parent_female", "e3_impact_parent_male",
            "e2_salary_gap_mother", "e4_greedy_gap_mother_pp"]
    cols = [c for c in cols if c in table.columns]
    print(table[cols].to_string(index=False))
    print(f"\n[compare] table + figure -> {out}")


@app.command()
def repair(
    run_glob: str = typer.Option("*/logs.jsonl", help="glob of logs.jsonl files to scan"),
    model: str = typer.Option(...),
    max_calls: int = typer.Option(None),
) -> None:
    """Targeted second repair pass for invalid non-refusal calls (documented deviation)."""
    from .repair import run_repair

    run_repair(run_glob, model, max_calls)


if __name__ == "__main__":
    app()
