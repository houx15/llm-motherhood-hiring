"""Phase-4 plan expansion (SPEC_PHASE4 §B + §C).

Fairness-instruction system-prompt arms (sp_none / sp_fair / sp_gap) over the
E2 cell set: L0 {parent, parent_gap, gap_travel} × 2 genders and L1
{gender_parent}, 480 calls per cell (2 pairs × 2 roles × 2 positions × 3 name
draws × 1 sample). The neutral gap labels gap_closure / gap_cert run in the
sp_none arm only (same run, same prompt version as gap_travel).
"""
from __future__ import annotations

import pandas as pd

from .config import load_occupations_built
from .plan import _balanced_paraphrases, _base_row, _call_id
from .plan_phase3 import _e2_cell, _e2_direct_cell
from .budget import TOKEN_EST

ARMS = ["sp_none", "sp_fair", "sp_gap"]
L0_CONTRASTS = ["parent", "parent_gap", "gap_travel"]
NEUTRAL_LABELS = ["gap_closure", "gap_cert"]
PAIRS = [(0, 1), (2, 3)]


def expand_phase4(cfg) -> pd.DataFrame:
    _rows: list[dict] = []
    keys: list[tuple] = []
    occs = [o.id for o in load_occupations_built().occupations if o.cohort == "o20"]

    def emit(row):
        _rows.append(row)
        keys.append((row["occupation_id"], row["sysarm"], row["contrast"], row["gender"],
                     row["position"], row["name_pair"]))

    for model_key in cfg.models:
        for arm in ARMS:
            for occ in occs:
                for (i, j) in PAIRS:
                    for role in (0, 1):
                        child_r, parent_r = (i, j) if role == 0 else (j, i)
                        for position in (0, 1):
                            contrasts = list(L0_CONTRASTS)
                            if arm == "sp_none":
                                contrasts += NEUTRAL_LABELS  # Part C: same run
                            for gender in ("female", "male"):
                                for contrast in contrasts:
                                    for k in range(3):  # 3 name draws, 1 sample
                                        row = _e2_cell(occ, model_key, cfg.phase, "name",
                                                       gender, contrast, child_r, parent_r,
                                                       position, k, 0)
                                        row["sysarm"] = arm
                                        emit(row)
                            # L1 direct contrast (gender_parent), all arms
                            for k in range(3):
                                woman_r, man_r = (i, j) if role == 0 else (j, i)
                                row = _e2_direct_cell(occ, model_key, cfg.phase, "name_field",
                                                      "gender_parent", woman_r, man_r,
                                                      position, k, 0)
                                row["sysarm"] = arm
                                emit(row)
    para = _balanced_paraphrases(keys)
    for row, key in zip(_rows, keys):
        row["paraphrase_id"] = para[key]

    df = pd.DataFrame(_rows)
    ids = []
    for r in df.to_dict("records"):
        payload = {
            "experiment": r["experiment"], "model_key": r["model_key"],
            "occupation_id": r["occupation_id"], "gender": r["gender"],
            "family_code": r["family_code"], "name_idx": r["name_idx"],
            "name_pair": r["name_pair"], "contrast": r["contrast"],
            "position": r["position"], "resume_ids": r["resume_ids"],
            "sample_idx": r["sample_idx"], "cue_level": r["cue_level"],
            "sysarm": r["sysarm"], "prompt_version": r["prompt_version"],
        }
        ids.append(_call_id(payload))
    df["call_id"] = ids
    df["est_input_tokens"] = TOKEN_EST["e2"][0]
    df["est_output_tokens"] = TOKEN_EST["e2"][1]
    assert df["call_id"].is_unique
    return df
