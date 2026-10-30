"""Final statistics for the report — implements REVIEW_NOTES.md rounds 1 & 2.

Everything the report cites is computed here, dumped to docs/report/stats.json, and
emitted as markdown tables to docs/report/tables.md (no hand-typed numbers).
Run via `uv run audit stats`.

Round-2 additions:
  - R2-1: pregnancy interview/fit gaps with résumé FE + clustered SEs; interview
    rates by withheld status (abstention coincides with interview denial)
  - R2-2: Tables 1-4 emitted programmatically
  - R2-3: E4 clustered difference-in-differences (variant x parent_gap, résumé FE,
    32 résumé clusters)
  - R2-4: moderator regressions re-run with withheld ($0) salaries excluded
  - Holm correction across the 12 E2 gender-difference tests
  - named-résumé sensitivity incl. registered_nurse_01 / medical_assistant_01
"""
import json

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from audit.analysis.build_tables import build_tables
from audit.analysis.models import e1_moderator_regressions
from audit.analysis.stats import meta_summary

MODELS = ["deepseek_v41_flash", "claude_haiku_55", "gpt6_luna", "qwen38_flash"]
OUT = {}


def pair_cluster(e2: pd.DataFrame) -> pd.Series:
    """Cluster id = occupation x resume pair (40 clusters)."""
    import re

    def pid(row):
        idxs = sorted(re.search(r"_(\d+)$", r).group(1) for r in str(row["resume_ids"]).split("+"))
        return f"{row['occupation_id']}|{'-'.join(idxs)}"
    return e2.apply(pid, axis=1)


def e2_clustered(e2: pd.DataFrame) -> dict:
    """MUST 3/4: cluster-level inference — aggregate P(parent chosen) to the 40
    résumé-pair clusters, then t-tests vs 0.5 (conservative, no sandwich
    degeneracy with few clusters). Gender differences via pair-matched t-tests."""
    from scipy import stats as sps

    d = e2[~e2.run_id.str.contains("phase3|phase4")].copy()  # main run only
    d["parent_chosen"] = pd.to_numeric(d["parent_chosen"], errors="coerce")
    d = d.dropna(subset=["parent_chosen"])
    d["cell"] = d["contrast"].astype(str) + "|" + d["gender"].astype(str)
    d["cluster"] = pair_cluster(d)
    cells = {}
    cl_means = {}
    for cell in d["cell"].unique():
        g = d[d["cell"] == cell]
        agg = g.groupby("cluster")["parent_chosen"].mean()
        cl_means[cell] = agg
        t, p = sps.ttest_1samp(agg, 0.5)
        cells[cell] = {
            "p": round(float(agg.mean()), 3),
            "se": round(float(agg.std(ddof=1) / np.sqrt(len(agg))), 4),
            "z_vs_half": round(float(t), 1),
            "pvalue": float(p),
            "n_clusters": int(len(agg)),
        }
    diffs = {}
    for contrast in ["parent", "parent_committed", "parent_gap"]:
        kf, km = f"{contrast}|female", f"{contrast}|male"
        if kf in cl_means and km in cl_means:
            j = pd.concat([cl_means[kf].rename("f"), cl_means[km].rename("m")], axis=1).dropna()
            dd = j["f"] - j["m"]
            t, p = sps.ttest_1samp(dd, 0.0)
            diffs[contrast] = {
                "mothers_minus_fathers": round(float(dd.mean()), 3),
                "se": round(float(dd.std(ddof=1) / np.sqrt(len(dd))), 4),
                "z": round(float(t), 1),
                "p": round(float(p), 4),
                "n_clusters": int(len(dd)),
            }
    return {"cells": cells, "gender_diff": diffs, "n_clusters": int(d["cluster"].nunique())}


def e2_strict_qwen(e2_all: pd.DataFrame) -> dict:
    """MUST 5: Qwen E2 means using strict validity only (drop repaired call_ids)."""
    import glob

    repaired = set()
    for f in glob.glob("runs/*/logs.jsonl"):
        for line in open(f):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("repair_of") and r.get("model_key") == "qwen38_flash":
                repaired.add(r["repair_of"])
    d = e_all = e2_all[~e2_all["call_id"].isin(repaired)]
    out = {}
    for contrast in ["parent", "parent_gap"]:
        for g in ["female", "male"]:
            sub = d[(d.contrast == contrast) & (d.gender == g)]
            out[f"{contrast}_{g}"] = round(float(sub["parent_chosen"].mean()), 3)
    out["dropped_calls"] = int(e2_all["call_id"].isin(repaired).sum())
    return out


def withheld_stats(e1: pd.DataFrame, label: str) -> dict:
    """MUST 1: salary withholding by condition (women only reported + men none)."""
    d = e1.copy()
    d["withheld"] = (d["starting_salary_usd"].fillna(0) == 0).astype(int)
    tab = d.groupby(["gender", "family_code"])["withheld"].mean()
    sal = d[d["withheld"] == 0].groupby(["gender", "family_code"])["starting_salary_usd"].mean()
    return {
        "rates": {f"{g}|{f}": round(float(v), 4) for (g, f), v in tab.items()},
        "nonzero_means": {f"{g}|{f}": round(float(v)) for (g, f), v in sal.items()},
    }


def pregnancy_effect_excl_zeros(e1: pd.DataFrame) -> dict:
    d = e1[(e1.gender == "female")].copy()
    d["withheld"] = d["starting_salary_usd"].fillna(0) == 0
    nz = d[~d["withheld"]]
    piv = nz.pivot_table(index="resume_ids", columns="family_code",
                         values="starting_salary_usd", aggfunc="mean")
    paired = (piv["pregnant"] - piv["none"]).dropna()
    none_mean = nz[nz.family_code == "none"]["starting_salary_usd"].mean()
    fit = d.groupby("family_code")["overall_fit"].mean()
    interview = d.groupby("family_code")["interview"].mean()
    preg_rows = d[d.family_code == "pregnant"]
    return {
        "paired_gap_excl_withheld_usd": round(float(paired.mean())),
        "paired_gap_pct": round(100 * float(paired.mean()) / none_mean, 2),
        "paired_n_resumes": int(len(paired)),
        "unconditional_gap_excl_withheld_usd": round(
            float(nz[nz.family_code == "pregnant"]["starting_salary_usd"].mean()
                  - nz[nz.family_code == "none"]["starting_salary_usd"].mean())),
        "naive_gap_with_zeros_usd": round(
            float(d[d.family_code == "pregnant"]["starting_salary_usd"].fillna(0).mean()
                  - d[d.family_code == "none"]["starting_salary_usd"].fillna(0).mean())),
        "withheld_pregnant": round(float(preg_rows["withheld"].mean()), 4),
        "withheld_none": round(float(d[d.family_code == "none"]["withheld"].mean()), 4),
        "fit_pregnant_minus_none": round(float(fit["pregnant"] - fit["none"]), 3),
        "interview_pregnant": round(float(interview["pregnant"]), 4),
        "interview_none": round(float(interview["none"]), 4),
        "interview_false_share_pregnant": round(
            float((d[d.family_code == "pregnant"]["interview"] == False).mean()), 4),
    }


def e3_fe_ratio(e3: pd.DataFrame) -> dict:
    """MUST 2: token-parent effect with resume FE, per gender; naive + adjusted."""
    res = {}
    ab = e3[e3["composition"].isin(["a", "b"])].copy()
    ab["parent"] = (ab["family_code"] == "parent").astype(int)
    ab["resume_num"] = ab["resume_id"].str[-2:].astype(int)
    for comp, g, tag in [("a", "female", "F"), ("b", "male", "M")]:
        sub = ab[(ab["composition"] == comp) & (ab["gender"] == g)].copy()
        if sub.empty:
            continue
        m = smf.ols(
            "top3 ~ parent + C(resume_id) + C(position)", data=sub
        ).fit(cov_type="cluster", cov_kwds={"groups": sub["occupation_id"]})
        gap = float(m.params["parent"])
        gap_se = float(m.bse["parent"])
        # FE-adjusted childless anchor for resumes 0-3 (they appear in both roles)
        core = sub[sub["resume_num"] < 4]
        anchor = float(core[core["parent"] == 0]["top3"].mean())
        naive_parent = float(sub[sub["parent"] == 1]["top3"].mean())
        naive_child = float(sub[sub["parent"] == 0]["top3"].mean())
        res[tag] = {
            "fe_gap": round(gap, 4), "fe_se": round(gap_se, 4),
            "fe_z": round(gap / gap_se, 1),
            "anchor_childless_core": round(anchor, 4),
            "adjusted_ratio": round((anchor + gap) / anchor, 3) if anchor else None,
            "naive_ratio": round(naive_parent / naive_child, 3),
        }
    # extras vs base childless quality check (SHOULD in MUST 2)
    childless = ab[ab["parent"] == 0]
    res["childless_top3_base_0_3"] = round(
        float(childless[childless["resume_num"] < 4]["top3"].mean()), 3)
    res["childless_top3_extras_4_5"] = round(
        float(childless[childless["resume_num"] >= 4]["top3"].mean()), 3)
    # comp c parent effect with FE (roles rotate)
    c = e3[e3["composition"] == "c"].copy()
    c["parent"] = (c["family_code"] == "parent").astype(int)
    m = smf.ols("top3 ~ parent + C(resume_id) + C(position)", data=c).fit(
        cov_type="cluster", cov_kwds={"groups": c["occupation_id"]})
    res["compc_fe_gap"] = round(float(m.params["parent"]), 4)
    res["compc_fe_z"] = round(float(m.params["parent"] / m.bse["parent"]), 1)
    return res


def lowfit_sensitivity(tables, e2_by_model, e3_by_model) -> dict:
    """SHOULD 7 + R2-SHOULD: exclude weak résumés (fit<4 cut AND named set incl.
    registered_nurse_01 / medical_assistant_01)."""
    fits = []
    for m in MODELS:
        e1 = tables[m]["e1"]
        f = e1.groupby("resume_ids")["overall_fit"].mean().rename(m)
        fits.append(f)
    fit_df = pd.concat(fits, axis=1).mean(axis=1)
    low = sorted(fit_df[fit_df < 4.0].index.tolist())
    named = sorted(set(low) | {"registered_nurse_01", "medical_assistant_01"})
    out = {
        "lowfit_resumes": low,
        "lowfit_mean_fit": {r: round(float(fit_df[r]), 2) for r in named},
        "named_exclusion_set": named,
    }

    def sens_run(exclude):
        e2s, e3s = {}, {}
        for m in MODELS:
            e2 = e2_by_model[m]
            mask = ~e2["resume_ids"].apply(lambda s: any(r in s for r in exclude))
            row = {}
            for contrast in ["parent", "parent_gap"]:
                for g in ["female", "male"]:
                    sub = e2[mask & (e2.contrast == contrast) & (e2.gender == g)]
                    row[f"{contrast}_{g}"] = round(float(sub["parent_chosen"].mean()), 3)
            e2s[m] = row
            e3 = e3_by_model[m]
            m3 = ~e3["resume_id"].isin(exclude)
            for comp, g, tag in [("a", "female", "F"), ("b", "male", "M")]:
                sub = e3[m3 & (e3.composition == comp) & (e3.gender == g)]
                rate = sub.groupby("family_code")["top3"].mean()
                try:
                    e3s[f"{m}_{tag}"] = round(rate.loc["parent"] / rate.loc["none"], 3)
                except KeyError:
                    pass
        return {"e2": e2s, "e3_ratios": e3s}

    out["sensitivity_fitcut"] = sens_run(low)
    out["sensitivity_named"] = sens_run(named)
    return out


def pregnancy_full(e1: pd.DataFrame) -> dict:
    """R2-1: pregnancy gaps on interview & fit with résumé FE + clustered SEs,
    plus the withheld-x-interview crosstab (abstention denies interviews)."""
    from scipy import stats as sps

    d = e1[e1.gender == "female"].copy()
    d["withheld"] = (d["starting_salary_usd"].fillna(0) == 0).astype(int)
    d["pregnant"] = (d["family_code"] == "pregnant").astype(float)
    sub = d[d["family_code"].isin(["none", "pregnant"])].copy()
    out = {}
    for y in ["interview", "overall_fit", "competence", "commitment"]:
        sub[y] = sub[y].astype(float)
        m = smf.ols(
            f"{y} ~ pregnant + C(resume_ids) + C(name_idx)", data=sub
        ).fit(cov_type="cluster", cov_kwds={"groups": sub["resume_ids"]})
        c, s = float(m.params["pregnant"]), float(m.bse["pregnant"])
        out[y] = {"coef": round(c, 4), "se": round(s, 4), "t": round(c / s, 1)}
    out["interview_rate_none"] = round(float(d[d.family_code == "none"]["interview"].mean()), 4)
    out["interview_rate_pregnant"] = round(float(d[d.family_code == "pregnant"]["interview"].mean()), 4)
    # withheld x interview crosstab
    ct = d[d.family_code.isin(["none", "pregnant", "married"])].groupby(
        ["family_code", "withheld"]
    )["interview"].agg(["mean", "count"])
    out["interview_by_withheld"] = {
        f"{f}|{'withheld' if w else 'offered'}": {"rate": round(float(r["mean"]), 3), "n": int(r["count"])}
        for (f, w), r in ct.iterrows()
    }
    return out


def e4_did(e4: pd.DataFrame) -> dict:
    """R2-3: clustered DiD — interview ~ jd_variant x parent_gap (+ résumé & name FE),
    SEs clustered by résumé (32 clusters). DiD(v) = extra leave-gap penalty under
    variant v relative to base."""
    d = e4[e4["family_code"].isin(["none", "parent_gap"])].copy()
    d["gapflag"] = (d["family_code"] == "parent_gap").astype(float)
    order = ["base", "eeo", "family_friendly", "greedy", "greedy_ff"]
    d["jd_variant"] = pd.Categorical(d["jd_variant"], categories=order)
    res = {}
    for gender in ["female", "male"]:
        sub = d[d["gender"] == gender].copy()
        sub["interview"] = sub["interview"].astype(float)
        m = smf.ols(
            "interview ~ C(jd_variant) * gapflag + C(resume_ids) + C(name_idx)",
            data=sub,
        ).fit(cov_type="cluster", cov_kwds={"groups": sub["resume_ids"]})
        base_gap = float(m.params["gapflag"])
        base_se = float(m.bse["gapflag"])
        row = {
            "base_gap_pp": round(100 * base_gap, 2),
            "base_se_pp": round(100 * base_se, 2),
            "base_t": round(base_gap / base_se, 1),
            "did": {}, "gap_by_variant": {},
        }
        for v in order[1:]:
            k = f"C(jd_variant)[T.{v}]:gapflag"
            c, s = float(m.params[k]), float(m.bse[k])
            row["did"][v] = {
                "pp": round(100 * c, 2), "se_pp": round(100 * s, 2), "t": round(c / s, 1),
                "total_gap_pp": round(100 * (base_gap + c), 2),
            }
        res[gender] = row
    return res


def holm(pvals: dict) -> dict:
    """Holm-Bonferroni adjusted p-values."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj = {}
    running = 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, (m - i) * p)
        adj[k] = min(1.0, running)
    return adj


def e1_outcome_gaps(e1: pd.DataFrame) -> dict:
    """SHOULD 10: fit + commitment cell gaps (women), salary excl withheld."""
    d = e1.copy()
    d.loc[d["starting_salary_usd"].fillna(0) == 0, "starting_salary_usd"] = np.nan
    out = {}
    for y in ["overall_fit", "commitment", "starting_salary_usd", "interview"]:
        cell = d[d.gender == "female"].groupby("family_code")[y].mean()
        out[y] = {
            "parent_minus_none": round(float(cell["parent"] - cell["none"]), 3),
            "parent_gap_minus_none": round(float(cell["parent_gap"] - cell["none"]), 3),
            "pregnant_minus_none": round(float(cell["pregnant"] - cell["none"]), 3),
        }
    return out


SHORTM = {"deepseek_v41_flash": "DeepSeek", "claude_haiku_55": "Haiku",
          "gpt6_luna": "Luna", "qwen38_flash": "Qwen"}


def _stars(t):
    return "***" if abs(t) > 3.3 else ("**" if abs(t) > 2.6 else ("*" if abs(t) > 2.0 else ""))


def emit_tables(out: dict) -> str:
    """R2-2: emit every report table as markdown from the stats dict."""
    L = []
    models = out["models"]

    L.append("### Table 1. E2 probability the parent candidate is chosen "
             "(mean of 40 résumé-pair cluster means; t vs 0.5, df 39)\n")
    L.append("| Contrast | DeepSeek F / M | Haiku F / M | Luna F / M | Qwen F / M |")
    L.append("| --- | --- | --- | --- | --- |")
    rows = {"parent": "Parent (PTA)", "parent_committed": "Parent + committed", "parent_gap": "Parent + leave gap"}
    for contrast, label in rows.items():
        cells = []
        for m in MODELS:
            c = models[m]["e2_clustered"]["cells"]
            f, mle = c[f"{contrast}|female"], c[f"{contrast}|male"]
            cells.append(f".{round(f['p']*1000):03d} ({f['z_vs_half']:.0f}){'' if contrast=='parent' else ''} / "
                         f".{round(mle['p']*1000):03d} ({mle['z_vs_half']:.0f})")
        L.append(f"| {label} | " + " | ".join(cells) + " |")

    L.append("\n### Table 2. E2 mother-minus-father differences (pair-matched t-tests; Holm over 12 tests)\n")
    L.append("| Contrast | DeepSeek | Haiku | Luna | Qwen |")
    L.append("| --- | --- | --- | --- | --- |")
    holm = out["gender_diff_holm"]
    for contrast, label in rows.items():
        cells = []
        for m in MODELS:
            g = models[m]["e2_clustered"]["gender_diff"][contrast]
            adj = holm[f"{m}|{contrast}"]
            mark = "**" if g["p"] < 0.05 and adj < 0.05 else ("*" if g["p"] < 0.05 else "")
            holm_note = f"; Holm p={adj:.3f}" if g["p"] < 0.05 else ""
            cells.append(f"{g['mothers_minus_fathers']:+.3f} (t {g['z']:.1f}{holm_note}){mark}")
        L.append(f"| {label} | " + " | ".join(cells) + " |")

    L.append("\n### Table 3. E3 top-3 impact ratios for token parents (naïve → résumé-FE adjusted; FE t)\n")
    L.append("| | DeepSeek | Haiku | Luna | Qwen |")
    L.append("| --- | --- | --- | --- | --- |")
    for g, label in [("F", "Mothers"), ("M", "Fathers")]:
        cells = []
        for m in MODELS:
            r = models[m]["e3_fe"][g]
            cells.append(f".{r['naive_ratio']*1000:.0f} → **.{r['adjusted_ratio']*1000:.0f}** ({r['fe_z']:.1f})")
        L.append(f"| {label} | " + " | ".join(cells) + " |")

    L.append("\n### Table 4. E4 leave-gap interview penalty (pp; résumé-FE DiD vs base, 32 résumé clusters)\n")
    L.append("| | DeepSeek F / M | Haiku F / M | Luna F / M | Qwen F / M |")
    L.append("| --- | --- | --- | --- | --- |")
    variants = ["base", "eeo", "family_friendly", "greedy", "greedy_ff"]
    vlabel = {"base": "Base (gap)", "eeo": "EEO (DiD)", "family_friendly": "Family-friendly (DiD)",
              "greedy": "Greedy (DiD)", "greedy_ff": "Greedy+FF (DiD)"}
    for v in variants:
        cells = []
        for m in MODELS:
            d = models[m]["e4_did"]
            def fmt(g):
                if v == "base":
                    r = d[g]
                    return f"{r['base_gap_pp']:+.1f} (t {r['base_t']:.1f})"
                r = d[g]["did"][v]
                return f"{r['pp']:+.1f} (t {r['t']:.1f}){_stars(r['t'])}"
            cells.append(f"{fmt('female')} / {fmt('male')}")
        L.append(f"| {vlabel[v]} | " + " | ".join(cells) + " |")

    L.append("\n### Table 5. Pregnancy within-résumé gaps (résumé FE, clustered SE)\n")
    L.append("| Outcome | DeepSeek | Haiku | Luna | Qwen |")
    L.append("| --- | --- | --- | --- | --- |")
    for y, label in [("interview", "Interview (pp)"), ("overall_fit", "Fit (points)"),
                     ("competence", "Competence"), ("commitment", "Commitment")]:
        cells = []
        for m in MODELS:
            r = models[m]["pregnancy_full"][y]
            mult = 100 if y == "interview" else 1
            cells.append(f"{mult*r['coef']:+.1f} (t {r['t']:.1f}){_stars(r['t'])}")
        L.append(f"| {label} | " + " | ".join(cells) + " |")

    L.append("\n### Table 6. Salary withholding ($0) and interview denial, E1 women\n")
    L.append("| Model | withheld: none | pregnant | married | interview: pregnant|withheld | pregnant|offered |")
    L.append("| --- | --- | --- | --- | --- | --- |")
    for m in MODELS:
        w = models[m]["withheld"]["rates"]
        pf = models[m]["pregnancy_full"]["interview_by_withheld"]
        iw = lambda key: f"{pf[key]['rate']:.3f} (n={pf[key]['n']})" if key in pf else "—"
        L.append(f"| {SHORTM[m]} | {100*w.get('female|none',0):.1f}% | {100*w.get('female|pregnant',0):.1f}% "
                 f"| {100*w.get('female|married',0):.1f}% | {iw('pregnant|withheld')} | {iw('pregnant|offered')} |")
    return "\n".join(L) + "\n"


def main():
    tables = {m: build_tables(None, model_key=m) for m in MODELS}
    # report_stats computes MAIN-RUN statistics (its charter); phase-3/4 have
    # their own modules (cross_model, phase3_key_stats, round3/5/6, phase4_stats)
    for m in MODELS:
        for k in ("e1", "e2", "e3", "e4", "e1_e4"):
            if k in tables[m] and "run_id" in tables[m][k].columns:
                tables[m][k] = tables[m][k][~tables[m][k].run_id.str.contains("phase3|phase4")].copy()
        if "e2" in tables[m]:
            tables[m]["e2"]["parent_chosen"] = pd.to_numeric(tables[m]["e2"]["parent_chosen"], errors="coerce")
    per_model = {}
    for m in MODELS:
        t = tables[m]
        s = {}
        s["e2_clustered"] = e2_clustered(t["e2"])
        s["withheld"] = withheld_stats(t["e1"], m)
        s["pregnancy"] = pregnancy_effect_excl_zeros(t["e1"])
        s["e3_fe"] = e3_fe_ratio(t["e3"])
        s["e1_gaps_women"] = e1_outcome_gaps(t["e1"])
        # paired salary diffs (nonzero only)
        e2 = t["e2"]
        for contrast in ["parent", "parent_gap"]:
            sub = e2[(e2.contrast == contrast) & (e2.gender == "female")].copy()
            sal_cols = [c for c in sub.columns if c.startswith(("A.starting", "B.starting"))]
            diff = sub["diff_starting_salary_usd"]
            base = sub[sal_cols].mean().mean()
            s[f"e2_{contrast}_salary_f"] = {
                "diff": round(float(diff.mean())),
                "pct": round(100 * float(diff.mean()) / base, 2),
                "base": round(float(base)),
            }
        # E4 leave-gap interview gaps by JD variant
        e4 = t.get("e4")
        if e4 is not None and not e4.empty:
            cell4 = e4.groupby(["jd_variant", "gender", "family_code"])["interview"].mean()
            gaps4 = {}
            for v in ["base", "eeo", "family_friendly", "greedy", "greedy_ff"]:
                try:
                    gaps4[v] = {
                        "F": round(100 * float(cell4.loc[(v, "female", "parent_gap")] - cell4.loc[(v, "female", "none")]), 2),
                        "M": round(100 * float(cell4.loc[(v, "male", "parent_gap")] - cell4.loc[(v, "male", "none")]), 2),
                    }
                except KeyError:
                    pass
            s["e4_gaps_pp"] = gaps4
        per_model[m] = s

    # meta-analysis with clustered SEs (mothers, parent & gap)
    for key, tag in [("e2_clustered", "parent"), ("e2_clustered", "parent_gap")]:
        effs = []
        for m in MODELS:
            c = per_model[m]["e2_clustered"]["cells"][f"{tag}|female"]
            effs.append((c["p"], c["se"]))
        pooled, se, z, i2 = meta_summary(effs)
        OUT[f"meta_{tag}_female"] = {
            "pooled_p": round(pooled, 3), "se": round(se, 4), "z": round(z, 1),
            "i2_pct": round(i2, 1),
            "per_model": {m: per_model[m]["e2_clustered"]["cells"][f"{tag}|female"] for m in MODELS},
        }

    OUT["qwen_strict"] = e2_strict_qwen(tables["qwen38_flash"]["e2"])
    OUT["lowfit"] = lowfit_sensitivity(
        tables, {m: tables[m]["e2"] for m in MODELS}, {m: tables[m]["e3"] for m in MODELS})

    # R2-1: pregnancy interview/fit gaps + withheld crosstab
    for m in MODELS:
        per_model[m]["pregnancy_full"] = pregnancy_full(tables[m]["e1"])

    # R2-3: E4 clustered DiD
    for m in MODELS:
        per_model[m]["e4_did"] = e4_did(tables[m]["e4"])

    # R2-SHOULD: Holm correction across the 12 gender-difference tests
    raw = {}
    for m in MODELS:
        for contrast, v in per_model[m]["e2_clustered"]["gender_diff"].items():
            raw[f"{m}|{contrast}"] = v["p"]
    OUT["gender_diff_holm"] = holm(raw)

    # R2-4: moderators re-run with withheld ($0) salaries excluded
    mods = {}
    for m in MODELS:
        e1 = tables[m]["e1"].copy()
        e1.loc[e1["starting_salary_usd"].fillna(0) == 0, "starting_salary_usd"] = np.nan
        r = e1_moderator_regressions(e1)
        if "note" not in r.columns:
            key = r[
                r["term"].isin(
                    ["mother-minus-father gap @ mean Z", "mother-minus-father gap x Z (H3/H4)",
                     "parent_gap gender gap @ mean Z", "parent_gap gender gap x Z",
                     "fatherhood effect @ mean Z", "fatherhood x Z"]
                )
            ]
            mods[m] = [
                {"Z": row.Z, "outcome": row.outcome, "term": row.term,
                 "coef": round(row.coef, 4), "se": round(row.se, 4), "p": round(row.pvalue, 4)}
                for _, row in key.iterrows()
            ]
    OUT["moderators"] = mods
    OUT["models"] = {m: per_model[m] for m in MODELS}

    with open("docs/report/stats.json", "w") as f:
        json.dump(OUT, f, indent=1, default=str)
    with open("docs/report/tables.md", "w") as f:
        f.write(emit_tables(OUT))
    print("[stats] wrote docs/report/stats.json + docs/report/tables.md")

    # console summary
    print("=== E2 clustered (mothers | fathers, z) ===")
    for m in MODELS:
        c = per_model[m]["e2_clustered"]["cells"]
        print(f"{m}: parent {c['parent|female']['p']}({c['parent|female']['z_vs_half']}) | {c['parent|male']['p']}({c['parent|male']['z_vs_half']})"
              f"  gap {c['parent_gap|female']['p']}({c['parent_gap|female']['z_vs_half']}) | {c['parent_gap|male']['p']}({c['parent_gap|male']['z_vs_half']})")
    print("=== gender diffs (F-M, z) ===")
    for m in MODELS:
        g = per_model[m]["e2_clustered"]["gender_diff"]
        print(m, {k: (v["mothers_minus_fathers"], v["z"]) for k, v in g.items()})
    print("=== meta ===", {k: (v["pooled_p"], v["z"], v["i2_pct"]) for k, v in OUT.items() if k.startswith("meta")})
    print("=== E3 FE ratios (naive -> adjusted) ===")
    for m in MODELS:
        r = per_model[m]["e3_fe"]
        print(m, "F:", r["F"]["naive_ratio"], "->", r["F"]["adjusted_ratio"], f"(z={r['F']['fe_z']})",
              "| M:", r["M"]["naive_ratio"], "->", r["M"]["adjusted_ratio"], f"(z={r['M']['fe_z']})",
              "| extras vs base:", r["childless_top3_base_0_3"], r["childless_top3_extras_4_5"])
    print("=== pregnancy excl withheld ===")
    for m in MODELS:
        p = per_model[m]["pregnancy"]
        print(m, "paired excl withheld:", p["paired_gap_excl_withheld_usd"], f"({p['paired_gap_pct']}%)", "withheld:", p["withheld_pregnant"])
    print("=== lowfit ===", OUT["lowfit"]["lowfit_resumes"])
    print("=== qwen strict ===", OUT["qwen_strict"])
    print("=== comp c FE gap ===", {m: per_model[m]["e3_fe"]["compc_fe_gap"] for m in MODELS})


if __name__ == "__main__":
    main()
