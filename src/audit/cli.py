"""CLI (spec §11): audit materials|plan|budget|run|parse|analyze|report."""
from __future__ import annotations

from pathlib import Path

import typer

from .config import RUNS_DIR, load_budget, load_experiment, load_models

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
def report(run: str = typer.Option(..., "--run")) -> None:
    """Full markdown + figures report for a run."""
    from .analysis.report import make_report

    make_report(run)


if __name__ == "__main__":
    app()
