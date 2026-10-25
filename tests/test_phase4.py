"""Phase-4 unit tests (SPEC_PHASE4 §7.2): system-prompt arms, neutral gap labels."""
import json
from pathlib import Path

import pandas as pd

from audit.config import load_experiment, load_phase4_arms
from audit.materials.perturb import apply_family_cue, render_resume
from audit.runner import build_prompt, _sysarm

RES = json.loads((Path("data/materials/base_resumes/software_engineer.json")).read_text())[0]


def test_neutral_gap_labels_diff_only_in_label():
    a = apply_family_cue(RES, "gap_travel")
    b = apply_family_cue(RES, "gap_closure")
    c = apply_family_cue(RES, "gap_cert")
    da = [(e["start"], e["end"]) for e in a["experience"]]
    assert da == [(e["start"], e["end"]) for e in b["experience"]] == \
           [(e["start"], e["end"]) for e in c["experience"]]
    labels = lambda r: [e["title"] for e in r["experience"]]
    lb, lc = labels(b), labels(c)
    assert "Job search after company closure" in lb
    assert "Full-time certification program" in lc
    # vs gap_travel: exactly one title differs
    la = labels(a)
    assert sum(x != y for x, y in zip(la, lb)) == 1
    assert sum(x != y for x, y in zip(la, lc)) == 1


def test_gap_label_lengths_within_15pct():
    t = "Career break — extended travel"
    for s in ("Job search after company closure", "Full-time certification program"):
        assert abs(len(s) - len(t)) / len(t) <= 0.15, (s, len(s))


def test_neutral_labels_no_family_cues():
    for fam in ("gap_closure", "gap_cert"):
        t = render_resume(RES, "female", 0, fam).lower()
        for w in ("parent", "parental", "child", "family", "pta", "pregnan"):
            assert w not in t, (fam, w)


def test_sysarm_plumbing():
    df = pd.read_parquet("data/plans/phase4_main.parquet")
    row = df[df.sysarm == "sp_fair"].iloc[0].to_dict()
    assert _sysarm(row) is not None and "equal employment opportunity" in _sysarm(row)
    row_none = df[df.sysarm == "sp_none"].iloc[0].to_dict()
    assert _sysarm(row_none) is None
    text, system = build_prompt(row)
    assert system is not None and "protected characteristics" in system
    assert "CANDIDATE" in text or "Candidate" in text or "finalist" in text


def test_phase4_plan_counts():
    df = pd.read_parquet("data/plans/phase4_main.parquet")
    per = df[df.model_key == "deepseek_v41_flash"]
    assert len(per) == 12000  # B 3x3360 + C 1920
    # sp_none contains travel + closure + cert; other arms travel only
    n = per[per.sysarm == "sp_none"]
    for con in ("parent", "parent_gap", "gap_travel", "gap_closure", "gap_cert"):
        assert len(n[n.contrast == con]) == 2 * 480  # 2 genders
    assert len(n[n.contrast == "gender_parent"]) == 480
    for arm in ("sp_fair", "sp_gap"):
        s = per[per.sysarm == arm]
        assert len(s) == 3360
        assert not s.contrast.isin(["gap_closure", "gap_cert"]).any()
    assert df.call_id.is_unique
