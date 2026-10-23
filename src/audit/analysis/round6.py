"""Round-6 computations (REVIEW_NOTES.md Round 6 + 6b).

6-3a amplification: do E2 choices amplify family cues MORE than quality differences?
       Estimate the quality-tracking slope from within-pair E1 fit differences, derive
       the cue's implied quality-equivalent, compare with its actual E1 effect.
6-3b noise model with within-résumé sigma (x sqrt2), sigma sensitivity, and a
       bootstrap CI for observed - predicted.
6b-1  TOST equivalence (±5pp) with 90% CIs: blind=names (per model), Haiku label,
       Qwen direct-gender parity.
6b-2  direct model-contrast tests (paired across the same résumé pairs):
       Luna vs Qwen / vs DeepSeek field response; Haiku vs others mother-father gap.
6b-3  wild cluster bootstrap (Rademacher) for small-cluster tests: O8 invariance
       and label (16 pairs), E4 DiD (32 résumé clusters).
6b-4  LPM robustness with pair FE + position/paraphrase/name controls (E2 cells).
6b-8  minimum detectable effects for the nulls.
Writes docs/phase3/round6_stats.json.
"""
import json

import numpy as np
import pandas as pd
from scipy import stats as sps

from audit.analysis.build_tables import build_tables
from audit.analysis.round3 import _pm, _unordered_pair
from audit.analysis.phase3_stats import _tables_for
from audit.config import ROOT

MODELS = ["deepseek_v41_flash", "claude_haiku_55", "gpt6_luna", "qwen38_flash"]
KEYS = ["deepseek", "haiku", "luna", "qwen"]
OUT: dict = {}


# ---------------- 6-3a amplification: cue vs quality ----------------
def amplification() -> dict:
    res = {}
    for m, k in zip(MODELS, KEYS):
        tabs = build_tables(None, model_key=m)
        e1 = tabs["e1"]
        e1 = e1[~e1.run_id.str.contains("phase3")]
        e2 = tabs["e2"]
        e2 = e2[~e2.run_id.str.contains("phase3")].copy()
        # resume quality from E1 none cells, per gender
        q = e1[e1.family_code == "none"].groupby(["resume_ids", "gender"])["overall_fit"].mean()
        rows = []
        for _, r in e2.iterrows():
            ctx = r.get("render_ctx")
            import json as _j

            ctx = _j.loads(ctx) if isinstance(ctx, str) else (ctx or {})
            pr, ch = ctx.get("parent_resume"), ctx.get("childless_resume")
            if not pr or not ch:
                continue
            qp = q.get((pr, r["gender"]))
            qc = q.get((ch, r["gender"]))
            if qp is None or qc is None or np.isnan(qp) or np.isnan(qc):
                continue
            rows.append({"dq": qp - qc,
                         "pc": pd.to_numeric(pd.Series([r["parent_chosen"]]).iloc[0], errors="coerce"),
                         "contrast": r["contrast"], "gender": r["gender"]})
        df = pd.DataFrame(rows).dropna()
        # quality-tracking slope: LPM of choice on dq among childless-quality variation
        # (use all rows; dq is orthogonal to the cue by counterbalancing)
        X = np.column_stack([np.ones(len(df)), df["dq"].values])
        beta = np.linalg.lstsq(X, df["pc"].values, rcond=None)[0]
        slope = float(beta[1])  # P(parent chosen) per +1 fit point of résumé quality
        entry = {"quality_slope_per_fit_point": round(slope, 3)}
        for con in ["parent", "parent_gap"]:
            sub = df[df.contrast == con]
            cue_choice_gap = float(0.5 - sub["pc"].mean())  # pp below parity
            implied_fit_points = cue_choice_gap / slope if slope else None
            e1_fit_effect = float(
                e1[(e1.family_code == con) & (e1.gender == "female")]["overall_fit"].mean()
                - e1[(e1.family_code == "none") & (e1.gender == "female")]["overall_fit"].mean()
            )
            entry[con] = {
                "choice_gap_pp": round(100 * cue_choice_gap, 1),
                "implied_quality_equivalent_fit_pts": round(implied_fit_points, 2) if implied_fit_points else None,
                "actual_e1_fit_effect": round(e1_fit_effect, 2),
                "amplification_ratio": round(abs(implied_fit_points / e1_fit_effect), 1) if implied_fit_points and e1_fit_effect else None,
            }
        res[k] = entry
    return res


# ---------------- 6-3b corrected noise model ----------------
def noise_model2() -> dict:
    res = {}
    rng = np.random.default_rng(20261023)
    for m, k in zip(MODELS, KEYS):
        tabs = build_tables(None, model_key=m)
        e1 = tabs["e1"]
        e1 = e1[~e1.run_id.str.contains("phase3")]
        e2 = tabs["e2"]
        e2 = e2[~e2.run_id.str.contains("phase3")].copy()
        e2["pair"] = _unordered_pair(e2)
        # within-résumé sigma: SD of fit across draws within resume x condition x gender
        sd = e1.groupby(["resume_ids", "family_code", "gender"])["overall_fit"].std()
        sigma = float(sd.mean())
        entry = {"sigma_within_resume": round(sigma, 2)}
        for con in ["parent", "parent_gap"]:
            gap = float(e1[(e1.family_code == con) & (e1.gender == "female")]["overall_fit"].mean()
                        - e1[(e1.family_code == "none") & (e1.gender == "female")]["overall_fit"].mean())
            pred = float(sps.norm.cdf(gap / (sigma * np.sqrt(2))))
            pm = e2[(e2.contrast == con) & (e2.gender == "female")].copy()
            pm["pc"] = pd.to_numeric(pm["parent_chosen"], errors="coerce")
            obs_pairs = pm.groupby("pair")["pc"].mean()
            obs = float(obs_pairs.mean())
            # bootstrap over pairs: CI for observed - predicted
            diffs = []
            arr = obs_pairs.values
            for _ in range(4000):
                boot = rng.choice(arr, size=len(arr), replace=True).mean()
                diffs.append(boot - pred)
            lo, hi = np.percentile(diffs, [2.5, 97.5])
            entry[con] = {"e1_fit_gap": round(gap, 2),
                          "predicted_P": round(pred, 3), "observed_P": round(obs, 3),
                          "obs_minus_pred": round(obs - pred, 3),
                          "boot_ci95": [round(float(lo), 3), round(float(hi), 3)],
                          "sigma_sensitivity": {s: round(float(sps.norm.cdf(gap / (s * np.sqrt(2)))), 3)
                                                for s in (0.5, 1.0, 2.0) if s}}
        res[k] = entry
    return res


# ---------------- 6b-1 TOST equivalence ----------------
def tost(d: np.ndarray, delta: float) -> dict:
    """Two one-sided tests vs ±delta on pair-level differences; 90% CI."""
    n = len(d)
    se = d.std(ddof=1) / np.sqrt(n)
    t_lo = (d.mean() + delta) / se
    t_hi = (d.mean() - delta) / se
    p_lo = 1 - sps.t.cdf(t_lo, n - 1)
    p_hi = sps.t.cdf(t_hi, n - 1)
    p_tost = max(p_lo, p_hi)
    ci90 = sps.t.ppf(0.95, n - 1) * se
    return {"mean": round(float(d.mean()), 3), "n": int(n),
            "ci90": [round(float(d.mean() - ci90), 3), round(float(d.mean() + ci90), 3)],
            "delta": delta, "tost_p": round(float(p_tost), 4),
            "equivalent_at_delta": bool(p_tost < 0.05)}


def equivalence() -> dict:
    from audit.config import load_occupations_built

    o8_ids = {o.id for o in load_occupations_built().occupations if o.cohort == "o8"}
    res = {}
    for m, k in zip(MODELS, KEYS):
        e2 = _tables_for(m)["e2"]
        o8 = e2[e2.occupation_id.isin(o8_ids)]
        entry = {}
        for con in ["parent", "parent_gap"]:
            a = _pm(o8, "name", con)
            b = _pm(o8, "blind", con)
            common = a.index.intersection(b.index)
            entry[f"blind_minus_names_{con}"] = tost((b[common] - a[common]).values, 0.05)
        # Haiku label vs ±5pp handled in decomposition; Qwen direct parity:
        d = e2[e2.direct]
        pm = {}
        for lvl in ["name", "name_field", "initial_field"]:
            for con in ["gender_none", "gender_parent"]:
                sub = d[(d.cue_level == lvl) & (d.contrast == con)].copy()
                sub["wc"] = pd.to_numeric(sub["woman_chosen"], errors="coerce")
                sub["pair"] = _unordered_pair(sub)
                s = sub.groupby("pair")["wc"].mean() - 0.5
                pm[f"{con}@{lvl}"] = tost(s.values, 0.05)
        entry["direct_parity"] = pm
        res[k] = entry
    return res


# ---------------- 6b-2 model-contrast interactions ----------------
def model_contrasts() -> dict:
    """Paired across the SAME résumé pairs: difference between models of the
    L1-L0 field response (direct gender), and of the mother-father choice gap."""
    res = {}
    dg = {k: _tables_for(m)["e2"] for m, k in zip(MODELS, KEYS)}

    def field_response(k, con):
        e2 = dg[k]
        d = e2[e2.direct & (e2.contrast == con)]
        a = _wm2(d, "name_field")
        b = _wm2(d, "name")
        common = a.index.intersection(b.index)
        return (a[common] - b[common]).rename(k)

    def _wm2(d, lvl):
        s = d[d.cue_level == lvl].copy()
        s["wc"] = pd.to_numeric(s["woman_chosen"], errors="coerce")
        s["pair"] = _unordered_pair(s)
        return s.groupby("pair")["wc"].mean()

    for con in ["gender_none", "gender_parent"]:
        tab = pd.concat([field_response(k, con) for k in KEYS], axis=1).dropna()
        out = {}
        for a, b in [("luna", "qwen"), ("luna", "deepseek"), ("haiku", "qwen"), ("haiku", "deepseek")]:
            d = (tab[a] - tab[b]).values
            t, p = sps.ttest_1samp(d, 0)
            out[f"{a}-{b}"] = {"diff": round(float(d.mean()), 3), "t": round(float(t), 1),
                               "p": round(float(p), 4), "n_pairs": int(len(d))}
        res[f"field_response_{con}"] = out

    # mother-father choice gap between models (main run, parent cue), paired by pair
    mf = {}
    tabs = {k: build_tables(None, model_key=m) for m, k in zip(MODELS, KEYS)}
    gaps = {}
    for k in KEYS:
        e2 = tabs[k]["e2"]
        e2 = e2[~e2.run_id.str.contains("phase3")].copy()
        e2["pair"] = _unordered_pair(e2)
        e2["pc"] = pd.to_numeric(e2["parent_chosen"], errors="coerce")
        f = e2[(e2.contrast == "parent") & (e2.gender == "female")].groupby("pair")["pc"].mean()
        ml = e2[(e2.contrast == "parent") & (e2.gender == "male")].groupby("pair")["pc"].mean()
        gaps[k] = (f - ml).rename(k)
    tab = pd.concat([gaps[k] for k in KEYS], axis=1).dropna()
    for other in ["deepseek", "luna", "qwen"]:
        d = (tab["haiku"] - tab[other]).values
        t, p = sps.ttest_1samp(d, 0)
        mf[f"haiku-{other}"] = {"diff": round(float(d.mean()), 3), "t": round(float(t), 1),
                                "p": round(float(p), 4), "n_pairs": int(len(d))}
    res["mother_father_gap_haiku_vs"] = mf
    return res


# ---------------- 6b-3 wild cluster bootstrap ----------------
def wild_bootstrap(d: np.ndarray, clusters: np.ndarray, n_boot=1999, seed=20261023) -> float:
    """Randomization-ish p-value for mean(d) != 0 via Rademacher cluster flips."""
    rng = np.random.default_rng(seed)
    stat = abs(d.mean())
    u = np.unique(clusters)
    cnt = 0
    for _ in range(n_boot):
        signs = rng.choice([-1.0, 1.0], size=len(u))
        m = dict(zip(u, signs))
        db = d * np.array([m[c] for c in clusters])
        if abs(db.mean()) >= stat:
            cnt += 1
    return (cnt + 1) / (n_boot + 1)


def small_cluster_bootstrap() -> dict:
    from audit.config import load_occupations_built

    res = {}
    o8_ids = {o.id for o in load_occupations_built().occupations if o.cohort == "o8"}
    # O8 label + invariance (16 pairs)
    for m, k in zip(MODELS, KEYS):
        e2 = _tables_for(m)["e2"]
        sub = e2[e2.occupation_id.isin(o8_ids)]
        entry = {}
        for lvl_a, lvl_b, con, tag in [("name", "blind", "parent", "invariance_parent"),
                                       ("name", "blind", "parent_gap", "invariance_gap"),
                                       ("name_field", "name", "parent", "field_parent")]:
            a, b = _pm(sub, lvl_a, con), _pm(sub, lvl_b, con)
            common = a.index.intersection(b.index)
            d = (a[common] - b[common]).values
            clusters = np.array([c.split("|")[0] for c in common])
            entry[tag] = {"t": round(float(sps.ttest_1samp(d, 0).statistic), 1),
                          "wild_p": round(wild_bootstrap(d, clusters), 4)}
        res[k] = entry
    return res


# ---------------- 6b-4 LPM robustness with controls ----------------
def lpm_robustness() -> dict:
    import statsmodels.formula.api as smf

    res = {}
    for m, k in zip(MODELS, KEYS):
        e2 = build_tables(None, model_key=m)["e2"]
        e2 = e2[~e2.run_id.str.contains("phase3")].copy()
        e2["pc"] = pd.to_numeric(e2["parent_chosen"], errors="coerce")
        e2["pair"] = _unordered_pair(e2)
        e2["pos_a_parent"] = ((e2["childless_position"] == "B")).astype(int)
        sub = e2[e2.contrast.isin(["parent", "parent_gap"])].dropna(subset=["pc", "gender"]).reset_index(drop=True)
        sub["pc"] = sub["pc"].astype(float)
        fit = smf.ols("pc ~ C(contrast)*C(gender) + pos_a_parent + C(paraphrase_id)",
                      data=sub).fit(cov_type="cluster", cov_kwds={"groups": sub["pair"].values})
        res[k] = {f"{c}": {"coef": round(float(fit.params[c]), 3), "se": round(float(fit.bse[c]), 3),
                           "t": round(float(fit.tvalues[c]), 1)}
                  for c in fit.params.index if "contrast" in c}
    return res


# ---------------- 6b-8 MDEs ----------------
def mdes() -> dict:
    res = {}
    for k in KEYS:
        s = OUT.get("equivalence", {}).get(k, {})
        row = {}
        for tag, r in s.items():
            if isinstance(r, dict) and "n" in r:
                se = (r["ci90"][1] - r["ci90"][0]) / (2 * sps.t.ppf(0.95, r["n"] - 1))
                row[tag] = round(float(2.8 * se), 3)  # 80% power, two-sided 5%
        res[k] = row
    return res


if __name__ == "__main__":
    OUT["amplification"] = amplification()
    OUT["noise_model2"] = noise_model2()
    OUT["equivalence"] = equivalence()
    OUT["model_contrasts"] = model_contrasts()
    OUT["wild_bootstrap"] = small_cluster_bootstrap()
    OUT["lpm_robustness"] = lpm_robustness()
    OUT["mdes"] = mdes()
    p = ROOT / "docs" / "phase3" / "round6_stats.json"
    p.write_text(json.dumps(OUT, indent=1))
    print(f"wrote {p}")
    print("\n== amplification (cue weight vs quality weight) ==")
    for k in KEYS:
        print(k, json.dumps(OUT["amplification"][k]))
    print("\n== noise model 2 ==")
    for k in KEYS:
        print(k, json.dumps({c: {kk: vv for kk, vv in v.items() if kk != 'sigma_sensitivity'} for c, v in OUT["noise_model2"][k].items() if isinstance(v, dict)}))
    print("\n== TOST equivalence ==")
    for k in KEYS:
        e = OUT["equivalence"][k]
        print(k, {t: (r["ci90"], r["tost_p"], r["equivalent_at_delta"]) for t, r in e.items() if t != "direct_parity"})
    print("qwen direct parity:", {t: (r["ci90"], r["tost_p"]) for t, r in OUT["equivalence"]["qwen"]["direct_parity"].items()})
    print("\n== model contrasts ==")
    print(json.dumps(OUT["model_contrasts"], indent=1))
    print("\n== wild bootstrap ==")
    print(json.dumps(OUT["wild_bootstrap"], indent=1))
