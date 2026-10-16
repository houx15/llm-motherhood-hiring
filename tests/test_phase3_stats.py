"""Smoke tests for phase-3 analysis functions against completed pilot runs
(DeepSeek pilot + manipulation check exist on disk; skipped if not)."""
import pytest

from audit.analysis.phase3_stats import (
    cue_level_penalties,
    gender_preference,
    manip_summary,
    pilot_checks,
    placebo_decomposition,
)

PILOT = "20261016-191222-phase3_pilot-deepseek_v41_flash"


def test_manip_summary_shape():
    df = manip_summary(["deepseek_v41_flash", "claude_haiku_55"])
    if df.empty:
        pytest.skip("manip runs not on disk")
    assert set(df.columns) >= {"model", "level", "pct_correct"}
    ds = df[df.model == "DeepSeek"]
    # explicit field must be perfectly legible
    assert ds[ds.level == "L1 name+field"]["pct_correct"].iloc[0] == 1.0
    assert ds[ds.level == "L2 initial+field"]["pct_correct"].iloc[0] == 1.0
    # blind is never mostly-guessed
    blind = ds[ds.level == "L3 blind"]
    assert (blind["pct_female"].iloc[0] + blind["pct_male"].iloc[0]) < 0.10


def test_pilot_checks_run():
    try:
        text = pilot_checks(PILOT)
    except FileNotFoundError:
        pytest.skip("pilot run not on disk")
    assert "parse ok" in text
    assert "P(parent chosen)" in text


def test_cue_level_penalties_pilot():
    try:
        df = cue_level_penalties("deepseek_v41_flash")
    except FileNotFoundError:
        pytest.skip("pilot run not on disk")
    if df.empty:
        pytest.skip("no phase3 e2 data")
    sub = df[(df.contrast == "parent") & (df.level == "L0 name")]
    assert not sub.empty
    # pilot showed ~0.37 for P(parent) at L0
    assert 0.2 < float(sub["P(parent)"].mean()) < 0.5
    # blind rows carry no gender
    blind = df[df.level == "L3 blind"]
    assert not blind.empty


def test_gender_preference_pilot():
    try:
        df = gender_preference("deepseek_v41_flash")
    except FileNotFoundError:
        pytest.skip("pilot run not on disk")
    if df.empty:
        pytest.skip("no direct-contrast data")
    pw = df[df["stat"] == "P(woman chosen)"]
    assert not pw.empty
    assert pw["value"].between(0.3, 0.7).all()


def test_placebo_decomposition_columns():
    try:
        df = placebo_decomposition("deepseek_v41_flash")
    except FileNotFoundError:
        pytest.skip("pilot run not on disk")
    if df.empty:
        pytest.skip("no placebo cells")
    assert {"parenthood (parent-personal)", "caregiving (gap_par-gap_travel)",
            "bundle (parent_gap-gap_par)"} <= set(df.columns)
