"""Expand experiment configs into deterministic call plans (spec §5, §8).

call_id = SHA-256 of (experiment, model_key, condition fields, sample_idx,
prompt_version) -> byte-identical on rerun.
"""
from __future__ import annotations

import hashlib
import json

import pandas as pd

from .config import (
    ExperimentCfg,
    MATERIALS_DIR,
    PLANS_DIR,
    PROMPTS_DIR,
    load_occupations_built,
)
from .budget import TOKEN_EST

PROMPT_VERSION = hashlib.sha256(
    b"".join(sorted(p.read_bytes() for p in PROMPTS_DIR.glob("*.j2")))
).hexdigest()[:12]

FAMILY_BOTH = ["none", "married", "parent", "parent_gap", "parent_committed"]


def _hash_int(*parts) -> int:
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).digest()
    return int.from_bytes(h[:8], "big")


def _balanced_paraphrases(keys: list) -> dict:
    """Deterministic, exactly-balanced paraphrase assignment over key tuples.

    A fixed-seed permutation of the sorted keys is dealt round-robin over the
    3 templates, so each paraphrase appears equally often within every experiment.
    """
    import random as _random

    ordered = sorted(keys, key=lambda k: tuple(str(x) for x in k))
    perm = ordered[:]
    _random.Random(20261014).shuffle(perm)
    return {k: i % 3 for i, k in enumerate(perm)}


def _call_id(payload: dict) -> str:
    canon = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode()).hexdigest()


def resolve_occupations(cfg: ExperimentCfg) -> list[str]:
    occs = load_occupations_built().occupations
    if cfg.occupations == "all":
        return [o.id for o in occs]
    if cfg.occupations == "in_e4":
        return [o.id for o in occs if o.in_e4]
    return list(cfg.occupations)


def _names_for(gender: str) -> int:
    return 3  # three names per gender in config/names.yaml


def _base_row(experiment: str, model_key: str, phase: str, occ: str, **kw) -> dict:
    row = {
        "experiment": experiment,
        "model_key": model_key,
        "phase": phase,
        "occupation_id": occ,
        "prompt_version": PROMPT_VERSION,
        "jd_variant": "base",
        "position": None,
        "gender": None,
        "family_code": None,
        "name": None,
        "name_idx": None,
        "resume_ids": None,
        "paraphrase_id": None,
        "sample_idx": None,
        "contrast": None,
        "draw": None,
        "name_pair": None,
        "render_ctx": None,
    }
    row.update(kw)
    return row


def expand_e1(cfg: ExperimentCfg, model_key: str, occs: list[str], samples: int) -> list[dict]:
    keys = [
        (f"{occ}_{ri:02d}", ni)
        for occ in occs
        for ri in range(4)
        for ni in range(3)
    ]
    para_map = _balanced_paraphrases(keys)
    rows = []
    for occ in occs:
        for resume_idx in range(4):
            rid = f"{occ}_{resume_idx:02d}"
            for gender in ("female", "male"):
                codes = FAMILY_BOTH + (["pregnant"] if gender == "female" else [])
                for family in codes:
                    for name_idx in range(_names_for(gender)):
                        para = para_map[(rid, name_idx)]
                        for s in range(samples):
                            ctx = {
                                "resume_id": rid,
                                "gender": gender,
                                "name_idx": name_idx,
                                "family_code": family,
                            }
                            rows.append(
                                _base_row(
                                    "e1", model_key, cfg.phase, occ,
                                    resume_ids=rid, gender=gender, family_code=family,
                                    name_idx=name_idx, paraphrase_id=para, sample_idx=s,
                                    render_ctx=ctx,
                                )
                            )
    return rows


def expand_e2(cfg: ExperimentCfg, model_key: str, occs: list[str], samples: int) -> list[dict]:
    pairs = [(0, 1), (2, 3)]
    name_pairs = [(0, 1), (0, 2), (1, 2)]
    contrasts = ["parent", "parent_gap", "parent_committed"]
    keys = [
        (occ, i, j, role, contrast, ni, nj)
        for occ in occs
        for (i, j) in pairs
        for role in (0, 1)
        for contrast in contrasts
        for (ni, nj) in name_pairs
    ]
    para_map = _balanced_paraphrases(keys)
    rows = []
    for occ in occs:
        for (i, j) in pairs:
            for role in (0, 1):  # which resume carries the parent cue
                child_r, parent_r = (i, j) if role == 0 else (j, i)
                for position in (0, 1):  # screen position of the CHILDLESS candidate
                    for gender in ("female", "male"):
                        for contrast in contrasts:
                            for (ni, nj) in name_pairs:
                                para = para_map[(occ, i, j, role, contrast, ni, nj)]
                                for s in range(samples):
                                    ctx = {
                                        "childless_resume": f"{occ}_{child_r:02d}",
                                        "parent_resume": f"{occ}_{parent_r:02d}",
                                        "childless_name_idx": ni,
                                        "parent_name_idx": nj,
                                        "gender": gender,
                                        "contrast": contrast,
                                        "childless_position": "A" if position == 0 else "B",
                                    }
                                    rows.append(
                                        _base_row(
                                            "e2", model_key, cfg.phase, occ,
                                            resume_ids=f"{occ}_{child_r:02d}+{occ}_{parent_r:02d}",
                                            gender=gender, family_code=contrast,
                                            name_idx=ni, name_pair=f"{ni}-{nj}",
                                            paraphrase_id=para, sample_idx=s,
                                            contrast=contrast, position=position,
                                            render_ctx=ctx,
                                        )
                                    )
    return rows


def _e3_pool(occ: str, composition: str, draw: int) -> list[dict]:
    """6 candidates in base order; each {resume_idx, gender, family_code}.

    draw 0-3 rotates the token-parent identity (comps a/b) and name offsets.
    Genders chosen so pools are 3 female / 3 male wherever possible.
    """
    cands: list[dict] = []
    if composition in ("a", "b"):
        parent_gender = "female" if composition == "a" else "male"
        other_genders = ["male", "female", "male", "female", "male"] if composition == "a" else ["female", "male", "female", "male", "female"]
        parent_idx = draw
        others = [i for i in range(6) if i != parent_idx]
        for k, i in enumerate(others):
            cands.append({"resume_idx": i, "gender": other_genders[k], "family_code": "none"})
        cands.insert(
            min(parent_idx, len(cands)), {"resume_idx": parent_idx, "gender": parent_gender, "family_code": "parent"}
        )
    elif composition == "c":
        parent_idx = [draw, (draw + 1) % 6, (draw + 2) % 6]
        parent_genders = ["female", "male", "female"]
        rest_genders = ["male", "female", "male"]
        pi = 0
        for i in range(6):
            if i in parent_idx:
                cands.append({"resume_idx": i, "gender": parent_genders[pi], "family_code": "parent"})
                pi += 1
            else:
                cands.append({"resume_idx": i, "gender": rest_genders[(i - pi) % 3], "family_code": "none"})
    else:  # d: all parents, alternating gender by base position
        for i in range(6):
            cands.append(
                {"resume_idx": i, "gender": "female" if i % 2 == 0 else "male", "family_code": "parent"}
            )
    # name assignment: rank within gender + draw offset (distinct names within gender)
    seen: dict[str, int] = {}
    for c in cands:
        rank = seen.get(c["gender"], 0)
        seen[c["gender"]] = rank + 1
        c["name_idx"] = (rank + draw) % 3
    return cands


def expand_e3(cfg: ExperimentCfg, model_key: str, occs: list[str], samples: int) -> list[dict]:
    rows = []
    comps = ["a", "b", "c", "d"]
    keys = [(occ, comp, draw, rot) for occ in occs for comp in comps for draw in range(4) for rot in range(6)]
    para_map = _balanced_paraphrases(keys)
    for occ in occs:
        for comp in comps:
            for draw in range(4):
                pool = _e3_pool(occ, comp, draw)
                for rotation in range(6):  # Latin square of display order
                    display = pool[rotation:] + pool[:rotation]
                    para = para_map[(occ, comp, draw, rotation)]
                    labels = [f"C{k+1}" for k in range(6)]
                    ctx = {
                        "pool": [
                            {
                                "label": labels[k],
                                "resume_id": f"{occ}_{d['resume_idx']:02d}",
                                "gender": d["gender"],
                                "name_idx": d["name_idx"],
                                "family_code": d["family_code"],
                            }
                            for k, d in enumerate(display)
                        ]
                    }
                    for s in range(samples):
                        rows.append(
                            _base_row(
                                "e3", model_key, cfg.phase, occ,
                                resume_ids="+".join(c["resume_id"] for c in ctx["pool"]),
                                paraphrase_id=para, sample_idx=s,
                                contrast=comp, position=rotation, draw=draw,
                                render_ctx=ctx,
                            )
                        )
    return rows


def expand_e4(cfg: ExperimentCfg, model_key: str, occs_in_e4: list[str], samples: int, pilot_occs: list[str]) -> list[dict]:
    occs = [o for o in occs_in_e4 if (not pilot_occs or o in pilot_occs)]
    keys = [(f"{occ}_{ri:02d}", ni) for occ in occs for ri in range(4) for ni in range(3)]
    para_map = _balanced_paraphrases(keys)
    rows = []
    variants = ["base", "greedy", "family_friendly", "greedy_ff", "eeo"]
    for occ in occs:
        for resume_idx in range(4):
            rid = f"{occ}_{resume_idx:02d}"
            for gender in ("female", "male"):
                for family in ("none", "parent", "parent_gap"):
                    for name_idx in range(3):
                        para = para_map[(rid, name_idx)]
                        for variant in variants:
                            for s in range(samples):
                                ctx = {
                                    "resume_id": rid,
                                    "gender": gender,
                                    "name_idx": name_idx,
                                    "family_code": family,
                                }
                                rows.append(
                                    _base_row(
                                        "e4", model_key, cfg.phase, occ,
                                        resume_ids=rid, gender=gender, family_code=family,
                                        name_idx=name_idx, paraphrase_id=para, sample_idx=s,
                                        jd_variant=variant, render_ctx=ctx,
                                    )
                                )
    return rows


def expand_plan(cfg: ExperimentCfg) -> pd.DataFrame:
    all_rows: list[dict] = []
    occs = resolve_occupations(cfg)
    for model_key in cfg.models:
        exps = cfg.experiments
        if exps.get("e1"):
            all_rows += expand_e1(cfg, model_key, occs, exps["e1"].get("samples", 5))
        if exps.get("e2"):
            all_rows += expand_e2(cfg, model_key, occs, exps["e2"].get("samples", 5))
        if exps.get("e3"):
            all_rows += expand_e3(cfg, model_key, occs, exps["e3"].get("samples", 5))
        if exps.get("e4") and (cfg.occupations == "in_e4" or cfg.name == "pilot"):
            e4_occs = [o.id for o in load_occupations_built().occupations if o.in_e4]
            pilot_occs = occs if cfg.name == "pilot" else []
            all_rows += expand_e4(cfg, model_key, e4_occs, exps["e4"].get("samples", 5), pilot_occs)
        if exps.get("e5") and exps["e5"].get("enabled", False):
            raise NotImplementedError("E5 plan expansion implemented but run disabled by config")
    df = pd.DataFrame(all_rows)
    ids = []
    for r in all_rows:
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
            "prompt_version": r["prompt_version"],
        }
        ids.append(_call_id(payload))
    df["call_id"] = ids
    df["est_input_tokens"] = df["experiment"].map(lambda e: TOKEN_EST.get(e, (1500, 400))[0])
    df["est_output_tokens"] = df["experiment"].map(lambda e: TOKEN_EST.get(e, (1500, 400))[1])
    assert df["call_id"].is_unique, "call_ids must be unique"
    return df


def write_plan(df: pd.DataFrame, name: str) -> pd.Index:
    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    path = PLANS_DIR / f"{name}.parquet"
    df.to_parquet(path, index=False)
    return path


def load_resumes(occ: str) -> list[dict]:
    p = MATERIALS_DIR / "base_resumes" / f"{occ}.json"
    return json.loads(p.read_text())
