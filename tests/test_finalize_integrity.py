"""Round-10 integrity guards: catch the finalize regressions if they recur.

1. E3 statistics must DIFFER across models (the pooled-E3 bug returned
   identical adjusted ratios for all four models).
2. Main-run E2 cells must rest on at most 40 résumé-pair clusters (20
   occupations x 2 pairs); more means non-main rows leaked in (e.g. phase-3
   repair runs whose names contain no 'phase3').
"""
import json
from pathlib import Path

import pytest

STATS = Path("docs/report/stats.json")


@pytest.fixture(scope="module")
def stats():
    return json.loads(STATS.read_text())


def test_e3_differs_across_models(stats):
    ratios = {m: v["e3_fe"]["F"]["adjusted_ratio"] for m, v in stats["models"].items()}
    assert len(set(ratios.values())) == len(ratios), f"E3 identical across models: {ratios}"
    spread = max(ratios.values()) - min(ratios.values())
    assert spread > 0.1, f"E3 spread suspiciously small: {ratios}"


def test_e3_known_values(stats):
    """Spot anchors: the published values (regression baseline)."""
    f = {m.split("_")[0]: v["e3_fe"]["F"]["adjusted_ratio"] for m, v in stats["models"].items()}
    assert abs(f["claude"] - 0.248) < 0.02
    assert abs(f["gpt6"] - 0.776) < 0.02


def test_main_run_e2_clusters(stats):
    for m, v in stats["models"].items():
        for cell, r in v["e2_clustered"]["cells"].items():
            n = r["n_clusters"]
            assert n <= 40, f"{m} {cell}: {n} clusters (> 40: non-main rows leaked)"


def test_main_run_e2_clusters_not_degenerate(stats):
    for m, v in stats["models"].items():
        ns = {r["n_clusters"] for r in v["e2_clustered"]["cells"].values()}
        assert max(ns) >= 39, f"{m}: fewer than 39 clusters — main rows missing?"
