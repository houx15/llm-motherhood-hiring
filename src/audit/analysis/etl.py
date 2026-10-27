"""Clean-data layer: persist build_tables output as typed parquet tables.

Pipeline (the analysis stack previously re-parsed the entire raw JSONL history
on every figures/stats run — 650k+ calls, GBs of memory; now):

    raw logs ──ETL (audit etl)──▶ runs/pooled/clean/*.parquet  (tidy, deduped,
                                   derived columns, moderators merged)
                 analysis/read ──▶ small stats JSONs
                     figures   ──▶ PDFs  (fast iteration)

build_tables(None, use_cache=True) (the pooled default everywhere) reads the
parquet cache when fresh; the cache is invalidated automatically whenever any
logs.jsonl is newer than the manifest. Single-run mode (run_id=...) always
reads raw logs (fresh-run inspection).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ..config import RUNS_DIR

CLEAN_DIR = RUNS_DIR / "pooled" / "clean"
TABLES = ["manip", "e1", "e4", "e1_e4", "e2", "e3", "diagnostics"]


def _source_max_mtime() -> float:
    mt = 0.0
    for f in RUNS_DIR.glob("*/logs.jsonl"):
        mt = max(mt, f.stat().st_mtime)
    return mt


def manifest_path() -> Path:
    return CLEAN_DIR / "manifest.json"


def cache_fresh() -> bool:
    mf = manifest_path()
    if not mf.exists():
        return False
    try:
        m = json.loads(mf.read_text())
    except json.JSONDecodeError:
        return False
    if m.get("code_version") != _code_version():
        return False
    if not all((CLEAN_DIR / f"{t}.parquet").exists() for t in m.get("tables", [])):
        return False
    return _source_max_mtime() <= m.get("source_max_mtime", 0)


def _code_version() -> str:
    """Cheap content hash of the code that builds the tables."""
    import hashlib

    h = hashlib.sha256()
    for p in [Path(__file__).parent / "build_tables.py", Path(__file__)]:
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def build_clean(force: bool = False) -> dict:
    """ETL: build tidy tables per model (bounded memory) and write the cache."""
    from .build_tables import build_tables

    if cache_fresh() and not force:
        return {"status": "fresh", "dir": str(CLEAN_DIR)}
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    models = ["deepseek_v41_flash", "claude_haiku_55", "gpt6_luna", "qwen38_flash"]
    acc: dict[str, list[pd.DataFrame]] = {t: [] for t in TABLES}
    for m in models:
        tabs = build_tables(None, model_key=m, use_cache=False)
        for t, df in tabs.items():
            if t in acc and not df.empty:
                acc[t].append(df)
    written = {}
    for t, parts in acc.items():
        if not parts:
            continue
        df = pd.concat(parts, ignore_index=True)
        p = CLEAN_DIR / f"{t}.parquet"
        df.to_parquet(p, index=False)
        written[t] = len(df)
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_max_mtime": _source_max_mtime(),
        "code_version": _code_version(),
        "tables": list(written),
        "rows": written,
    }
    manifest_path().write_text(json.dumps(manifest, indent=1))
    return {"status": "rebuilt", "tables": written, "dir": str(CLEAN_DIR)}


def load_clean(table: str) -> pd.DataFrame:
    p = CLEAN_DIR / f"{table}.parquet"
    if not p.exists():
        raise FileNotFoundError(f"clean table missing: {p} (run `uv run audit etl`)")
    return pd.read_parquet(p)
