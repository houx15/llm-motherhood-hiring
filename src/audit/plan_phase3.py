"""Phase-3 plan expansion (SPEC_PHASE3.md §4).

Implements E1-v3 (cue levels L0-L3 + placebos), E2-v3 (placebo contrasts +
direct woman-vs-man contrasts), E3-v3 (role/gender-rotated pools, compositions
a/b/c/e), the gender-perception manipulation check, and the lawyer-cells rerun.

Determinism: same design as plan.py — call_id = SHA-256 over the condition
payload; rebuilding yields byte-identical plans. `cue_level` enters the payload
only when set, so pre-phase-3 call_ids are unchanged.

E3-v3 pool balance (unit-tested): across the 36 pools per composition each
résumé appears with each gender exactly 18 times and in the parent role exactly
6 times (a/b) / 18 times (c: 12 mother + 6 father), via cyclic margin designs.
"""
from __future__ import annotations

import pandas as pd

from .config import load_names
from .plan import _balanced_paraphrases, _base_row, _call_id
from .budget import TOKEN_EST

E1_CODES = ["none", "parent", "parent_gap", "personal", "gap_travel"]
E1_MAINRUN_CELLS = ["none", "married", "parent", "parent_gap", "parent_committed"]
E2_CONTRASTS = ["parent", "parent_committed", "parent_gap", "personal", "gap_travel", "gap_parental_only"]
E2_MAINRUN_CONTRASTS = ["parent", "parent_committed", "parent_gap"]
DIRECT_CONTRASTS = ["gender_none", "gender_parent"]
GENDERED_LEVELS = ["name", "name_field", "initial_field"]
ALL_LEVELS = GENDERED_LEVELS + ["blind"]

N_NAMES = 6   # names per gender (config/names.yaml)
N_INIT = 6    # initials (config/cue_levels.yaml)
PAIRS = [(0, 1), (2, 3)]


def _split_cohorts() -> tuple[list[str], list[str]]:
    from .config import load_occupations_built

    occs = load_occupations_built().occupations
    o20 = [o.id for o in occs if o.cohort == "o20"]
    o8 = [o.id for o in occs if o.cohort == "o8"]
    return o20, o8


def _names_ok() -> None:
    n = load_names()
    assert len(n.female) == N_NAMES and len(n.male) == N_NAMES, "phase 3 needs 6 names/gender"


# ---------------------------------------------------------------- E1-v3

def expand_e1v3(cfg, model_key: str, occs: list[str], samples: int, pilot: bool = False) -> list[dict]:
    _names_ok()
    o20_all, o8_all = _split_cohorts()
    o20 = [o for o in occs if o in o20_all]
    o8 = [o for o in occs if o in o8_all]
    rows: list[dict] = []
    keys: list[tuple] = []

    def emit(occ, rid, level, gender, family, rep, reps):
        name_idx = rep % N_NAMES
        ctx = {
            "resume_id": rid, "gender": gender, "name_idx": name_idx,
            "family_code": family, "cue_level": level, "initial_idx": name_idx,
        }
        keys.append((rid, level, gender, family, name_idx))
        rows.append(
            _base_row(
                "e1", model_key, cfg.phase, occ,
                resume_ids=rid, gender=gender, family_code=family,
                name_idx=name_idx, paraphrase_id=0, sample_idx=rep,
                cue_level=level, render_ctx=ctx,
            )
        )

    # O20: new cue levels (L1, L2 gendered codes incl. pregnant; L3 gender-free)
    for occ in o20:
        for ri in range(4):
            rid = f"{occ}_{ri:02d}"
            for level in ("name_field", "initial_field"):
                for gender in ("female", "male"):
                    codes = E1_CODES + (["pregnant"] if gender == "female" else [])
                    for family in codes:
                        for rep in range(samples):
                            emit(occ, rid, level, gender, family, rep, samples)
            for family in E1_CODES:  # L3: no gender, no pregnant
                for rep in range(samples):
                    emit(occ, rid, "blind", None, family, rep, samples)
            # L0 new placebo codes (personal, gap_travel only)
            for family in ("personal", "gap_travel"):
                for gender in ("female", "male"):
                    for rep in range(samples):
                        emit(occ, rid, "name", gender, family, rep, samples)
            # drift anchor: none + parent, both genders, L0, fewer reps
            anchor_reps = 2 if not pilot else 1
            for family in ("none", "parent"):
                for gender in ("female", "male"):
                    for rep in range(anchor_reps):
                        emit(occ, rid, "name", gender, family, rep, anchor_reps)

    # O8: all levels incl. L0
    for occ in o8:
        for ri in range(4):
            rid = f"{occ}_{ri:02d}"
            for level in GENDERED_LEVELS:
                for gender in ("female", "male"):
                    codes = E1_CODES + (["pregnant"] if gender == "female" else [])
                    for family in codes:
                        for rep in range(samples):
                            emit(occ, rid, level, gender, family, rep, samples)
            for family in E1_CODES:
                for rep in range(samples):
                    emit(occ, rid, "blind", None, family, rep, samples)

    para = _balanced_paraphrases(keys)
    for row, key in zip(rows, keys):
        row["paraphrase_id"] = para[key]
    return rows


# ---------------------------------------------------------------- E2-v3

def _e2_cell(occ, model_key, phase, level, gender, contrast, child_r, parent_r,
             child_pos, k, sample) -> dict:
    ki, kj = k % N_NAMES, (k + 1) % N_NAMES  # two different names, same gender
    ctx = {
        "childless_resume": f"{occ}_{child_r:02d}", "parent_resume": f"{occ}_{parent_r:02d}",
        "childless_name_idx": ki, "parent_name_idx": kj, "gender": gender,
        "contrast": contrast, "childless_position": "A" if child_pos == 0 else "B",
        "cue_level": level, "childless_initial_idx": ki, "parent_initial_idx": kj,
    }
    return _base_row(
        "e2", model_key, phase, occ,
        resume_ids=ctx["childless_resume"] + "+" + ctx["parent_resume"],
        gender=gender, family_code=contrast, name_idx=ki, name_pair=f"{ki}-{kj}",
        paraphrase_id=0, sample_idx=sample, contrast=contrast, position=child_pos,
        cue_level=level, render_ctx=ctx,
    )


def _e2_direct_cell(occ, model_key, phase, level, contrast, woman_r, man_r,
                    woman_pos, k, sample) -> dict:
    fam = "none" if contrast == "gender_none" else "parent"
    wi, mi = k % N_NAMES, (k + 1) % N_NAMES  # different names AND surnames
    ctx = {
        "woman_resume": f"{occ}_{woman_r:02d}", "man_resume": f"{occ}_{man_r:02d}",
        "woman_name_idx": wi, "man_name_idx": mi,
        "woman_family": fam, "man_family": fam,
        "woman_position": "A" if woman_pos == 0 else "B",
        "cue_level": level, "woman_initial_idx": wi, "man_initial_idx": mi,
        "gender": None, "contrast": contrast,
    }
    return _base_row(
        "e2", model_key, phase, occ,
        resume_ids=ctx["woman_resume"] + "+" + ctx["man_resume"],
        gender=None, family_code=contrast, name_idx=wi,
        name_pair=f"{wi}F-{mi}M",
        paraphrase_id=0, sample_idx=sample, contrast=contrast, position=woman_pos,
        cue_level=level, render_ctx=ctx,
    )


def expand_e2v3(cfg, model_key: str, occs: list[str], samples: int, pilot: bool = False) -> list[dict]:
    _names_ok()
    o20_all, o8_all = _split_cohorts()
    o20 = [o for o in occs if o in o20_all]
    o8 = [o for o in occs if o in o8_all]
    rows: list[dict] = []
    n_draws = N_NAMES  # 6 name-draws = "3 name pairs x 2 samples"
    if pilot:
        n_draws = 3

    def same_gender_block(occ_list, level, contrasts, genders, samples_mult):
        for occ in occ_list:
            for (i, j) in PAIRS:
                for role in (0, 1):  # which resume carries the treatment
                    child_r, parent_r = (i, j) if role == 0 else (j, i)
                    for position in (0, 1):  # screen position of the childless candidate
                        for gender in genders:
                            for contrast in contrasts:
                                for k in range(n_draws):
                                    sample = (k // 3) if samples_mult == 2 else 0
                                    rows.append(_e2_cell(
                                        occ, model_key, cfg.phase, level, gender, contrast,
                                        child_r, parent_r, position, k, sample,
                                    ))

    def direct_block(occ_list, level):
        for occ in occ_list:
            for (i, j) in PAIRS:
                for role in (0, 1):  # which resume is the woman
                    woman_r, man_r = (i, j) if role == 0 else (j, i)
                    for position in (0, 1):  # screen position of the woman
                        for contrast in DIRECT_CONTRASTS:
                            for k in range(n_draws):
                                sample = (k // 3) if not pilot else 0
                                rows.append(_e2_direct_cell(
                                    occ, model_key, cfg.phase, level, contrast,
                                    woman_r, man_r, position, k, sample,
                                ))

    # O20 L0: new contrasts only (3 placebos x 2 genders) + 2 direct
    same_gender_block(o20, "name", ["personal", "gap_travel", "gap_parental_only"],
                      ["female", "male"], 2 if not pilot else 1)
    direct_block(o20, "name")
    # O20 L1 + L2: 6 contrasts x 2 genders + 2 direct
    for level in ("name_field", "initial_field"):
        same_gender_block(o20, level, E2_CONTRASTS, ["female", "male"], 2)
        direct_block(o20, level)
    # O20 L3: 6 contrasts, no gender, no direct
    same_gender_block(o20, "blind", E2_CONTRASTS, [None], 2)
    # O20 drift anchor: parent L0 both genders, 1 sample (3 name draws)
    for occ in o20:
        for (i, j) in PAIRS:
            for role in (0, 1):
                child_r, parent_r = (i, j) if role == 0 else (j, i)
                for position in (0, 1):
                    for gender in ("female", "male"):
                        for k in range(3):
                            rows.append(_e2_cell(occ, model_key, cfg.phase, "name",
                                                 gender, "parent", child_r, parent_r,
                                                 position, k, 0))
    # O8: all levels
    for level in GENDERED_LEVELS:
        same_gender_block(o8, level, E2_CONTRASTS, ["female", "male"], 2)
        direct_block(o8, level)
    same_gender_block(o8, "blind", E2_CONTRASTS, [None], 2)

    # balanced paraphrases over (resume pair, level, contrast, position, k)
    keys = [
        (r["resume_ids"], r["cue_level"], r["contrast"], r["position"], r["name_pair"])
        for r in rows
    ]
    para = _balanced_paraphrases(keys)
    for row, key in zip(rows, keys):
        row["paraphrase_id"] = para[key]
    return rows


# ---------------------------------------------------------------- E3-v3

def _e3_pool_v3(composition: str, draw: int, rotation: int) -> list[dict]:
    """6 candidates in base order; each {resume_idx, gender, family_code, name_idx, initial_idx}.

    Margin-balanced design (unit-tested): across the 36 pools of a composition
    each resume is female exactly 18x and parent exactly 6x (a/b) or 18x
    (c: 12 mother + 6 father) -- see tests/test_phase3.py::test_e3_pool_balance.
    """
    cands: list[dict] = []
    if composition in ("a", "b"):
        parent_gender = "female" if composition == "a" else "male"
        childless = [i for i in range(6) if i != draw]
        # positions of the 2 childless resumes matching the parent's gender
        sel = {(rotation + draw) % 5, (rotation + draw + 2) % 5}
        for q, i in enumerate(childless):
            g = parent_gender if q in sel else ("male" if parent_gender == "female" else "female")
            cands.append({"resume_idx": i, "gender": g, "family_code": "none"})
        cands.insert(min(draw, len(cands)),
                     {"resume_idx": draw, "gender": parent_gender, "family_code": "parent"})
    elif composition == "c":
        for i in range(6):
            k = (i - draw) % 6
            if k in (0, 1, 2):  # parent triple {draw, draw+1, draw+2} (cyclic)
                g = "male" if k == (rotation + draw) % 3 else "female"
                cands.append({"resume_idx": i, "gender": g, "family_code": "parent"})
            else:  # childless triple; slot = cyclic position within it
                slot = (i - draw - 3) % 6 % 3
                g = "female" if slot == (rotation + draw) % 3 else "male"
                cands.append({"resume_idx": i, "gender": g, "family_code": "none"})
    else:  # e: six childless, 3F/3M Latin square
        for i in range(6):
            g = "female" if ((i + draw + rotation) % 6) < 3 else "male"
            cands.append({"resume_idx": i, "gender": g, "family_code": "none"})

    # names: distinct within gender; initials: distinct across the whole pool
    seen_g: dict[str, int] = {}
    for rank, c in enumerate(cands):
        grank = seen_g.get(c["gender"], 0)
        seen_g[c["gender"]] = grank + 1
        c["name_idx"] = (grank + draw + rotation) % N_NAMES
        c["initial_idx"] = (rank + draw + rotation) % N_INIT
    return cands


E3_COMPS = ["a", "b", "c", "e"]


def expand_e3v3(cfg, model_key: str, occs: list[str], samples: int, pilot: bool = False) -> list[dict]:
    _names_ok()
    o20_all, _o8 = _split_cohorts()
    o20 = [o for o in occs if o in o20_all]
    rows: list[dict] = []
    keys: list[tuple] = []
    draws = range(1) if pilot else range(6)
    for occ in o20:
        for level in GENDERED_LEVELS:
            for comp in E3_COMPS:
                for draw in draws:
                    pool = _e3_pool_v3(comp, draw, 0 if pilot else draw)
                    for rotation in (range(1) if pilot else range(6)):
                        display = pool[rotation:] + pool[:rotation]
                        labels = [f"C{k+1}" for k in range(6)]
                        ctx = {
                            "cue_level": level,
                            "pool": [
                                {
                                    "label": labels[m],
                                    "resume_id": f"{occ}_{d['resume_idx']:02d}",
                                    "gender": d["gender"],
                                    "name_idx": d["name_idx"],
                                    "initial_idx": d["initial_idx"],
                                    "family_code": d["family_code"],
                                }
                                for m, d in enumerate(display)
                            ],
                        }
                        keys.append((occ, level, comp, draw, rotation))
                        rows.append(
                            _base_row(
                                "e3", model_key, cfg.phase, occ,
                                resume_ids="+".join(c["resume_id"] for c in ctx["pool"]),
                                paraphrase_id=0, sample_idx=0,
                                contrast=comp, position=rotation, draw=draw,
                                cue_level=level, render_ctx=ctx,
                            )
                        )
        # L3: composition a only, gender-free
        for draw in draws:
            pool = _e3_pool_v3("a", draw, 0 if pilot else draw)
            for rotation in (range(1) if pilot else range(6)):
                display = pool[rotation:] + pool[:rotation]
                labels = [f"C{k+1}" for k in range(6)]
                ctx = {
                    "cue_level": "blind",
                    "pool": [
                        {
                            "label": labels[m],
                            "resume_id": f"{occ}_{d['resume_idx']:02d}",
                            "gender": d["gender"],
                            "name_idx": d["name_idx"],
                            "initial_idx": d["initial_idx"],
                            "family_code": d["family_code"],
                        }
                        for m, d in enumerate(display)
                    ],
                }
                keys.append((occ, "blind", "a", draw, rotation))
                rows.append(
                    _base_row(
                        "e3", model_key, cfg.phase, occ,
                        resume_ids="+".join(c["resume_id"] for c in ctx["pool"]),
                        paraphrase_id=0, sample_idx=0,
                        contrast="a", position=rotation, draw=draw,
                        cue_level="blind", render_ctx=ctx,
                    )
                )
    para = _balanced_paraphrases(keys)
    for row, key in zip(rows, keys):
        row["paraphrase_id"] = para[key]
    return rows


# ------------------------------------------------- manipulation check (§2.2)

def expand_manip(cfg, model_key: str) -> list[dict]:
    _names_ok()
    from .config import load_occupations_built

    occs = [o.id for o in load_occupations_built().occupations]
    rows: list[dict] = []
    for occ in occs:
        rid = f"{occ}_00"
        variants = (
            [("name", g, n, n) for g in ("female", "male") for n in range(N_NAMES)]
            + [("name_field", g, n, n) for g in ("female", "male") for n in range(N_NAMES)]
            + [("initial_field", g, None, i) for g in ("female", "male") for i in range(N_INIT)]
            + [("blind", None, None, i) for i in range(N_INIT)]
        )
        for level, gender, name_idx, init_idx in variants:
            ctx = {
                "resume_id": rid, "gender": gender,
                "name_idx": name_idx if name_idx is not None else init_idx,
                "initial_idx": init_idx, "cue_level": level, "family_code": "none",
            }
            rows.append(
                _base_row(
                    "manip", model_key, cfg.phase, occ,
                    resume_ids=rid, gender=gender, family_code="none",
                    name_idx=ctx["name_idx"], paraphrase_id=0, sample_idx=0,
                    cue_level=level, render_ctx=ctx,
                )
            )
    return rows


# ------------------------------------------------- lawyer rerun (§4.4)

def expand_lawyer_fix(cfg, model_key: str) -> list[dict]:
    _names_ok()
    rows: list[dict] = []
    occ = "lawyer"
    keys: list[tuple] = []
    for ri in (0, 1):
        rid = f"lawyer_{ri:02d}"
        for gender in ("female", "male"):
            codes = E1_MAINRUN_CELLS + (["pregnant"] if gender == "female" else [])
            for family in codes:
                for name_idx in range(3):  # main-run rotation: 3 names
                    for s in range(5):     # main-run replication: 5 samples
                        ctx = {"resume_id": rid, "gender": gender, "name_idx": name_idx,
                               "family_code": family}
                        keys.append((rid, gender, family, name_idx, s))
                        rows.append(
                            _base_row(
                                "e1", model_key, cfg.phase, occ,
                                resume_ids=rid, gender=gender, family_code=family,
                                name_idx=name_idx, paraphrase_id=0, sample_idx=s,
                                render_ctx=ctx,
                            )
                        )
    # E2: original 3 contrasts x 2 genders, pair (0,1), main-run geometry
    name_pairs = [(0, 1), (0, 2), (1, 2)]
    for role in (0, 1):
        child_r, parent_r = (0, 1) if role == 0 else (1, 0)
        for position in (0, 1):
            for gender in ("female", "male"):
                for contrast in E2_MAINRUN_CONTRASTS:
                    for (ni, nj) in name_pairs:
                        for s in range(2):
                            ctx = {
                                "childless_resume": f"lawyer_{child_r:02d}",
                                "parent_resume": f"lawyer_{parent_r:02d}",
                                "childless_name_idx": ni, "parent_name_idx": nj,
                                "gender": gender, "contrast": contrast,
                                "childless_position": "A" if position == 0 else "B",
                            }
                            keys.append((f"lawyer_{child_r:02d}+lawyer_{parent_r:02d}",
                                         contrast, position, ni, nj, s))
                            rows.append(
                                _base_row(
                                    "e2", model_key, cfg.phase, occ,
                                    resume_ids=ctx["childless_resume"] + "+" + ctx["parent_resume"],
                                    gender=gender, family_code=contrast, name_idx=ni,
                                    name_pair=f"{ni}-{nj}", paraphrase_id=0, sample_idx=s,
                                    contrast=contrast, position=position, render_ctx=ctx,
                                )
                            )
    para = _balanced_paraphrases(keys)
    for row, key in zip(rows, keys):
        row["paraphrase_id"] = para[key]
    return rows


# ------------------------------------------------- dispatch + call ids

def _attach_ids(df: pd.DataFrame) -> pd.DataFrame:
    ids = []
    for r in df.to_dict("records"):
        payload = {
            "experiment": r["experiment"],
            "model_key": r["model_key"],
            "occupation_id": r["occupation_id"],
            "gender": r["gender"],
            "family_code": r["family_code"],
            "name_idx": r["name_idx"],
            "name_pair": r["name_pair"],
            "contrast": r["contrast"],
            "draw": r["draw"],
            "jd_variant": r["jd_variant"],
            "position": r["position"],
            "resume_ids": r["resume_ids"],
            "sample_idx": r["sample_idx"],
            "cue_level": r["cue_level"],
            "prompt_version": r["prompt_version"],
        }
        ids.append(_call_id(payload))
    df["call_id"] = ids
    return df


def expand_phase3(cfg) -> pd.DataFrame:
    """Dispatch on the experiment keys present in a phase-3 config."""
    all_rows: list[dict] = []
    from .config import load_occupations_built

    occs = [o.id for o in load_occupations_built().occupations] if cfg.occupations == "all" else list(cfg.occupations)
    pilot = bool(getattr(cfg, "pilot", False))
    e = cfg.experiments
    for model_key in cfg.models:
        if e.get("e1v3"):
            all_rows += expand_e1v3(cfg, model_key, occs, e["e1v3"].get("samples", 6), pilot=pilot)
        if e.get("e2v3"):
            all_rows += expand_e2v3(cfg, model_key, occs, e["e2v3"].get("samples", 2), pilot=pilot)
        if e.get("e3v3"):
            all_rows += expand_e3v3(cfg, model_key, occs, e["e3v3"].get("samples", 1), pilot=pilot)
        if e.get("manip"):
            all_rows += expand_manip(cfg, model_key)
        if e.get("lawyer_fix"):
            all_rows += expand_lawyer_fix(cfg, model_key)
    if not all_rows:
        raise SystemExit(f"no phase-3 experiments found in config {cfg.name!r}")
    df = pd.DataFrame(all_rows)
    df = _attach_ids(df)
    df["est_input_tokens"] = df["experiment"].map(lambda x: TOKEN_EST.get(x, (1500, 400))[0])
    df["est_output_tokens"] = df["experiment"].map(lambda x: TOKEN_EST.get(x, (1500, 400))[1])
    assert df["call_id"].is_unique, "call_ids must be unique"
    return df
