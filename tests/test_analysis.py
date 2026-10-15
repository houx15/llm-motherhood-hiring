"""Smoke tests for analysis regressions (pilot data + synthetic panel)."""
import numpy as np
import pandas as pd

from audit.analysis.models import _find_key, e1_moderator_regressions, e1_regressions


def test_find_key_matches_two_and_three_way():
    keys = [
        "Intercept",
        "C(family_code)[T.parent]",
        "C(family_code)[T.parent_gap]",
        "C(female)[T.1]",
        "C(family_code)[T.parent]:C(female)[T.1]",
        "C(family_code)[T.parent]:Z[time_demands]",
        "C(family_code)[T.parent]:C(female)[T.1]:Z[time_demands]",
        "C(family_code)[T.parent_gap]:C(female)[T.1]:Z[time_demands]",
        "Z[time_demands]",
    ]
    assert _find_key(keys, "parent", True, None) == "C(family_code)[T.parent]:C(female)[T.1]"
    keys2 = [k.replace("Z[time_demands]", "zmod") for k in keys]
    assert _find_key(keys2, "parent", False, "zmod") == "C(family_code)[T.parent]:zmod"
    assert _find_key(keys2, "parent", True, "zmod") == "C(family_code)[T.parent]:C(female)[T.1]:zmod"
    assert _find_key(keys2, "parent_gap", True, "zmod") == "C(family_code)[T.parent_gap]:C(female)[T.1]:zmod"
    assert _find_key(keys, "married", True, None) is None


def _panel(n_occ=12, seed=7):
    rng = np.random.default_rng(seed)
    occs = [f"occ{i:02d}" for i in range(n_occ)]
    recs = []
    for occ in occs:
        fs, mw, td = rng.uniform(0.05, 0.95), rng.uniform(40e3, 200e3), rng.normal(0, 1)
        for ri in range(4):
            rid = f"{occ}_{ri:02d}"
            for gender, fem in [("female", 1), ("male", 0)]:
                for fam in ["none", "married", "parent", "parent_gap", "parent_committed"] + (
                    ["pregnant"] if gender == "female" else []
                ):
                    for ni in range(3):
                        for s in range(3):
                            recs.append(
                                {
                                    "occupation_id": occ, "resume_ids": rid, "gender": gender,
                                    "female": fem, "family_code": fam, "name_idx": ni, "sample_idx": s,
                                    "female_share": fs, "median_wage": mw, "time_demands": td,
                                    "interview": float(rng.uniform() > 0.2),
                                    "starting_salary_usd": 80e3 + 20e3 * fs + rng.normal(0, 5e3),
                                    "commitment": rng.normal(5.5, 0.8) + 1,
                                    "competence": rng.normal(5.5, 0.8),
                                    "overall_fit": rng.normal(8, 0.9),
                                    "promotability": rng.normal(5.5, 0.8),
                                    "likability": rng.normal(5.5, 0.8),
                                }
                            )
    return pd.DataFrame(recs)


def test_moderator_regressions_run_and_find_terms():
    df = _panel()
    out = e1_moderator_regressions(df)
    assert "note" not in out.columns
    assert set(out["Z"]) == {"female_share", "median_wage", "time_demands"}
    # the H3/H4 term must be present for every outcome x Z
    h34 = out[out["term"].str.contains("H3/H4")]
    assert len(h34) == 3 * 5
    assert h34["coef"].notna().all()
    # exact keys in the regression table (no fuzzy mislabels)
    assert out[out["term"] == "mother-minus-father gap @ mean Z"]["coef"].notna().all()


def test_moderator_too_few_occupations_returns_note():
    df = _panel(n_occ=2)
    out = e1_moderator_regressions(df)
    assert "note" in out.columns


def test_e1_regressions_smoke():
    df = _panel(n_occ=3)
    out = e1_regressions(df, outcomes=["commitment"])
    assert out["coef"].notna().any()
    mom = out[out["term"] == "parent (women) = motherhood effect"]
    assert len(mom) == 1 and np.isfinite(mom["coef"].iloc[0])
