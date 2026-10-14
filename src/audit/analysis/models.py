"""Regressions (spec §10). For the pilot (2 occupations) we estimate the
family x gender design with résumé FE; occupation-level moderator interactions
need the full 20-occupation Phase 1 run."""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

RATINGS = ["competence", "commitment", "promotability", "likability"]
OUTCOMES = ["overall_fit", "interview", "starting_salary_usd"] + RATINGS


def e1_regressions(e1: pd.DataFrame, outcomes=OUTCOMES) -> pd.DataFrame:
    """Y ~ C(family_code)*female + C(resume_id) + C(name_idx) + C(occupation_id),
    SEs clustered by resume_id. Returns tidy coefficient table."""
    rows = []
    for y in outcomes:
        sub = e1.dropna(subset=[y]).copy()
        if sub.empty:
            continue
        try:
            m = smf.ols(
                f"{y} ~ C(family_code) * C(female) + C(resume_id) + C(name_idx) + C(occupation_id)",
                data=sub,
            ).fit(cov_type="cluster", cov_kwds={"groups": sub["resume_id"]})
        except Exception as e:  # noqa: BLE001
            rows.append({"outcome": y, "error": str(e)[:120]})
            continue
        base = {p: m.params.get(p) for p in m.params.index}
        for term, label in [
            ("C(family_code)[T.married]", "married (men)"),
            ("C(family_code)[T.parent]", "parent (men) = fatherhood effect"),
            ("C(family_code)[T.parent_gap]", "parent_gap (men)"),
            ("C(family_code)[T.parent_committed]", "parent_committed (men)"),
            ("C(family_code)[T.pregnant]", "pregnant (women)"),
        ]:
            if term in base:
                rows.append(_row(m, y, term, label))
        inter = "C(family_code)[T.parent]:C(female)"
        mother = base.get("C(family_code)[T.parent]", np.nan) + base.get(inter, np.nan)
        se_int = m.bse.get(inter, np.nan)
        se_par = m.bse.get("C(family_code)[T.parent]", np.nan)
        c = m.cov_params()
        k1, k2 = "C(family_code)[T.parent]", inter
        if k1 in c.index and k2 in c.index:
            var = c.loc[k1, k1] + c.loc[k2, k2] + 2 * c.loc[k1, k2]
            se = np.sqrt(var)
        else:
            se = np.sqrt(se_par**2 + se_int**2)
        rows.append(
            {
                "outcome": y, "term": "parent (women) = motherhood effect",
                "coef": mother, "se": se, "tstat": mother / se if se else np.nan,
                "pvalue": 2 * (1 - _norm_cdf(abs(mother / se))) if se else np.nan, "n": int(m.nobs),
            }
        )
    return pd.DataFrame(rows)


def _norm_cdf(x):
    from statistics import NormalDist

    return NormalDist().cdf(x)


def _row(m, y, term, label):
    return {
        "outcome": y, "term": label, "coef": m.params[term], "se": m.bse[term],
        "tstat": m.tvalues[term], "pvalue": m.pvalues[term], "n": int(m.nobs),
    }


def e2_analysis(e2: pd.DataFrame) -> dict:
    """Parent-choice logit + paired differences by contrast x gender."""
    res: dict[str, pd.DataFrame] = {}
    sub = e2.dropna(subset=["parent_chosen"]).copy()
    if not sub.empty:
        try:
            m = smf.logit(
                "parent_chosen ~ C(female) + C(contrast) + position_a + C(occupation_id)",
                data=sub,
            ).fit(disp=0)
            res["choice_logit"] = pd.DataFrame(
                {"coef": m.params, "se": m.bse, "pvalue": m.pvalues}
            ).reset_index(names="term")
        except Exception as e:  # noqa: BLE001
            res["choice_logit"] = pd.DataFrame([{"error": str(e)[:200]}])
        rates = (
            sub.groupby(["contrast", "gender"])["parent_chosen"].agg(["mean", "count"]).reset_index()
        )
        res["parent_choice_rates"] = rates
        pos = sub.groupby("position_a")["call_id"].count()
        res["position_bias"] = pd.DataFrame(
            {"share_chosen_A": [pos.get(1, 0) / max(pos.sum(), 1)]}
        )
        diffs = []
        for key in ["diff_starting_salary_usd", "diff_overall_fit", "diff_commitment", "diff_competence"]:
            for (contrast, gender), g in sub.groupby(["contrast", "gender"]):
                v = g[key].dropna()
                if len(v) > 1:
                    t = smf.ols(f"{key} ~ 1", data=g).fit().tvalues["Intercept"]
                    diffs.append(
                        {"metric": key, "contrast": contrast, "gender": gender,
                         "mean_diff_parent_minus_childless": v.mean(), "t": t, "n": len(v)}
                    )
        res["paired_diffs"] = pd.DataFrame(diffs)
    return res


def e3_analysis(e3: pd.DataFrame) -> dict:
    res = {}
    if not e3.empty:
        sel = (
            e3.groupby(["composition", "gender", "family_code"])[["top1", "top3"]]
            .mean()
            .reset_index()
        )
        res["selection_rates"] = sel
        # four-fifths rule: mothers vs childless women (comp a), fathers vs childless men (comp b)
        ratios = []
        for comp, fam, g in [("a", "parent", "female"), ("b", "parent", "male")]:
            sub = e3[e3["composition"] == comp]
            rate = sub.groupby(["family_code", "gender"])["top3"].mean()
            try:
                num = rate.loc[(fam, g)]
                den = rate.loc[("none", g)]
                ratios.append(
                    {"composition": comp, "group": f"{fam} {g}", "top3_rate": num,
                     "childless_rate": den, "impact_ratio": num / den if den else np.nan}
                )
            except KeyError:
                continue
        res["four_fifths"] = pd.DataFrame(ratios)
        # position bias: top-1 by screen label
        res["position_bias"] = e3.groupby("position")[["top1"]].mean().reset_index()
    return res


def diagnostics(diag: pd.DataFrame) -> dict:
    d = {}
    if diag.empty:
        return d
    g = diag.groupby(["experiment", "gender", "family_code"]).agg(
        n=("call_id", "count"),
        parse_ok=("parse_ok", "mean"),
        refusal=("refusal_flag", lambda s: s.fillna(False).mean()),
    )
    d["by_condition"] = g
    kw = ["child", "parent", "family", "pta", "leave", "pregnan", "mother", "father"]
    def kw_rate(text):
        t = str(text or "").lower()
        return any(k in t for k in kw)
    if "rationale" in diag.columns:
        pass
    d["rationale_family_mention"] = diag.assign(
        mentions=diag["parsed_json"].apply(
            lambda p: kw_rate((p or {}).get("rationale")) if isinstance(p, dict) else False
        )
    ).groupby(["experiment", "family_code"])["mentions"].mean()
    return d
