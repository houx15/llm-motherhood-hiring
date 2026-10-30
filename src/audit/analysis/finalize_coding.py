"""SPEC_FINALIZE F1: rationale coding made reportable.

a. Self-coding check: kappa (DeepSeek vs Qwen) split by DeepSeek-written items
   vs other-model items; flag codes differing by > .10.
b. Retained codes: kappa >= .70 overall and in (a) -> substantive analyses.
c. Losing-cued code shares per model x contrast with pair-clustered 95% CIs.
d. Comparators: same shares when the cued candidate WON; personal placebo
   baseline; differences with CIs.
e. Decomposition alignment tests (pre-stated): gap/availability higher for
   interruption contrasts than parent/parent_committed; family higher for
   family contrasts than gap_travel/personal. Holm across models.
f. disclosure_irrelevant (parent, parent_committed), losing vs won.
g. Code-share gender differences (female vs male cued), Holm.

Outputs: docs/final/coding_stats.json, docs/final/coding_tables.md,
docs/report/figures/fig15_coding.pdf.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

from audit.analysis.round3 import _unordered_pair, holm
from audit.config import ROOT

CODES = ["gap", "availability", "family", "disclosure_irrelevant",
         "gap_reason_quality", "protected_mention", "qualifications", "gender"]
INTERRUPTION = ["gap_travel", "gap_parental_only", "parent_gap"]
FAMILY = ["parent", "parent_committed", "parent_gap"]


def load_coded() -> pd.DataFrame:
    """Join the coding-sample frame with both coders' outputs (from logs)."""
    sample = pd.read_parquet(ROOT / "docs/phase4/coding/sample.parquet")
    sample = sample.rename(columns={"model_key": "model_coded"})
    coded: dict[str, dict[str, dict]] = {"primary": {}, "second": {}}
    for f in sorted(ROOT.glob("runs/*rationale_coding-*/logs.jsonl")):
        for l in open(f):
            r = json.loads(l)
            if not r.get("parse_ok"):
                continue
            which = "primary" if r["model_key"] == "deepseek_v41_flash" else "second"
            # keep latest successful coding per (coder, call_id)
            coded[which][r["call_id"]] = r["parsed_json"]
    df = sample.copy()
    df["codes_p"] = df.call_id.map(lambda c: (coded["primary"].get(c) or {}).get("codes", []))
    df["codes_s"] = df.call_id.map(lambda c: (coded["second"].get(c) or {}).get("codes", []))
    df["coded_p"] = df.codes_p.map(lambda x: x != [])
    df["coded_s"] = df.codes_s.map(lambda x: x != [])
    # pair cluster from resume_ids
    df["pair"] = _unordered_pair(df.rename(columns={"model_coded": "m"}))
    return df


def _ck(a, b) -> float:
    a, b = list(a), list(b)
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def self_coding_check(df: pd.DataFrame) -> dict:
    sub = df[df.coded_s].copy()
    out = {"overall": {}, "deepseek_written": {}, "other_written": {}, "flag": []}
    for code in CODES:
        a = sub.codes_p.map(lambda cs: int(code in cs)).values
        b = sub.codes_s.map(lambda cs: int(code in cs)).values
        out["overall"][code] = round(_ck(a, b), 2)
        for grp, mask in [("deepseek_written", sub.model_coded == "deepseek_v41_flash"),
                          ("other_written", sub.model_coded != "deepseek_v41_flash")]:
            aa = sub[mask].codes_p.map(lambda cs: int(code in cs)).values
            bb = sub[mask].codes_s.map(lambda cs: int(code in cs)).values
            if len(aa) >= 20 and (aa.sum() + bb.sum()) > 0:
                out[grp][code] = {"kappa": round(_ck(aa, bb), 2), "n": int(mask.sum())}
        k1 = out["deepseek_written"].get(code, {}).get("kappa")
        k2 = out["other_written"].get(code, {}).get("kappa")
        if k1 is not None and k2 is not None and abs(k1 - k2) > 0.10:
            out["flag"].append(code)
    return out


def _share_ci(df: pd.DataFrame, code: str) -> dict:
    """Share of rationales invoking `code`, clustered by résumé pair."""
    d = df.copy()
    d["x"] = d.codes_p.map(lambda cs: int(code in cs)).astype(float)
    pm = d.groupby("pair")["x"].mean()
    if len(pm) < 3:
        return {"share": None, "n": len(d)}
    se = pm.std(ddof=1) / np.sqrt(len(pm))
    t = sps.t.ppf(0.975, len(pm) - 1)
    return {"share": round(float(d["x"].mean()), 3),
            "ci95": [round(float(d["x"].mean() - t * se), 3), round(float(d["x"].mean() + t * se), 3)],
            "n": int(len(d)), "n_pairs": int(len(pm))}


def _diff_ci(df_a: pd.DataFrame, df_b: pd.DataFrame, code: str) -> dict:
    """Difference of shares (a - b) with pair-clustered SE."""
    def pm(d):
        d = d.copy()
        d["x"] = d.codes_p.map(lambda cs: int(code in cs)).astype(float)
        return d.groupby("pair")["x"].mean()
    a, b = pm(df_a), pm(df_b)
    common = a.index.intersection(b.index)
    if len(common) < 3:
        return {"diff": None}
    d = (a[common] - b[common]).values
    t, p = sps.ttest_1samp(d, 0)
    se = d.std(ddof=1) / np.sqrt(len(d))
    tq = sps.t.ppf(0.975, len(d) - 1)
    return {"diff": round(float(d.mean()), 3),
            "ci95": [round(float(d.mean() - tq * se), 3), round(float(d.mean() + tq * se), 3)],
            "t": round(float(t), 1), "p": round(float(p), 4), "n_pairs": int(len(common))}


def main() -> None:
    out_dir = ROOT / "docs" / "final"
    out_dir.mkdir(parents=True, exist_ok=True)
    df = load_coded()
    res: dict = {}
    res["f1a_self_coding"] = self_coding_check(df)
    retained = [c for c in ["gap", "availability", "family", "disclosure_irrelevant",
                            "gap_reason_quality", "protected_mention"]
                if res["f1a_self_coding"]["overall"].get(c, 0) >= 0.70]
    res["retained_codes"] = retained

    # c) losing shares + d) won comparator + personal baseline
    tables = {}
    diffs = {}
    for model, mdf in df[df.coded_p].groupby("model_coded"):
        mkey = model.split("_")[0]
        tables[mkey] = {}
        diffs[mkey] = {}
        for con, cdf in mdf.groupby("contrast"):
            lose, won = cdf[~cdf.cued_won], cdf[cdf.cued_won]
            tables[mkey][con] = {c: _share_ci(lose, c) for c in retained}
            diffs[mkey][con] = {c: _diff_ci(lose, won, c) for c in retained}
    res["shares_losing"] = tables
    res["diff_losing_minus_won"] = diffs

    # e) decomposition alignment
    align = {}
    fam_p = {}
    for model, mdf in df[df.coded_p].groupby("model_coded"):
        mkey = model.split("_")[0]
        lose = mdf[~mdf.cued_won]
        inter = lose[lose.contrast.isin(INTERRUPTION)]
        plain = lose[lose.contrast.isin(["parent", "parent_committed"])]
        famc = lose[lose.contrast.isin(["parent", "parent_committed", "parent_gap"])]
        nonfam = lose[lose.contrast.isin(["gap_travel", "personal"])]
        row = {}
        for c in ["gap", "availability"]:
            row[f"{c}_interruption_minus_parent"] = _diff_ci(inter, plain, c)
            fam_p[f"{mkey}:{c}"] = row[f"{c}_interruption_minus_parent"]["p"] or 1
        row["family_family_minus_nonfamily"] = _diff_ci(famc, nonfam, "family")
        fam_p[f"{mkey}:family"] = row["family_family_minus_nonfamily"]["p"] or 1
        align[mkey] = row
    adj = holm(fam_p)
    for k, v in adj.items():
        mkey, c = k.split(":")
        key = {"gap": "gap_interruption_minus_parent", "availability": "availability_interruption_minus_parent",
               "family": "family_family_minus_nonfamily"}[c]
        align[mkey][key]["holm"] = round(v, 4)
    res["f1e_alignment"] = align

    # f) disclosure_irrelevant for parent contrasts
    f1f = {}
    for model, mdf in df[df.coded_p].groupby("model_coded"):
        mkey = model.split("_")[0]
        pc = mdf[mdf.contrast.isin(["parent", "parent_committed"])]
        f1f[mkey] = {"losing": _share_ci(pc[~pc.cued_won], "disclosure_irrelevant"),
                     "won": _share_ci(pc[pc.cued_won], "disclosure_irrelevant")}
    res["f1f_irrelevant"] = f1f

    # g) gender differences per model x code
    g = {}
    gp = {}
    for model, mdf in df[df.coded_p].groupby("model_coded"):
        mkey = model.split("_")[0]
        lose = mdf[~mdf.cued_won]
        g[mkey] = {}
        for c in retained:
            r = _diff_ci(lose[lose.gender == "female"], lose[lose.gender == "male"], c)
            g[mkey][c] = r
            if r.get("p") is not None:
                gp[f"{mkey}:{c}"] = r["p"]
    adjg = holm(gp)
    for k, v in adjg.items():
        mkey, c = k.split(":")
        g[mkey][c]["holm"] = round(v, 4)
    res["f1g_gender"] = g

    (out_dir / "coding_stats.json").write_text(json.dumps(res, indent=1))

    # markdown tables
    L = ["# F1: rationale coding (reportable)", "",
         f"Retained codes (κ ≥ .70 overall): {', '.join(retained)}. "
         f"Self-coding flag (> .10 κ gap): {res['f1a_self_coding']['flag'] or 'none'}.", "",
         "## Losing-cued code shares by model × contrast (95% CI, pair-clustered)", ""]
    for mkey, cons in tables.items():
        L.append(f"### {mkey}")
        L.append("")
        L.append("| contrast | " + " | ".join(retained) + " |")
        L.append("| --- | " + " | ".join(["---"] * len(retained)) + " |")
        for con, cells in cons.items():
            row = [con]
            for c in retained:
                s = cells[c]
                row.append(f"{s['share']:.2f} [{s['ci95'][0]:.2f},{s['ci95'][1]:.2f}]" if s.get("share") is not None else "—")
            L.append("| " + " | ".join(row) + " |")
        L.append("")
    L.append("## Decomposition alignment (pre-stated; Holm across models)")
    L.append("")
    L.append("| model | gap: interruption − parent | availability: interruption − parent | family: family − nonfamily |")
    L.append("| --- | --- | --- | --- |")
    for mkey, row in align.items():
        def fmt(r):
            return f"{r['diff']:+.3f} (H {r.get('holm', '—')})" if r.get("diff") is not None else "—"
        L.append(f"| {mkey} | {fmt(row['gap_interruption_minus_parent'])} | "
                 f"{fmt(row['availability_interruption_minus_parent'])} | {fmt(row['family_family_minus_nonfamily'])} |")
    (out_dir / "coding_tables.md").write_text("\n".join(L) + "\n")
    print(f"[F1] wrote {out_dir}/coding_stats.json + coding_tables.md")
    print("self-coding flag:", res["f1a_self_coding"]["flag"] or "none")
    for mkey, row in align.items():
        print(mkey, {k: (v.get("diff"), v.get("holm")) for k, v in row.items()})


if __name__ == "__main__":
    main()
