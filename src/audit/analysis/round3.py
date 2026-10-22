"""Round-3 review computations (REVIEW_NOTES.md, 2026-10-22).

R3-1  matched-set placebo decomposition + pair-matched t-tests + Holm
R3-2  implicit gender-inference check: pronoun congruence in rationales
R3-3  direct-gender contrasts: pair-clustered t vs parity + level contrasts
R3-6  cue-level invariance tests (O8-only L0 vs L3, L1 vs L0)
R3-S5 E2 drift anchors (choice-probability deltas, the spec's flagged metric)
R3-S3 mother-vs-father by outcome (main run)
Writes docs/phase3/round3_stats.json and prints markdown-ready tables.
"""
import json
import re

import numpy as np
import pandas as pd
from scipy import stats as sps

from audit.analysis.build_tables import build_tables
from audit.analysis.phase3_stats import _tables_for
from audit.config import ROOT, load_occupations_built

MODELS = ["deepseek_v41_flash", "claude_haiku_55", "gpt6_luna", "qwen38_flash"]
SHORT = dict(zip(MODELS, ["deepseek", "haiku", "luna", "qwen"]))
O8 = {o.id for o in load_occupations_built().occupations if o.cohort == "o8"}
OUT: dict = {}


def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj, running = {}, 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, (m - i) * p)
        adj[k] = min(1.0, running)
    return adj


def _unordered_pair(e2: pd.DataFrame) -> pd.Series:
    """Cluster id = occupation x UNORDERED résumé pair (R4-MUST 1: `resume_ids`
    is role-ordered 'a+b' vs 'b+a' and would double the clusters)."""
    import re

    def pid(row):
        idxs = sorted(re.search(r"_(\d+)$", r).group(1) for r in str(row["resume_ids"]).split("+"))
        return f"{row['occupation_id']}|{'-'.join(idxs)}"
    return e2.apply(pid, axis=1)


def _pm(df, lvl, con):
    s = df[(df.cue_level == lvl) & (df.contrast == con)].copy()
    s["pc"] = pd.to_numeric(s["parent_chosen"], errors="coerce")
    s["pair"] = _unordered_pair(s)
    return s.groupby("pair")["pc"].mean()


def _wm(df, lvl, con):
    s = df[(df.cue_level == lvl) & (df.contrast == con)].copy()
    s["wc"] = pd.to_numeric(s["woman_chosen"], errors="coerce")
    s["pair"] = _unordered_pair(s)
    return s.groupby("pair")["wc"].mean()


def _pair_means(e2: pd.DataFrame, mask, contrast: str) -> pd.Series:
    sub = e2[mask & (e2.contrast == contrast)].copy()
    sub["pc"] = pd.to_numeric(sub["parent_chosen"], errors="coerce")
    sub["pair"] = _unordered_pair(sub)
    return sub.groupby("pair")["pc"].mean()


def _matched_t(e2, mask, c1, c2):
    """Pair-matched difference c1 - c2 across résumé pairs present in both."""
    a, b = _pair_means(e2, mask, c1), _pair_means(e2, mask, c2)
    common = a.index.intersection(b.index)
    if len(common) < 5:
        return None
    d = (a[common] - b[common]).values
    t, p = sps.ttest_1samp(d, 0)
    return {"diff": round(float(d.mean()), 3), "se": round(float(d.std(ddof=1) / np.sqrt(len(d))), 3),
            "t": round(float(t), 1), "p": round(float(p), 4), "n_pairs": int(len(common))}


# ---------------- R3-1: matched-set decomposition ----------------
def decomposition_matched() -> dict:
    res = {}
    for m in MODELS:
        e2 = _tables_for(m)["e2"]
        for mset, mask in {
            "o8_L0": (e2.occupation_id.isin(O8)) & (e2.cue_level == "name"),
            "o8_L1": (e2.occupation_id.isin(O8)) & (e2.cue_level == "name_field"),
            "o8_L2": (e2.occupation_id.isin(O8)) & (e2.cue_level == "initial_field"),
            "o8_L3": (e2.occupation_id.isin(O8)) & (e2.cue_level == "blind"),
            "o20_L1": (~e2.occupation_id.isin(O8)) & (e2.cue_level == "name_field"),
            "o20_L2": (~e2.occupation_id.isin(O8)) & (e2.cue_level == "initial_field"),
        }.items():
            res[f"{SHORT[m]}|{mset}"] = {
                "parenthood": _matched_t(e2, mask, "parent", "personal"),
                "label": _matched_t(e2, mask, "gap_parental_only", "gap_travel"),
                "bundle": _matched_t(e2, mask, "parent_gap", "gap_parental_only"),
            }
    # Holm within each model across its sets x components
    for m in MODELS:
        fam = {}
        for mset in ["o8_L0", "o8_L1", "o8_L2", "o8_L3", "o20_L1", "o20_L2"]:
            for comp in ("parenthood", "label", "bundle"):
                r = res[f"{SHORT[m]}|{mset}"][comp]
                if r:
                    fam[f"{mset}:{comp}"] = r["p"]
        adj = holm(fam)
        for k, v in adj.items():
            mset, comp = k.split(":")
            res[f"{SHORT[m]}|{mset}"][comp]["holm"] = round(v, 4)
    return res


# ---------------- R3-2: pronoun congruence ----------------
FEM = re.compile(r"\b(she|her|hers|herself)\b", re.I)
MAL = re.compile(r"\b(he|his|him|himself)\b", re.I)


def _pronoun_stats(rows: list[dict]) -> dict:
    n = len(rows)
    f = sum(1 for r in rows if FEM.search(r["rat"]) and not MAL.search(r["rat"]))
    m_ = sum(1 for r in rows if MAL.search(r["rat"]) and not FEM.search(r["rat"]))
    both = sum(1 for r in rows if FEM.search(r["rat"]) and MAL.search(r["rat"]))
    congruent = sum(1 for r in rows if r["ok"])
    return {"n": n, "pct_female_only": round(100 * f / n, 1), "pct_male_only": round(100 * m_ / n, 1),
            "pct_both": round(100 * both / n, 1),
            "pct_congruent_of_gendered": round(100 * congruent / max(1, f + m_ + both), 1)}


def pronoun_check() -> dict:
    """E1 `none` cells. L0-L2: does the rationale's pronoun match the name/field?
    L3 (blind): does the model impose gendered pronouns at all?"""
    res = {}
    for m in MODELS:
        tabs = build_tables(None, model_key=m)
        e1 = tabs["e1"]
        e1 = e1[(e1.family_code == "none") & e1.rationale.notna()].copy()
        e1["cue_level"] = e1["cue_level"].fillna("name")
        main = e1[~e1.run_id.str.contains("phase3")]
        p3 = e1[e1.run_id.str.contains("phase3")]

        def rows(df):
            out = []
            for _, r in df.iterrows():
                rat = str(r["rationale"])
                has_f, has_m = bool(FEM.search(rat)), bool(MAL.search(rat))
                ok = (r["gender"] == "female" and has_f and not has_m) or \
                     (r["gender"] == "male" and has_m and not has_f) or \
                     (has_f and has_m)  # both -> uninformative, treat as congruent-neutral
                out.append({"rat": rat, "ok": ok})
            return out

        entry = {"main_L0": _pronoun_stats(rows(main))}
        for lvl in ["name", "name_field", "initial_field", "blind"]:
            sub = p3[p3.cue_level == lvl]
            entry[f"p3_{lvl}"] = _pronoun_stats(rows(sub))
        res[SHORT[m]] = entry
    return res


# ---------------- R3-3: direct-gender inference ----------------
def direct_gender_inference() -> dict:
    res = {}
    for m in MODELS:
        e2 = _tables_for(m)["e2"]
        d = e2[e2.direct]
        entry: dict = {"parity": {}, "level_diff": {}}
        fam = {}
        for lvl in ["name", "name_field", "initial_field"]:
            for con in ["gender_none", "gender_parent"]:
                pm = _wm(d, lvl, con)
                t, p = sps.ttest_1samp(pm.values, 0.5)
                cell = f"{con}@{lvl}"
                entry["parity"][cell] = {"p_woman": round(float(pm.mean()), 3),
                                         "t_vs_half": round(float(t), 1), "p": round(float(p), 4),
                                         "n_pairs": int(len(pm))}
                fam[cell] = p
        adj = holm(fam)
        for k, v in adj.items():
            entry["parity"][k]["holm"] = round(v, 4)
        for con in ["gender_none", "gender_parent"]:
            a = _wm(d, "name_field", con)
            b = _wm(d, "name", con)
            common = a.index.intersection(b.index)
            if len(common) >= 5:
                diff = (a[common] - b[common]).values
                t, p = sps.ttest_1samp(diff, 0)
                entry["level_diff"][f"{con}:L1-L0"] = {"diff": round(float(diff.mean()), 3),
                                                       "t": round(float(t), 1), "p": round(float(p), 4)}
            a = _wm(d, "initial_field", con)
            b = _wm(d, "name_field", con)
            common = a.index.intersection(b.index)
            if len(common) >= 5:
                diff = (a[common] - b[common]).values
                t, p = sps.ttest_1samp(diff, 0)
                entry["level_diff"][f"{con}:L2-L1"] = {"diff": round(float(diff.mean()), 3),
                                                       "t": round(float(t), 1), "p": round(float(p), 4)}
        res[SHORT[m]] = entry
    return res


# ---------------- R3-6: cue-level invariance tests ----------------
def invariance_tests() -> dict:
    res = {}
    for m in MODELS:
        e2 = _tables_for(m)["e2"]
        sub = e2[e2.occupation_id.isin(O8)]
        entry = {}
        for con in ["parent", "parent_gap"]:
            for la, lb in [("name", "blind"), ("name_field", "name"), ("initial_field", "blind")]:
                a = _pm(sub, la, con)
                b = _pm(sub, lb, con)
                common = a.index.intersection(b.index)
                if len(common) >= 5:
                    d_ = (a[common] - b[common]).values
                    t, p = sps.ttest_1samp(d_, 0)
                    entry[f"{con}:{la}-{lb}"] = {"diff": round(float(d_.mean()), 3),
                                                 "t": round(float(t), 1), "p": round(float(p), 4),
                                                 "n_pairs": int(len(common))}
        res[SHORT[m]] = entry
    return res


# ---------------- R3-S5: E2 drift anchors ----------------
def e2_drift() -> dict:
    """Drift anchors: the phase-3 E2 `parent` L0 1-sample cells on O20 (the
    designed anchor; SPEC_PHASE3 §8.7 flags |delta| > .03 in choice probability).
    The lawyer occupation is excluded everywhere (its phase-3 cells use the
    replacement attorney résumés)."""
    res = {}
    for m in MODELS:
        e2 = build_tables(None, model_key=m)["e2"]
        main = e2[~e2.run_id.str.contains("phase3") & (e2.occupation_id != "lawyer")]
        p3 = e2[e2.run_id.str.contains("phase3") & (e2.cue_level == "name")
                & (~e2.occupation_id.isin(O8)) & (e2.occupation_id != "lawyer")]
        rows = {}
        o = main[(main.contrast == "parent")]
        n_ = p3[(p3.contrast == "parent")]
        for g in ["female", "male"]:
            om = float(o[o.gender == g]["parent_chosen"].astype(float).mean())
            nm = float(n_[n_.gender == g]["parent_chosen"].astype(float).mean()) if len(n_[n_.gender == g]) else None
            if nm is not None:
                rows[f"parent|{g}"] = {"main": round(om, 3), "phase3": round(nm, 3),
                                       "delta": round(nm - om, 3), "n_p3": int(len(n_[n_.gender == g]))}
        res[SHORT[m]] = rows
    return res


# ---------------- R4-2/3: mother-father by outcome (main run, with inference) ----------------
def mother_father_main() -> dict:
    """Mother-minus-father penalty differences by outcome, main run.

    E2: per unordered-pair cluster means for each gender, matched across pairs,
    t across pairs; Holm within each contrast's outcome family. Salary validity:
    a pair enters only if BOTH sides' offers are present and non-zero (withheld
    offers excluded); identical offers count as a zero difference.
    E1: per-résumé (parent - none) differences by gender, mothers-minus-fathers
    matched by résumé, t across résumés.
    """
    res = {}
    for m in MODELS:
        tabs = build_tables(None, model_key=m)
        e2 = tabs["e2"]
        e2 = e2[~e2.run_id.str.contains("phase3")].copy()
        e2["pair"] = _unordered_pair(e2)
        sal_ok = (pd.to_numeric(e2["A.starting_salary_usd"], errors="coerce").fillna(0) > 0) & \
                 (pd.to_numeric(e2["B.starting_salary_usd"], errors="coerce").fillna(0) > 0)
        e1 = tabs["e1"]
        e1 = e1[~e1.run_id.str.contains("phase3")].copy()
        e1["sal"] = e1["starting_salary_usd"].where(e1["withheld"] == 0)
        entry = {}
        for con in ["parent", "parent_gap"]:
            fam: dict = {}
            # --- E2 outcomes, pair-matched M - F ---
            for outcome, col in [("choice_pp", "parent_chosen"),
                                 ("salary_usd", "diff_starting_salary_usd"),
                                 ("commitment", "diff_commitment"),
                                 ("competence", "diff_competence"),
                                 ("likability", "diff_likability")]:
                pm: dict = {}
                for g in ("female", "male"):
                    sub = e2[(e2.contrast == con) & (e2.gender == g)]
                    if outcome == "salary_usd":
                        sub = sub[sal_ok]
                    pc = pd.to_numeric(sub[col], errors="coerce")
                    pm[g] = pd.concat([sub["pair"], pc.rename("v")], axis=1).dropna().groupby("pair")["v"].mean()
                common = pm["female"].index.intersection(pm["male"].index)
                d = (pm["female"][common] - pm["male"][common]).values
                t, p = sps.ttest_1samp(d, 0)
                fam[outcome] = {"mothers": round(float(pm["female"][common].mean()), 3),
                                "fathers": round(float(pm["male"][common].mean()), 3),
                                "M_minus_F": round(float(d.mean()), 3),
                                "t": round(float(t), 1), "p": round(float(p), 4),
                                "n_pairs": int(len(common))}
            # --- E1 perception outcomes, résumé-matched M - F ---
            for outcome in ["e1_commitment", "e1_competence", "e1_likability", "e1_salary_usd", "e1_fit"]:
                key = {"e1_commitment": "commitment", "e1_competence": "competence",
                       "e1_likability": "likability", "e1_salary_usd": "sal",
                       "e1_fit": "overall_fit"}[outcome]
                gd = {}
                for g in ("female", "male"):
                    treat = e1[(e1.gender == g) & (e1.family_code == con)].groupby("resume_ids")[key].mean()
                    base = e1[(e1.gender == g) & (e1.family_code == "none")].groupby("resume_ids")[key].mean()
                    gd[g] = (treat - base).dropna()
                common = gd["female"].index.intersection(gd["male"].index)
                if len(common) >= 10:
                    d = (gd["female"][common] - gd["male"][common]).values
                    t, p = sps.ttest_1samp(d, 0)
                    fam[outcome] = {"mothers": round(float(gd["female"][common].mean()), 3),
                                    "fathers": round(float(gd["male"][common].mean()), 3),
                                    "M_minus_F": round(float(d.mean()), 3),
                                    "t": round(float(t), 1), "p": round(float(p), 4),
                                    "n_resumes": int(len(common))}
            adj = holm({k: v["p"] for k, v in fam.items() if "p" in v})
            for k, v in adj.items():
                fam[k]["holm"] = round(v, 4)
            # withholding (women only; no male analogue)
            w = e1[e1.gender == "female"].groupby("family_code")["withheld"].mean()
            fam["withholding_women"] = {k: round(float(v), 3) for k, v in w.items() if k in
                                        ("none", "married", "parent", "parent_gap", "pregnant")}
            entry[con] = fam
        res[SHORT[m]] = entry
    return res


if __name__ == "__main__":
    OUT["decomposition_matched"] = decomposition_matched()
    OUT["pronoun_check"] = pronoun_check()
    OUT["direct_gender"] = direct_gender_inference()
    OUT["invariance"] = invariance_tests()
    OUT["e2_drift"] = e2_drift()
    OUT["mother_father_main"] = mother_father_main()
    p = ROOT / "docs" / "phase3" / "round3_stats.json"
    p.write_text(json.dumps(OUT, indent=1))
    print(f"wrote {p}")
    # console digests
    print("\n== R3-1 label effect (matched sets), p-values / Holm ==")
    for k, v in OUT["decomposition_matched"].items():
        lab = v.get("label")
        if lab:
            print(f"{k:22} diff {lab['diff']:+.3f} t {lab['t']:+.1f} p {lab['p']:.3f} H {lab.get('holm')}")
    print("\n== R3-2 pronoun congruence (E1 none) ==")
    for mk, v in OUT["pronoun_check"].items():
        ml = v["main_L0"]
        print(f"{mk:9} main-L0: gendered {100-ml['pct_female_only']-ml['pct_male_only']-ml['pct_both']:.0f}% none;"
              f" among gendered {ml['pct_congruent_of_gendered']}% congruent (n={ml['n']})")
    print("\n== R3-3 direct gender: t vs parity (Holm) ==")
    for mk, v in OUT["direct_gender"].items():
        line = f"{mk:9}"
        for cell in ["gender_none@name", "gender_none@name_field", "gender_parent@name", "gender_parent@name_field"]:
            c = v["parity"][cell]
            line += f"  {cell.split('@')[1][:4]}: {c['p_woman']:.3f} (t{c['t_vs_half']:+.0f},H{c['holm']:.2f})"
        print(line)
    print("\n== R3-6 invariance L0 vs L3 (O8) ==")
    for mk, v in OUT["invariance"].items():
        print(f"{mk:9} parent L0-L3: {v.get('parent:name-blind')}  gap L0-L3: {v.get('parent_gap:name-blind')}")
