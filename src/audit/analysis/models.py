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


def _find_key(keys, family: str, female: bool, z: str | None):
    """Exact patsy term lookup: right family level, optionally x female, optionally x Z."""
    want = {f"C(family_code)[T.{family}]"}
    if female:
        want.add("C(female)[T.1]")
    if z:
        want.add(z)
    for k in keys:
        parts = k.split(":")
        if len(parts) != len(want):
            continue
        # strip level suffix from C(female)[T.1] for set comparison, keep Z exact
        norm = set()
        for p in parts:
            if p.startswith("C(female)"):
                norm.add("C(female)[T.1]")
            elif p == "Intercept":
                norm.add("Intercept")
            else:
                norm.add(p)
        if norm == want:
            return k
    return None


def e1_moderator_regressions(e1: pd.DataFrame, outcomes=None) -> pd.DataFrame:
    """Spec §10 core model, run separately per standardized occupation moderator Z:

    Y ~ C(family_code) * C(female) * Z + resume FE + name FE, cluster SE by resume.

    Key terms (P = parent indicator):
      - parent x female: how much the motherhood effect differs from the fatherhood
        effect at the occupation mean of Z (H1 vs H2)
      - parent x female x Z: does the mother-minus-father gap grow with Z
        (H3 greedy jobs for Z=time_demands; H4 gender typing for Z=female_share)
    Needs the full 20-occupation grid (Phase 1).
    """
    if outcomes is None:
        outcomes = ["interview", "starting_salary_usd", "commitment", "competence", "overall_fit"]
    rows = []
    order = [c for c in ["none", "married", "parent", "parent_gap", "parent_committed", "pregnant"]
             if c in set(e1["family_code"])]
    zs = {}
    for z in ["female_share", "median_wage", "time_demands"]:
        if z in e1.columns and e1[z].notna().sum() > 15:
            zs[z] = e1[z]
    if e1["occupation_id"].nunique() < 10:
        return pd.DataFrame([{"note": "moderator regressions need >= 10 occupations (Phase 1)"}])
    sub0 = e1.dropna(subset=["family_code"]).copy()
    sub0["family_code"] = pd.Categorical(sub0["family_code"], categories=order)
    for z_name in zs:
        sub = sub0.dropna(subset=[z_name]).copy()
        sub[z_name] = (sub[z_name] - sub[z_name].mean()) / sub[z_name].std(ddof=0)
        for y in outcomes:
            s = sub.dropna(subset=[y]).copy()
            s[y] = s[y].astype(float)
            if s.empty:
                continue
            s["zmod"] = s[z_name]
            zcol = "zmod"
            try:
                m = smf.ols(
                    f"{y} ~ C(family_code) * C(female) * {zcol} + C(resume_ids) + C(name_idx)",
                    data=s,
                ).fit(cov_type="cluster", cov_kwds={"groups": s["resume_ids"]})
            except Exception as e:  # noqa: BLE001
                rows.append({"Z": z_name, "outcome": y, "error": str(e)[:120]})
                continue
            wanted = [
                ("C(family_code)[T.parent]", "fatherhood effect @ mean Z"),
                ("C(family_code)[T.parent_gap]", "parent_gap (men) @ mean Z"),
                ("C(family_code)[T.pregnant]", "pregnant (women) @ mean Z"),
            ]
            for pat, label in wanted:
                if pat in m.params.index:
                    r = _row(m, y, pat, label)
                    r["Z"] = z_name
                    rows.append(r)
            zcol = "zmod"
            inter_specs = [
                (True, None, "mother-minus-father gap @ mean Z"),
                (False, zcol, "fatherhood x Z"),
                (True, zcol, "mother-minus-father gap x Z (H3/H4)"),
            ]
            if any(f == "parent_gap" for f in s["family_code"].unique()):
                inter_specs.append(("gap", zcol, "parent_gap gender gap x Z"))
            for spec in inter_specs:
                if spec[0] == "gap":
                    k = _find_key(m.params.index, "parent_gap", True, zcol)
                else:
                    k = _find_key(m.params.index, "parent", spec[0], spec[1])
                if k:
                    r = _row(m, y, k, spec[2])
                    r["Z"] = z_name
                    rows.append(r)
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
