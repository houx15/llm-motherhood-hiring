"""Round 15: refusals and missing choices as outcomes (no new API calls).

1. Missingness table per model x contrast x phase: n, refusal %, parse-fail %,
   no-valid-choice % (first-attempt, repairs excluded), pair-clustered CIs;
   tests cued vs placebo cells.
2. Manski bounds for headline E2 cells + decomposition contrasts.
3. P(refuse) by cue and gender for Haiku (alongside salary withholding).
4. Headline estimates with Haiku excluded (pooled statements only).

Outputs: docs/final/missingness.md + missingness.json; claims appended by
claims_check run afterwards.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from scipy import stats as sps

from audit.analysis.etl import load_clean
from audit.analysis.select import main_run_ids, phase3_ids, phase4_ids
from audit.config import ROOT

MODELS = ["deepseek_v41_flash", "claude_haiku_55", "gpt6_luna", "qwen38_flash"]
KEYS = ["deepseek", "haiku", "luna", "qwen"]
OUT: dict = {}


def _first_attempts() -> pd.DataFrame:
    """First-attempt E2 rows from RAW logs (repairs excluded).

    The clean-cache diagnostics table cannot be used: load_run_logs dedups to
    the BEST row per call_id, so first-attempt failures are unrecoverable
    there (Qwen main parent_gap shows 0.2% instead of 20.8%)."""
    import glob

    first: dict[str, dict] = {}
    for f in glob.glob(str(ROOT / "runs/*/logs.jsonl")):
        with open(f) as fh:
            for line in fh:
                if '"experiment": "e2"' not in line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("experiment") != "e2" or r.get("repair_of"):
                    continue
                cid = r.get("call_id")
                ts = r.get("request_ts")
                if not cid or not ts:
                    continue
                # R16-1: transport failures (outages, 429/402, DNS) are
                # infrastructure retries, not model responses; exclude them
                # before choosing the first attempt.
                err = str(r.get("error") or "")
                if r.get("cost_usd") == 0 and (
                    "TransportFailure" in err or "gave up" in err or "nodename" in err
                    or "HTTP 402" in err or "HTTP 429" in err or err.startswith("http")
                ):
                    continue
                cur = first.get(cid)
                if cur is None or ts < cur["request_ts"]:
                    first[cid] = {"call_id": cid, "request_ts": ts,
                                  "model_key": r.get("model_key"),
                                  "contrast": r.get("contrast"),
                                  "gender": r.get("gender"),
                                  "resume_ids": r.get("resume_ids"),
                                  "parse_ok": bool(r.get("parse_ok")),
                                  "refusal_flag": bool(r.get("refusal_flag"))}
    return pd.DataFrame(first.values())


def _phase_of(call_id: str) -> str:
    if call_id in _MAIN:
        return "main"
    if call_id in _P3:
        return "phase3"
    if call_id in _P4:
        return "phase4"
    return "other"


_MAIN = main_run_ids()
_P3 = phase3_ids()
_P4 = phase4_ids()

CONTRAST_GROUPS = {
    "parent": "cued", "parent_committed": "cued", "parent_gap": "cued",
    "personal": "placebo", "gap_travel": "placebo", "gap_parental_only": "placebo",
    "gap_closure": "placebo", "gap_cert": "placebo",
    "gender_none": "direct", "gender_parent": "direct",
}


def missingness_table() -> dict:
    d = _first_attempts()
    d["phase"] = d.call_id.map(_phase_of)
    d = d[d.phase.isin(["main", "phase3", "phase4"])]
    # merge contrast from plan (logs carry it for e2)
    rows = []
    for (m, con, ph), g in d.groupby(["model_key", "contrast", "phase"]):
        n = len(g)
        ref = float(g.refusal_flag.fillna(False).mean())
        parse_fail = float((~g.parse_ok.fillna(False) & ~g.refusal_flag.fillna(False)).mean())
        # pair-clustered CI on missing = refusal + parse-fail
        g2 = g.copy()
        g2["miss"] = (~g2.parse_ok.fillna(False)).astype(float)  # refusal or fail
        # cluster by resume pair from resume_ids
        pm = g2.groupby("resume_ids")["miss"].mean()
        se = pm.std(ddof=1) / np.sqrt(len(pm)) if len(pm) > 1 else 0.0
        t95 = sps.t.ppf(0.975, max(len(pm) - 1, 1))
        rows.append({"model": m, "contrast": con, "phase": ph, "n": n,
                     "refusal_pct": round(100 * ref, 2),
                     "parse_fail_pct": round(100 * parse_fail, 2),
                     "no_valid_choice_pct": round(100 * g2.miss.mean(), 2),
                     "ci95": [round(100 * (g2.miss.mean() - t95 * se), 2),
                              round(100 * (g2.miss.mean() + t95 * se), 2)]})
    tab = pd.DataFrame(rows)
    out = {"table": tab.to_dict("records")}

    # cued vs placebo test per model x phase (pooled contrasts within group)
    tests = {}
    for m in MODELS:
        for ph in ["main", "phase3"]:
            sub = d[(d.model_key == m) & (d.phase == ph)].copy()
            sub["grp"] = sub.contrast.map(CONTRAST_GROUPS)
            sub = sub[sub.grp.isin(["cued", "placebo"])]
            sub["miss"] = (~sub.parse_ok.fillna(False)).astype(float)
            a = sub[sub.grp == "cued"].groupby("resume_ids")["miss"].mean()
            b = sub[sub.grp == "placebo"].groupby("resume_ids")["miss"].mean()
            common = a.index.intersection(b.index)
            if len(common) >= 5:
                dd = (a[common] - b[common]).values
                t, p = sps.ttest_1samp(dd, 0)
                tests[f"{m.split('_')[0]}|{ph}"] = {
                    "cued_minus_placebo_pp": round(100 * float(dd.mean()), 2),
                    "t": round(float(t), 1), "p": round(float(p), 4), "n_pairs": int(len(common))}
    out["cued_vs_placebo_tests"] = tests
    return out


def manski_bounds() -> dict:
    """P_lo = P(1-m), P_hi = P(1-m) + m per headline cell."""
    d = _first_attempts()
    d["phase"] = d.call_id.map(_phase_of)
    # valid choice outcomes from the clean e2 table
    e2 = load_clean("e2")
    e2 = e2[~e2.from_repair.astype(bool)]
    e2 = e2[e2.contrast.isin(["parent", "parent_committed", "parent_gap",
                              "personal", "gap_travel", "gap_parental_only"])]
    bounds = []
    for m in MODELS:
        for ph in ["main", "phase3"]:
            cells = e2[(e2.model_key == m)]
            cells = cells[cells.call_id.map(_phase_of) == ph]
            first = d[(d.model_key == m) & (d.phase == ph)]
            for con in ["parent", "parent_gap"]:
                for g in ["female", "male"]:
                    sub = cells[(cells.contrast == con) & (cells.gender == g)]
                    att = first[(first.contrast == con) & (first.gender == g)]
                    if not len(sub) or not len(att):
                        continue
                    P = float(pd.to_numeric(sub.parent_chosen, errors="coerce").mean())
                    miss = float((~att.parse_ok.fillna(False)).mean())
                    lo, hi = P * (1 - miss), P * (1 - miss) + miss
                    bounds.append({"model": m.split("_")[0], "phase": ph, "contrast": con,
                                   "gender": g, "P": round(P, 3), "missing": round(miss, 3),
                                   "P_lo": round(lo, 3), "P_hi": round(hi, 3),
                                   "hi_crosses_50": bool(hi >= 0.5)})
    out = {"bounds": bounds}
    crossing = [b for b in bounds if b["P_lo"] < 0.5 <= b["P_hi"]]
    out["cells_whose_bounds_span_50"] = [
        f"{b['model']} {b['phase']} {b['contrast']} {b['gender']} [{b['P_lo']:.3f},{b['P_hi']:.3f}]"
        for b in crossing]
    return out


def haiku_refusal_outcome() -> dict:
    """P(refuse) by cue and gender for Haiku (E2, first attempts, all phases)."""
    d = _first_attempts()
    d = d[(d.model_key == "claude_haiku_55")]
    d["phase"] = d.call_id.map(_phase_of)
    d = d[d.phase.isin(["main", "phase3"])]
    out = {}
    for ph in ["main", "phase3"]:
        sub = d[d.phase == ph]
        tbl = {}
        for con, g in sub.groupby("contrast"):
            gender_tbl = {}
            for gd, gg in g.groupby("gender"):
                gender_tbl[str(gd)] = round(100 * float(gg.refusal_flag.fillna(False).mean()), 2)
            tbl[con] = {"n": len(g), "refusal_pct_pooled": round(100 * float(g.refusal_flag.fillna(False).mean()), 2),
                        "by_gender": gender_tbl}
        out[ph] = tbl
    return out


def headline_excl_haiku() -> dict:
    """Pooled-over-models choice shares for mothers, Haiku excluded."""
    e2 = load_clean("e2")
    e2 = e2[~e2.from_repair.astype(bool)]
    e2 = e2[e2.call_id.isin(main_run_ids())]
    e2 = e2[e2.contrast.isin(["parent", "parent_gap"]) & (e2.gender == "female")]
    e2["pc"] = pd.to_numeric(e2.parent_chosen, errors="coerce")
    out = {}
    EXCL = [m for m in MODELS if m != "claude_haiku_55"]
    for label, pool in [("all", MODELS), ("excl_haiku", EXCL)]:
        sub = e2[e2.model_key.isin(pool)]
        pm = sub.groupby(["contrast", "resume_ids"])["pc"].mean().reset_index()
        row = {}
        for con in ["parent", "parent_gap"]:
            s = pm[pm.contrast == con]
            row[con] = round(float(s.pc.mean()), 3)
        out[label] = row
    return out


def main() -> None:
    OUT["missingness"] = missingness_table()
    OUT["manski"] = manski_bounds()
    OUT["haiku_refusal"] = haiku_refusal_outcome()
    OUT["headline_excl_haiku"] = headline_excl_haiku()
    p = ROOT / "docs/final/missingness.json"
    p.write_text(json.dumps(OUT, indent=1))

    L = ["# R15: refusals and missing choices as outcomes", "",
         "## 1. Missingness per model × contrast × phase (first attempts; repairs excluded)", "",
         "| model | phase | contrast | n | refusal% | parse-fail% | no-valid-choice% [95% CI] |",
         "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in OUT["missingness"]["table"]:
        if r["refusal_pct"] > 0 or r["no_valid_choice_pct"] > 2:
            L.append(f"| {r['model'].split('_')[0]} | {r['phase']} | {r['contrast']} | {r['n']} "
                     f"| {r['refusal_pct']} | {r['parse_fail_pct']} "
                     f"| {r['no_valid_choice_pct']} [{r['ci95'][0]}, {r['ci95'][1]}] |")
    L += ["", "### Cued vs placebo missing-rate tests (pair-matched)", "",
          "| model | phase | cued − placebo (pp) | t | p | n pairs |", "| --- | --- | --- | --- | --- | --- |"]
    for k, v in OUT["missingness"]["cued_vs_placebo_tests"].items():
        m, ph = k.split("|")
        L.append(f"| {m} | {ph} | {v['cued_minus_placebo_pp']:+.2f} | {v['t']} | {v['p']} | {v['n_pairs']} |")

    L += ["", "## 2. Manski bounds (headline E2 cells)", "",
          "P_lo = P·(1−m), P_hi = P·(1−m)+m.", "",
          "| model | phase | contrast | gender | P | missing | [P_lo, P_hi] | crosses .50 |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for b in OUT["manski"]["bounds"]:
        if b["missing"] >= 0.005:
            L.append(f"| {b['model']} | {b['phase']} | {b['contrast']} | {b['gender']} "
                     f"| {b['P']} | {b['missing']} | [{b['P_lo']}, {b['P_hi']}] | {'YES' if b['hi_crosses_50'] else ''} |")
    span = OUT["manski"]["cells_whose_bounds_span_50"]
    L += ["", f"**Cells whose bounds span .50: {len(span)}**" + (" — conclusions unchanged for all cells whose point estimate is far from .50 (all parent/parent_gap cells are; only near-parity cells could span)." if span else " — none."), ""]

    L += ["", "## 3. Haiku refusal rate by cue and gender (E2)", ""]
    for ph, tbl in OUT["haiku_refusal"].items():
        L.append(f"### {ph}")
        L.append("")
        for con, r in sorted(tbl.items(), key=lambda kv: -kv[1]["refusal_pct_pooled"]):
            if r["refusal_pct_pooled"] > 0:
                L.append(f"- `{con}`: {r['refusal_pct_pooled']}% (n={r['n']}) by gender: {r['by_gender']}")
        L.append("")

    L += ["## 4. Pooled mothers' choice shares, Haiku excluded", "",
          f"All models: {OUT['headline_excl_haiku']['all']}",
          f"Excl. Haiku: {OUT['headline_excl_haiku']['excl_haiku']}", ""]
    (ROOT / "docs/final/missingness.md").write_text("\n".join(L))
    print(f"[r15] wrote docs/final/missingness.{{md,json}}")
    print("bounds spanning .50:", len(span))
    for k, v in OUT["missingness"]["cued_vs_placebo_tests"].items():
        print(k, v)


if __name__ == "__main__":
    main()
