"""Build tidy per-experiment tables from run logs (+ occupation moderators)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ..config import MATERIALS_DIR, PLANS_DIR, RUNS_DIR, load_occupations_built


def load_run_logs(run_id: str | None = None, model_key: str | None = None) -> pd.DataFrame:
    rows = []
    files = [RUNS_DIR / run_id / "logs.jsonl"] if run_id else sorted(RUNS_DIR.glob("*/logs.jsonl"))
    for f in files:
        if not f.exists():
            continue
        for line in f.read_text().splitlines():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    if model_key and "model_key" in df.columns:
        df = df[df["model_key"] == model_key]
    # pooled mode (run_id=None): dedup by call_id, preferring valid parses (repairs,
    # re-runs) and the latest attempt
    if run_id is None and "call_id" in df.columns:
        df["_ok"] = df.get("parse_ok", False).fillna(False).astype(int)
        df = df.sort_values(["_ok", "request_ts"], ascending=[False, False])
        df = df.drop_duplicates("call_id", keep="first").drop(columns=["_ok"])
    return df


def _moderators() -> pd.DataFrame:
    df = pd.DataFrame([o.model_dump() for o in load_occupations_built().occupations])
    keep = ["id", "title", "cell", "female_share", "median_wage", "time_demands", "in_e4"]
    # phase-3 O*NET work-activity scores for all 28 occupations, when built
    p3 = MATERIALS_DIR / "occupations_phase3.csv"
    if p3.exists():
        scores = pd.read_csv(p3)[["id", "physical", "care", "analytic", "manage"]]
        df = df.drop(columns=[c for c in scores.columns if c != "id"]).merge(scores, on="id", how="left")
        keep += ["physical", "care", "analytic", "manage"]
    return df[keep].rename(columns={"id": "occupation_id"})


def _ctx_from_plan(run_id: str | None) -> pd.Series:
    """call_id -> render_ctx, recovered from plan parquets (manifest points to it)."""
    if run_id is None:  # pooled: load every experiment plan
        plans = sorted(PLANS_DIR.glob("*.parquet"))
        dfs = [pd.read_parquet(p, columns=["call_id", "render_ctx"]) for p in plans]
        if not dfs:
            return pd.Series(dtype=object)
        plan = pd.concat(dfs, ignore_index=True)
        return plan.drop_duplicates("call_id").set_index("call_id")["render_ctx"]
    mf = RUNS_DIR / run_id / "manifest.json"
    if not mf.exists():
        return pd.Series(dtype=object)
    plan_path = json.loads(mf.read_text()).get("plan")
    if not plan_path or not Path(plan_path).exists():
        return pd.Series(dtype=object)
    plan = pd.read_parquet(plan_path, columns=["call_id", "render_ctx"])
    return plan.set_index("call_id")["render_ctx"]


def build_tables(run_id: str | None, model_key: str | None = None) -> dict[str, pd.DataFrame]:
    logs = load_run_logs(run_id, model_key=model_key)
    logs = logs[logs["experiment"].isin(["e1", "e2", "e3", "e4", "manip"])]
    if "render_ctx" not in logs.columns:
        logs["render_ctx"] = logs["call_id"].map(_ctx_from_plan(run_id))
    mod = _moderators()
    out: dict[str, pd.DataFrame] = {}

    # ---- manipulation check (phase 3) ----
    manip = logs[(logs["experiment"] == "manip") & logs["parse_ok"].fillna(False)].copy()
    if not manip.empty:
        parsed = pd.json_normalize(manip["parsed_json"])
        manip = pd.concat([manip.drop(columns=["parsed_json"]).reset_index(drop=True),
                           parsed.reset_index(drop=True)], axis=1)
        ctx = manip["render_ctx"].apply(lambda c: json.loads(c) if isinstance(c, str) else (c or {}))
        manip["true_gender"] = ctx.apply(lambda c: c.get("gender"))
        manip["correct"] = (manip["perceived_gender"] == manip["true_gender"]).astype(int)
        if "cue_level" not in manip.columns:
            manip["cue_level"] = None
        manip["cue_level"] = manip["cue_level"].fillna(ctx.apply(lambda c: c.get("cue_level")))
        out["manip"] = manip

    # ---- E1 / E4 ----
    e14 = logs[logs["experiment"].isin(["e1", "e4"]) & logs["parse_ok"].fillna(False)].copy()
    if not e14.empty:
        parsed = pd.json_normalize(e14["parsed_json"])
        e14 = pd.concat([e14.drop(columns=["parsed_json"]).reset_index(drop=True), parsed.reset_index(drop=True)], axis=1)
        e14["female"] = (e14["gender"] == "female").astype(int)
        e14["parent"] = e14["family_code"].isin(["parent", "parent_gap", "parent_committed"]).astype(int)
        if "cue_level" not in e14.columns:
            e14["cue_level"] = None
        _c = e14["render_ctx"].apply(lambda c: (json.loads(c) if isinstance(c, str) else (c or {})).get("cue_level"))
        e14["cue_level"] = e14["cue_level"].fillna(_c)
        e14["cue_level"] = e14["cue_level"].fillna("name")
        e14["withheld"] = (e14["starting_salary_usd"].fillna(0) == 0).astype(int)
        e14 = e14.merge(mod, on="occupation_id", how="left")
        for exp in ("e1", "e4"):
            sub = e14[e14["experiment"] == exp]
            if not sub.empty:
                out[exp] = sub
        out["e1_e4"] = e14

    # ---- E2 ----
    e2 = logs[(logs["experiment"] == "e2") & logs["parse_ok"].fillna(False)].copy()
    if not e2.empty:
        parsed = pd.json_normalize(e2["parsed_json"])
        e2 = pd.concat([e2.drop(columns=["parsed_json"]).reset_index(drop=True), parsed.reset_index(drop=True)], axis=1)
        # resolve which screen slot is the parent / the woman from render_ctx
        ctx = e2["render_ctx"].apply(lambda c: json.loads(c) if isinstance(c, str) else (c or {}))
        e2["childless_position"] = ctx.apply(lambda c: c.get("childless_position"))
        e2["parent_position"] = e2["childless_position"].map({"A": "B", "B": "A"})
        e2["woman_position"] = ctx.apply(lambda c: c.get("woman_position"))
        e2["direct"] = e2["contrast"].isin(["gender_none", "gender_parent"])
        # same-gender contrasts: outcome = parent(treatment) chosen
        e2["parent_chosen"] = [
            (r["chosen"] == r["parent_position"]) if r["parent_position"] in ("A", "B") else None
            for _, r in e2.iterrows()
        ]
        # direct gender contrasts: outcome = woman chosen
        e2["woman_chosen"] = [
            (r["chosen"] == r["woman_position"]) if r["woman_position"] in ("A", "B") else None
            for _, r in e2.iterrows()
        ]
        e2["position_a"] = (e2["chosen"] == "A").astype(int)
        e2["female"] = (e2["gender"] == "female").astype(int)
        if "cue_level" not in e2.columns:
            e2["cue_level"] = None
        e2["cue_level"] = e2["cue_level"].fillna(ctx.apply(lambda c: c.get("cue_level")))
        e2["cue_level"] = e2["cue_level"].fillna("name")
        # paired differences: treatment minus control (json_normalize flattens A/B to dotted cols)
        def _diff(row, key):
            if row["parent_position"] not in ("A", "B"):
                return None
            parent_side = row["parent_position"]
            child_side = "A" if parent_side == "B" else "B"
            return row[f"{parent_side}.{key}"] - row[f"{child_side}.{key}"]
        for key in ["starting_salary_usd", "overall_fit", "commitment", "competence", "promotability", "likability"]:
            e2[f"diff_{key}"] = e2.apply(lambda r: _diff(r, key), axis=1)
        # direct contrasts: woman minus man differences
        def _wdiff(row, key):
            if row["woman_position"] not in ("A", "B"):
                return None
            w, m = row["woman_position"], "A" if row["woman_position"] == "B" else "B"
            return row[f"{w}.{key}"] - row[f"{m}.{key}"]
        for key in ["starting_salary_usd", "overall_fit", "commitment", "competence", "promotability", "likability"]:
            e2[f"woman_minus_man_{key}"] = e2.apply(lambda r: _wdiff(r, key), axis=1)
        e2 = e2.merge(mod, on="occupation_id", how="left")
        out["e2"] = e2

    # ---- E3 ----
    e3 = logs[(logs["experiment"] == "e3") & logs["parse_ok"].fillna(False)].copy()
    if not e3.empty:
        recs = []
        for _, row in e3.iterrows():
            ctx = row.get("render_ctx")
            ctx = json.loads(ctx) if isinstance(ctx, str) else (ctx or {})
            pool = {c["label"]: c for c in ctx.get("pool", [])}
            lvl = ctx.get("cue_level") or "name"
            for rank, label in enumerate(row["parsed_json"]["ranking"], start=1):
                c = pool.get(label, {})
                recs.append(
                    {
                        "run_id": row["run_id"], "call_id": row["call_id"],
                        "occupation_id": row["occupation_id"], "composition": row["contrast"],
                        "draw": row.get("draw"), "rotation": row["position"], "sample_idx": row["sample_idx"],
                        "cue_level": lvl,
                        "rank": rank, "top1": int(rank == 1), "top3": int(rank <= 3),
                        "label": label, "position": int(label[1:]) if label and label[1:].isdigit() else None,
                        "resume_id": c.get("resume_id"), "gender": c.get("gender"),
                        "family_code": c.get("family_code"),
                    }
                )
        e3t = pd.DataFrame(recs)
        if not e3t.empty:
            e3t["female"] = (e3t["gender"] == "female").astype(int)
            e3t["parent"] = e3t["family_code"].isin(["parent", "parent_gap", "parent_committed"]).astype(int)
            e3t = e3t.merge(mod, on="occupation_id", how="left")
            out["e3"] = e3t

    # ---- diagnostics ----
    diag = logs.copy()
    if not diag.empty:
        diag["parse_ok"] = diag["parse_ok"].fillna(False)
        out["diagnostics"] = diag
    return out


def save_tables(run_id: str) -> Path:
    outdir = RUNS_DIR / run_id / "analysis"
    outdir.mkdir(parents=True, exist_ok=True)
    tables = build_tables(run_id)
    for name, df in tables.items():
        df.to_parquet(outdir / f"{name}.parquet", index=False)
    print(f"[analysis] wrote {list(tables)} -> {outdir}")
    return outdir
