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
    """Y ~ C(family_code)*C(female) + resume FE + name FE + occupation FE,
    SEs clustered by resume. Returns tidy coefficient table."""
    rows = []
    order = [c for c in ["none", "married", "parent", "parent_gap", "parent_committed", "pregnant"]
             if c in set(e1["family_code"])]
    sub0 = e1.dropna(subset=["family_code"]).copy()
    sub0["family_code"] = pd.Categorical(sub0["family_code"], categories=order)
    for y in outcomes:
        sub = sub0.dropna(subset=[y]).copy()
        sub[y] = sub[y].astype(float)
        if sub.empty:
            continue
        try:
            m = smf.ols(
                f"{y} ~ C(family_code) * C(female) + C(resume_ids) + C(name_idx) + C(occupation_id)",
                data=sub,
            ).fit(cov_type="cluster", cov_kwds={"groups": sub["resume_ids"]})
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
        k_par = "C(family_code)[T.parent]"
        k_inter_candidates = [k for k in m.params.index if "T.parent]" in k and ":C(female)" in k]
        if k_par in base and k_inter_candidates:
            k_inter = k_inter_candidates[0]
            mother = base[k_par] + base.get(k_inter, np.nan)
            c = m.cov_params()
            if k_par in c.index and k_inter in c.index:
                var = c.loc[k_par, k_par] + c.loc[k_inter, k_inter] + 2 * c.loc[k_par, k_inter]
                se = float(np.sqrt(var))
            else:
                se = np.nan
            rows.append(
                {
                    "outcome": y, "term": "parent (women) = motherhood effect",
                    "coef": mother, "se": se, "tstat": mother / se if se else np.nan,
                    "pvalue": 2 * (1 - _norm_cdf(abs(mother / se))) if se else np.nan, "n": int(m.nobs),
                }
            )
    df = pd.DataFrame(rows)
    if "error" in df.columns and df["error"].notna().all():
        return df
    return df[df.get("error", pd.Series(index=df.index, dtype=object)).isna()]


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
