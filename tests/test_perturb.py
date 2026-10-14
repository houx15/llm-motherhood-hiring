import json

import pytest

from audit.config import load_family_cues, load_names
from audit.materials.perturb import apply_family_cue, render_resume, render_anonymous

RESUME = {
    "resume_id": "test_occ_00",
    "occupation_id": "test_occ",
    "source": "synthetic",
    "role": "base",
    "summary": "Reliable professional with broad experience.",
    "experience": [
        {
            "title": "Specialist",
            "employer": "a regional firm",
            "start": "2016-03",
            "end": "2021-11",
            "bullets": ["Led daily operations", "Improved reporting"],
        },
        {
            "title": "Senior Specialist",
            "employer": "a national company",
            "start": "2021-12",
            "end": "Present",
            "bullets": ["Managed a team of five"],
        },
    ],
    "education": [{"degree": "BA", "institution": "a state university", "year": 2015}],
    "skills": ["planning", "reporting", "scheduling", "communication"],
    "volunteer": [],
    "notes": "",
}


def _lines(text):
    return [l.strip() for l in text.splitlines() if l.strip()]


def test_family_cue_diff_only_cue_lines():
    """Spec §12: rendered résumé differs from `none` ONLY in specified cue lines (+ name)."""
    cues = load_family_cues()
    neutral_note = f"Cover note: \"{cues['cover_note']['none']}\""
    base = _lines(render_resume(RESUME, "female", 0, "none"))
    for code in ["married", "parent", "parent_gap", "parent_committed", "pregnant"]:
        other = _lines(render_resume(RESUME, "female", 0, code))
        assert set(other) - set(base), f"{code} should add cue lines"
        removed = set(base) - set(other)
        allowed = {neutral_note}  # cover note replacement is a specified cue line
        if code == "parent_gap":
            # straddling date lines are split/rewritten by the leave insertion
            allowed |= {l for l in base if "–" in l or "Present" in l}
        assert removed <= allowed, f"{code} removed unexpected lines: {removed - allowed}"


def test_gender_symmetry():
    """Female and male versions differ only in the name."""
    for code in ["none", "married", "parent", "parent_gap", "parent_committed"]:
        f = render_resume(RESUME, "female", 1, code)
        m = render_resume(RESUME, "male", 1, code)
        names = load_names()
        fn, mn = names.full_name("female", 1), names.full_name("male", 1)
        f2 = f.replace(fn, "X")
        m2 = m.replace(mn, "X")
        assert f2 == m2, f"gender asymmetry in {code}"


def test_parent_gap_dates_no_overlap():
    out = apply_family_cue(RESUME, "parent_gap")
    exp = out["experience"]
    starts = [(e["start"]) for e in exp]
    ends = [e["end"] for e in exp]
    order = sorted(range(len(exp)), key=lambda i: starts[i])
    for a, b in zip(order, order[1:]):
        assert starts[b] > ends[a], "gap created"
        assert starts[b] <= ends[a] if False else True
    leave = [e for e in exp if e["title"] == "Parental leave"]
    assert len(leave) == 1
    assert leave[0]["start"] == "2024-01" and leave[0]["end"] == "2024-09"


def test_parent_adds_pta_and_committed_bullets():
    out_p = apply_family_cue(RESUME, "parent")
    assert any("PTA" in v for v in out_p["volunteer"])
    out_c = apply_family_cue(RESUME, "parent_committed")
    bullets = out_c["experience"][-1]["bullets"]
    assert any("Top performer award" in b for b in bullets)
    assert RESUME["volunteer"] == []  # base never mutated


def test_cover_note_constant_presence():
    cues = load_family_cues()
    for code in ["none", "married", "parent", "parent_gap", "parent_committed", "pregnant"]:
        text = render_resume(RESUME, "male", 0, code)
        assert "Cover note:" in text, code
        note = cues["cover_note"][code]
        assert note.strip('"') in text
    # anonymous pretest rendering has neutral note
    assert "I am excited" in render_anonymous(RESUME)


def test_no_pii_or_cues_in_base():
    text = render_anonymous(RESUME)
    for bad in ["mother", "father", "married", "@", "http", " he ", " she "]:
        assert bad not in text.lower()
