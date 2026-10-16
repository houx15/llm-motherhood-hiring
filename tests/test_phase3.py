"""Phase-3 unit tests (SPEC_PHASE3 §6.1): cue rendering guarantees, placebo
surgical diffs, E3 pool balance, plan counts, determinism, manip parsing."""
import json
from pathlib import Path

import pandas as pd
import pytest

from audit.config import load_experiment
from audit.materials.perturb import apply_family_cue, render_resume
from audit.parse import parse_response
from audit.plan import PROMPT_VERSION
from audit.plan_phase3 import (
    N_NAMES,
    _e3_pool_v3,
    expand_e1v3,
    expand_e2v3,
    expand_e3v3,
    expand_lawyer_fix,
    expand_manip,
    expand_phase3,
)

RES = json.loads((Path("data/materials/base_resumes/software_engineer.json")).read_text())[0]
FAMILY_WORDS = [
    "married", "children", "parent", "mother", "father", "PTA", "pregnan",
    "parental", "family",
]


def render(fam, gender="female", name_idx=0, cue="name", init=0):
    return render_resume(RES, gender, name_idx, fam, cue_level=cue, initial_idx=init)


# ------------------------------------------------------------- cue levels

def test_female_male_differ_only_in_name_l0():
    f, m = render("parent", "female", 0), render("parent", "male", 0)
    lf, lm = f.splitlines(), m.splitlines()
    assert len(lf) == len(lm)
    diffs = [i for i, (a, b) in enumerate(zip(lf, lm)) if a != b]
    assert diffs == [2], f"L0 diff should be the name line only, got {diffs}"
    assert lf[2] == "Emily Baker" and lm[2] == "Greg Baker"


def test_female_male_differ_only_in_name_and_field_l1():
    f, m = render("parent", "female", 1, "name_field"), render("parent", "male", 1, "name_field")
    lf, lm = f.splitlines(), m.splitlines()
    assert len(lf) == len(lm)
    diffs = [i for i, (a, b) in enumerate(zip(lf, lm)) if a != b]
    assert diffs == [2, 3]
    assert lf[3] == "Gender: Female" and lm[3] == "Gender: Male"


def test_l2_vs_l1_differ_only_in_name_line():
    l1, l2 = render("parent", "female", 0, "name_field"), render("parent", "female", 0, "initial_field", 1)
    a, b = l1.splitlines(), l2.splitlines()
    assert len(a) == len(b)
    diffs = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    assert diffs == [2]
    assert a[2] == "Emily Baker" and b[2] == "M. Baker"
    assert a[3] == b[3] == "Gender: Female"


def test_blind_has_no_gender_signal():
    t = render("parent", "female", 0, "blind", 2)
    assert "Gender:" not in t
    for name in ("Emily", "Sarah", "Anne", "Greg", "Matthew", "Todd",
                 "Allison", "Laurie", "Meredith", "Brad", "Geoffrey", "Neil"):
        assert name not in t
    assert "K. Baker" in t.splitlines()[2]


def test_blind_rendering_identical_across_genders():
    assert render("parent", "female", 0, "blind", 0) == render("parent", "male", 0, "blind", 0)


def test_names_rotate_over_six():
    names = {render("none", "female", i).splitlines()[2] for i in range(6)}
    assert names == {"Emily Baker", "Sarah Walsh", "Anne Murphy",
                     "Allison Baker", "Laurie Walsh", "Meredith Murphy"}


# ------------------------------------------------------------- placebos

def _diff_lines(a: str, b: str):
    sa, sb = a.splitlines(), b.splitlines()
    out = []
    for i in range(max(len(sa), len(sb))):
        x = sa[i] if i < len(sa) else "<eof>"
        y = sb[i] if i < len(sb) else "<eof>"
        if x != y:
            out.append((x, y))
    return out


def test_placebo_personal_vs_none_only_specified_lines():
    a, b = render("none"), render("personal")
    sa = a.splitlines()
    d = _diff_lines(a, b)
    # exactly: the cover-note line changes, and 2 volunteer lines are appended
    assert len(d) == 3
    assert d[0][0].startswith("Cover note") and "marathon" in d[0][1]
    assert all(x == "<eof>" for x, _ in d[1:])
    assert d[1][1] == "Volunteer:" and "Riverside Pet Shelter" in d[2][1]
    # everything between the note and the appended volunteer block is unchanged
    assert b.splitlines()[2:-2] == sa[2:]


def test_placebo_personal_no_family_cues():
    t = render("personal").lower()
    assert not any(w.lower() in t for w in FAMILY_WORDS)


def test_gap_placebos_share_parent_gap_date_arithmetic():
    pg, gt, gpo = (apply_family_cue(RES, c) for c in ("parent_gap", "gap_travel", "gap_parental_only"))
    dates = lambda r: [(e["start"], e["end"]) for e in r["experience"]]
    titles = lambda r: [e["title"] for e in r["experience"]]
    # identical date structure across all three gap conditions
    assert dates(gt) == dates(gpo) == dates(pg)
    # gap_travel vs parent_gap differ ONLY in the leave label (and the PTA volunteer,
    # which lives outside experience); gap_parental_only shares the parent_gap label
    diff_tg = [i for i, (a, b) in enumerate(zip(titles(pg), titles(gt))) if a != b]
    assert len(diff_tg) == 1
    assert titles(gt)[diff_tg[0]] == "Career break — extended travel"
    assert titles(pg)[diff_tg[0]] == "Parental leave"
    assert titles(gpo) == titles(pg)


def test_gap_travel_vs_none_changes_only_leave_and_shifted_dates():
    a, b = render("none"), render("gap_travel")
    assert "Career break — extended travel (Jan 2024 – Sep 2024)" in b
    assert "Career break" not in a
    # neutral cover note unchanged
    assert a.splitlines()[0] == b.splitlines()[0]


def test_personal_volunteer_line_length_matched_to_parent():
    cues_parent = "PTA Coordinator, Lincoln Elementary School (2022-present)"
    cues_personal = "Volunteer Coordinator, Riverside Pet Shelter (2022-present)"
    assert abs(len(cues_personal) - len(cues_parent)) / len(cues_parent) <= 0.10


def test_placebo_cover_notes():
    from audit.config import load_family_cues

    notes = load_family_cues()["cover_note"]
    assert notes["gap_travel"] == notes["none"] == notes["gap_parental_only"]
    assert "marathon" in notes["personal"]


# ------------------------------------------------------------- E3 pools

@pytest.mark.parametrize("comp", ["a", "b", "c", "e"])
def test_e3_pool_balance(comp):
    """Every resume: each gender 18x; parent role 6x (a/b) or 18x (c: 12F/6M)."""
    pools = [_e3_pool_v3(comp, d, r) for d in range(6) for r in range(6)]
    assert len(pools) == 36
    for i in range(6):
        n_f = sum(1 for p in pools for c in p if c["resume_idx"] == i and c["gender"] == "female")
        n_par = sum(1 for p in pools for c in p if c["resume_idx"] == i and c["family_code"] == "parent")
        n_par_f = sum(
            1 for p in pools for c in p
            if c["resume_idx"] == i and c["family_code"] == "parent" and c["gender"] == "female"
        )
        assert n_f == 18, (comp, i, n_f)
        if comp in ("a", "b"):
            assert n_par == 6 and n_par_f in (0, 6)  # a: mother; b: father
        elif comp == "c":
            assert n_par == 18 and n_par_f == 12
        else:
            assert n_par == 0
    for p in pools:  # 3F/3M in every pool; distinct names within gender; distinct initials
        assert sum(c["gender"] == "female" for c in p) == 3
        for g in ("female", "male"):
            idx = [c["name_idx"] for c in p if c["gender"] == g]
            assert len(idx) == len(set(idx))
        inits = [c["initial_idx"] for c in p]
        assert len(inits) == len(set(inits))


# ------------------------------------------------------------- plan counts

def test_e1v3_counts_match_spec():
    cfg = load_experiment("phase3_main")
    rows = expand_e1v3(cfg, "m", ["software_engineer"], 6)
    # O20 block: 4 x (11+11+5) x 6 + 4x4x6 placebos + 4x4x2 anchor
    assert len(rows) == 4 * 27 * 6 + 4 * 4 * 6 + 4 * 4 * 2
    rows8 = expand_e1v3(cfg, "m", ["housekeeper"], 6)
    assert len(rows8) == 4 * 38 * 6  # O8: all levels


def test_e2v3_counts_match_spec():
    cfg = load_experiment("phase3_main")
    rows = expand_e2v3(cfg, "m", ["software_engineer"], 2)
    # O20: L0 (3 placebos x2g + 2 direct) x48 + L1,L2 (14 each) x48 + L3 6 x48 + anchor 2 x24
    assert len(rows) == (8 * 48) + 2 * (14 * 48) + (6 * 48) + (2 * 24)
    rows8 = expand_e2v3(cfg, "m", ["housekeeper"], 2)
    assert len(rows8) == (14 * 3 + 6) * 48


def test_e3v3_counts_match_spec():
    cfg = load_experiment("phase3_main")
    rows = expand_e3v3(cfg, "m", ["software_engineer"], 1)
    assert len(rows) == 3 * 4 * 36 + 36  # L0-L2 x a,b,c,e + L3 x a


def test_full_phase3_plan_counts_and_determinism():
    df = expand_phase3(load_experiment("phase3_main"))
    per = df[df.model_key == "deepseek_v41_flash"].groupby("experiment").size().to_dict()
    assert per == {"e1": 22816, "e2": 59712, "e3": 9360}
    df2 = expand_phase3(load_experiment("phase3_main"))
    assert (df["call_id"] == df2.loc[df.index, "call_id"]).all()
    assert df["call_id"].is_unique


def test_manip_count():
    rows = expand_manip(load_experiment("phase3_manip"), "m")
    assert len(rows) == 28 * 42  # 12 + 12 + 12 + 6 variants


def test_lawyer_fix_count_and_old_geometry():
    rows = expand_lawyer_fix(load_experiment("phase3_lawyer"), "m")
    e1 = [r for r in rows if r["experiment"] == "e1"]
    e2 = [r for r in rows if r["experiment"] == "e2"]
    assert len(e1) == 2 * 11 * 3 * 5      # original 11 cells x 3 names x 5 samples
    assert len(e2) == 3 * 2 * 2 * 2 * 3 * 2  # original 3 contrasts, main-run geometry
    assert all("cue_level" not in (r["render_ctx"] or {}) for r in rows)  # L0 like main run


def test_cue_level_in_payload_changes_call_id():
    cfg = load_experiment("phase3_main")
    rows = expand_e1v3(cfg, "m", ["software_engineer"], 1)
    ids_l1 = {r["call_id"] if "call_id" in r else None for r in rows}  # expand returns pre-id rows
    # expand_phase3 attaches ids; verify distinct across levels on the full plan
    df = expand_phase3(load_experiment("phase3_pilot"))
    sub = df[(df.experiment == "e1") & (df.occupation_id == "software_engineer")]
    assert sub["cue_level"].nunique() == 4
    assert sub.groupby("cue_level")["call_id"].nunique().eq(
        sub.groupby("cue_level").size()
    ).all()


# ------------------------------------------------------------- manip parsing

def test_manip_parse():
    ok = parse_response("manip", '{"perceived_gender": "Male"}')
    assert ok[1] and ok[0] == {"perceived_gender": "male"}
    ok2 = parse_response("manip", '{"perceived_gender": "unknown"}')
    assert ok2[1]
    bad = parse_response("manip", '{"perceived_gender": "nonbinary"}')
    assert not bad[1]


# ------------------------------------------------------------- E2 direct rendering

def test_e2_direct_prompt_renders_both_genders():
    from audit.runner import build_prompt

    cfg = load_experiment("phase3_main")
    rows = expand_e2v3(cfg, "m", ["software_engineer"], 2)
    direct = [r for r in rows if r["contrast"] == "gender_none" and r["cue_level"] == "name"]
    assert direct
    r0 = next(r for r in direct if r["position"] == 0)
    text, _ = build_prompt(r0)
    assert "Emily Baker" in text or "Sarah Walsh" in text or "Anne Murphy" in text \
        or "Allison" in text or "Laurie" in text or "Meredith" in text
    assert "Greg Baker" in text or "Matthew Walsh" in text or "Todd Murphy" in text \
        or "Brad" in text or "Geoffrey" in text or "Neil" in text
    # both candidates childless: no parent cue in the packet
    assert "PTA" not in text and "children" not in text
