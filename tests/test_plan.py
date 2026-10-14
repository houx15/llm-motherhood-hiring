import pandas as pd

from audit.config import load_experiment
from audit.plan import (
    PROMPT_VERSION,
    expand_e1,
    expand_e2,
    expand_e3,
    expand_e4,
    expand_plan,
    _call_id,
)
from audit.materials.resumes import validate_resume

OCCS = ["software_engineer", "administrative_assistant"]


def _cfg(name="pilot"):
    return load_experiment(name)


def test_plan_counts_e1_full_grid():
    """Spec §5: 20 occ x 4 resumes x 11 cells x 3 names x 5 samples = 13,200."""
    cfg = _cfg()
    rows = expand_e1(cfg, "deepseek_v41_flash", [f"occ{i}" for i in range(20)], 5)
    assert len(rows) == 20 * 4 * 11 * 3 * 5


def test_plan_counts_e2():
    """20 x 2 x 2 x 2 x 2 x 3 x 3 x 5 = 14,400."""
    cfg = _cfg()
    rows = expand_e2(cfg, "m", [f"occ{i}" for i in range(20)], 5)
    assert len(rows) == 20 * 2 * 2 * 2 * 2 * 3 * 3 * 5


def test_plan_counts_e3():
    """20 x 4 compositions x 4 draws x 6 rotations x 3 samples = 5,760."""
    cfg = _cfg()
    rows = expand_e3(cfg, "m", [f"occ{i}" for i in range(20)], 3)
    assert len(rows) == 20 * 4 * 4 * 6 * 3


def test_plan_counts_e4():
    """8 x 4 x 2 x 3 x 3 x 5 variants x 5 samples = 14,400."""
    cfg = _cfg()
    rows = expand_e4(cfg, "m", [f"occ{i}" for i in range(8)], 5, [])
    assert len(rows) == 8 * 4 * 2 * 3 * 3 * 5 * 5


def test_pilot_counts():
    df = expand_plan(_cfg("pilot"))
    e1 = len(df[df.experiment == "e1"])
    e2 = len(df[df.experiment == "e2"])
    e3 = len(df[df.experiment == "e3"])
    assert (e1, e2, e3) == (2 * 4 * 11 * 3 * 5, 2 * 720, 2 * 288)
    # E4: only software_engineer is in_e4 among pilot occupations
    e4 = len(df[df.experiment == "e4"])
    assert e4 == 1 * 4 * 2 * 3 * 3 * 5 * 3  # pilot samples=3


def test_balance_names_paraphrase_position():
    df = expand_plan(_cfg("pilot"))
    e1 = df[df.experiment == "e1"]
    # within each occupation x gender x family cell, names and samples balanced
    g = e1.groupby(["occupation_id", "gender", "family_code", "name_idx"]).size()
    assert g.nunique() == 1
    par = e1.groupby("paraphrase_id").size()
    assert par.max() / par.min() < 1.35  # hash-balanced within ~33%
    e2 = df[df.experiment == "e2"]
    pos = e2.groupby("position").size()
    assert pos.nunique() == 1
    e3 = df[df.experiment == "e3"]
    rot = e3.groupby("position").size()
    assert rot.nunique() == 1


def test_call_id_stable():
    df1 = expand_plan(_cfg("pilot"))
    df2 = expand_plan(_cfg("pilot"))
    assert df1["call_id"].tolist() == df2["call_id"].tolist()
    assert df1["call_id"].is_unique


def test_call_id_changes_with_condition():
    payload_a = {"experiment": "e1", "model_key": "m", "family_code": "none"}
    payload_b = {"experiment": "e1", "model_key": "m", "family_code": "parent"}
    assert _call_id(payload_a) != _call_id(payload_b)
    # prompt_version is part of the id: template changes invalidate old completions
    payload_c = {**payload_a, "prompt_version": "different"}
    assert _call_id(payload_a) != _call_id(payload_c)


def test_e3_pool_genders_balanced_and_distinct_names():
    from audit.plan import _e3_pool

    for comp in ["a", "b", "c", "d"]:
        for draw in range(4):
            pool = _e3_pool("occ", comp, draw)
            assert len(pool) == 6
            females = sum(1 for c in pool if c["gender"] == "female")
            males = sum(1 for c in pool if c["gender"] == "male")
            if comp in ("a", "b", "c", "d"):
                assert females == 3 and males == 3, (comp, draw)
            for g in ("female", "male"):
                name_idx = [c["name_idx"] for c in pool if c["gender"] == g]
                assert len(name_idx) == len(set(name_idx)), (comp, draw, g)


def test_validate_resume_flags_cues():
    bad = {
        "resume_id": "x", "occupation_id": "x", "source": "synthetic", "role": "base",
        "summary": "Proud mother of two children", "experience": [], "education": [], "skills": [], "volunteer": [],
    }
    v = validate_resume(bad)
    assert any("cue" in s for s in v)


def test_validate_resume_allows_occupation_terms():
    """Teacher resumes may say 'children'/'parents' about students, not the applicant."""
    teacher = {
        "resume_id": "x", "occupation_id": "x", "source": "synthetic", "role": "base",
        "summary": "Preschool teacher skilled in early childhood development and parent communication.",
        "experience": [], "education": [], "skills": [], "volunteer": [],
    }
    v = validate_resume(teacher)
    assert not any("cue" in s for s in v)
