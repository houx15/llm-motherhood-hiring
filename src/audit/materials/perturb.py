"""Render base résumé JSON into prompt text, applying name + family-status cues
and (phase 3) gender-cue levels.

Design guarantees (tested in tests/):
- A rendered résumé differs from the `none` condition ONLY in the cue lines
  specified by config/family_cues.yaml and the name line.
- Female and male versions of a condition differ only in the name
  (and the gender field line where the cue level has one).
- L2 vs L1 differ only in the name line (initial vs full first name).
- Placebo conditions differ from `none` only in the lines specified in
  config/family_cues.yaml (volunteer line / leave entry / cover note).
- Dates are deterministic month arithmetic; `parent_gap` and both gap placebos
  share identical date arithmetic (leave 2024-01..2024-09, later entries shifted).
"""
from __future__ import annotations

import copy
import json
from datetime import date

from ..config import load_cue_levels, load_family_cues, load_names

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def parse_month(s: str | int) -> tuple[int, int]:
    """'2024-01' -> (2024, 1)."""
    if isinstance(s, int):
        return divmod(s, 100)[0], s % 100
    y, m = str(s).split("-")
    return int(y), int(m)


def add_months(y: int, m: int, k: int) -> tuple[int, int]:
    t = y * 12 + (m - 1) + k
    return t // 12, t % 12 + 1


def fmt_month(s: str | int | None) -> str:
    if s is None or str(s).lower() == "present":
        return "Present"
    y, m = parse_month(s)
    return f"{MONTHS[m - 1]} {y}"


def _month_int(s: str | int, default: int) -> int:
    if str(s).lower() == "present":
        return default
    y, m = parse_month(s)
    return y * 12 + m


def load_resume(resume: dict | str) -> dict:
    if isinstance(resume, str):
        resume = json.loads(resume)
    return resume


def apply_family_cue(resume: dict, family_code: str) -> dict:
    """Apply the resume-side changes for a family condition (never mutates input)."""
    r = copy.deepcopy(resume)
    cues = load_family_cues()
    changes = cues.get("resume_changes", {}).get(family_code, {})
    if changes.get("volunteer"):
        r["volunteer"] = list(r.get("volunteer", [])) + list(changes["volunteer"])
    if changes.get("extra_bullets"):
        if r["experience"]:
            r["experience"][-1]["bullets"] = (
                list(r["experience"][-1].get("bullets", []))
                + list(changes["extra_bullets"])
            )
    leave = changes.get("leave")
    if leave:
        ls, le = leave["start_month"], leave["end_month"]
        ls_y, ls_m = parse_month(ls)
        le_y, le_m = parse_month(le)
        ls_int = ls_y * 12 + ls_m
        le_int = le_y * 12 + le_m
        dur = le_int - ls_int + 1  # calendar months occupied by the leave
        # "now" anchor for Present entries: leave end + 24 months keeps entry non-empty
        now_int = le_int + 24
        new_exp: list[dict] = []
        leave_inserted = False
        for e in sorted(r["experience"], key=lambda e: _month_int(e["start"], 0)):
            s_int = _month_int(e["start"], 0)
            e_end_int = _month_int(e.get("end", "Present"), now_int)
            if e_end_int <= ls_int:
                new_exp.append(e)  # entirely before the leave
                continue
            if s_int >= ls_int:  # starts at/after leave start: shift by leave duration
                e2 = copy.deepcopy(e)
                e2["start"] = _fmt_int(s_int + dur if str(e["start"]).lower() != "present" else now_int)
                if str(e.get("end", "Present")).lower() != "present":
                    e2["end"] = _fmt_int(_month_int(e["end"], now_int) + dur)
                else:
                    e2["end"] = "Present"
                if not leave_inserted:
                    new_exp.append(
                        {"title": leave["label"], "employer": "", "start": ls, "end": le, "bullets": []}
                    )
                    leave_inserted = True
                new_exp.append(e2)
                continue
            # straddling entry: split around the leave
            before = copy.deepcopy(e)
            before["end"] = _fmt_int(ls_int - 1)
            new_exp.append(before)
            if not leave_inserted:
                new_exp.append(
                    {"title": leave["label"], "employer": "", "start": ls, "end": le, "bullets": []}
                )
                leave_inserted = True
            after = copy.deepcopy(e)
            after["start"] = _fmt_int(le_int + 1)
            after["end"] = "Present" if str(e.get("end", "Present")).lower() == "present" else e["end"]
            new_exp.append(after)
        r["experience"] = new_exp
    return r


def _fmt_int(t: int) -> str:
    y, m = divmod(t - 1, 12)
    return f"{y:04d}-{m + 1:02d}"


def _candidate_header(gender: str, name_idx: int, cue_level: str, initial_idx: int | None) -> str:
    """Name/identity block per cue level (SPEC_PHASE3 §2.1).

    L0 name: gendered first name + surname. L1 name_field: + "Gender: ..." line.
    L2 initial_field: initial + surname + field. L3 blind: initial + surname only.
    """
    levels = load_cue_levels()["levels"]
    if cue_level not in levels:
        raise ValueError(f"unknown cue level {cue_level!r}")
    names = load_names()
    surname = names.surnames[name_idx % len(names.surnames)]
    spec = levels[cue_level]
    if spec["use_initial"]:
        initials = load_cue_levels()["initials"]
        ii = (initial_idx if initial_idx is not None else name_idx) % len(initials)
        header = f"{initials[ii]} {surname}"
    else:
        first = names.first_names(gender)[name_idx % len(names.first_names(gender))]  # type: ignore[arg-type]
        header = f"{first} {surname}"
    if spec["gender_field"]:
        header += "\n" + load_cue_levels()["field_line"][gender]
    return header


def render_resume(
    resume: dict,
    gender: str,
    name_idx: int,
    family_code: str,
    cue_level: str = "name",
    initial_idx: int | None = None,
) -> str:
    """Render one candidate packet: cover note + named resume text.

    `cue_level` defaults to L0 (`name`) so main-run plans render identically.
    """
    header = _candidate_header(gender, name_idx, cue_level, initial_idx)
    r = apply_family_cue(resume, family_code)
    cues = load_family_cues()
    note = cues["cover_note"].get(family_code, cues["cover_note"]["none"])
    lines = [f"Cover note: \"{note}\"", "", header, ""]
    lines.append(f"Summary: {r['summary']}")
    lines.append("Experience:")
    for e in r["experience"]:
        employer = f", {e['employer']}" if e.get("employer") else ""
        lines.append(f"- {e['title']}{employer} ({fmt_month(e['start'])} – {fmt_month(e.get('end', 'Present'))})")
        for b in e.get("bullets", []):
            lines.append(f"  * {b}")
    lines.append("Education:")
    for ed in r["education"]:
        lines.append(f"- {ed['degree']}, {ed['institution']} ({ed.get('year', '')})")
    lines.append(f"Skills: {', '.join(r['skills'])}")
    if r.get("volunteer"):
        lines.append("Volunteer:")
        for v in r["volunteer"]:
            lines.append(f"- {v}")
    return "\n".join(lines)


def render_anonymous(resume: dict) -> str:
    """Pretest rendering: 'Candidate', neutral note, no family cue."""
    r = apply_family_cue(resume, "none")
    lines = ["Cover note: \"I am excited to be applying for this position.\"", "", "Candidate", ""]
    lines.append(f"Summary: {r['summary']}")
    lines.append("Experience:")
    for e in r["experience"]:
        employer = f", {e['employer']}" if e.get("employer") else ""
        lines.append(f"- {e['title']}{employer} ({fmt_month(e['start'])} – {fmt_month(e.get('end', 'Present'))})")
        for b in e.get("bullets", []):
            lines.append(f"  * {b}")
    lines.append("Education:")
    for ed in r["education"]:
        lines.append(f"- {ed['degree']}, {ed['institution']} ({ed.get('year', '')})")
    lines.append(f"Skills: {', '.join(r['skills'])}")
    return "\n".join(lines)
