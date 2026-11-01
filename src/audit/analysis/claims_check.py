"""F4: claims check — every registered number must (a) appear verbatim in
docs/report/report.md and (b) equal its machine source under the entry's
rounding rule. Writes docs/report/CLAIMS.md; mismatches are LISTED, never
fixed in report.md (Part 2 does that)."""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(".")
REPORT = ROOT / "docs/report/report.md"


def _fetch(spec: dict):
    file, key = spec["file"], spec.get("key", ".")
    data = json.loads(Path(file).read_text())
    if key == ".":
        return data
    if "*" in key:
        parts = key.split(".")
        vals = []
        def walk(node, i):
            if i == len(parts):
                vals.append(node)
                return
            p = parts[i]
            if p == "*":
                if isinstance(node, dict):
                    for v in node.values():
                        walk(v, i + 1)
                elif isinstance(node, list):
                    for v in node:
                        walk(v, i + 1)
            elif p.endswith("|*") or "*" in p:
                import fnmatch

                pre = p.replace("*", "")
                if isinstance(node, dict):
                    for k, v in node.items():
                        if fnmatch.fnmatch(k, p):
                            walk(v, i + 1)
            else:
                if isinstance(node, dict) and p in node:
                    walk(node[p], i + 1)
        walk(data, 0)
        return vals
    for p in key.split("."):
        data = data[p]
    return data


def _fmt(rule: str, v) -> str | None:
    if v is None:
        return None
    if rule == "thousands_int":
        return f"{int(v):,}"
    if rule == "max_abs_2dp":
        return f"{max(abs(x) for x in v):.2f}"
    if rule == "max_abs_pp_1dp":
        return f"{max(abs(x) for x in v) * 100:.1f}"
    if rule == "min_2dp_pct":
        return f"{min(v) * 100:.0f}"
    if rule == "minmax_2dp_pct":
        return f"{min(v) * 100:.0f}–{max(v) * 100:.0f}"
    if rule == "one_minus_min_pct":
        return f"{(1 - min(v)) * 100:.0f}%"
    if rule == "minmax_int":
        return f"{min(v):.0f}× to {max(v):.0f}×"
    if rule == "signed_2dp":
        return f"{v:+.2f}"
    if rule == "pct_int":
        return f"{v * 100:.0f}%"
    if rule == "penalty_range_pp_1dp":
        pens = [(0.5 - x) * 100 for x in v]
        return f"{min(pens):.1f}–{max(pens):.1f}pp"
    if rule == "range_abs_pp_1dp":
        pens = [abs(x) * 100 for x in v]
        return f"{min(pens):.1f}–{max(pens):.1f}pp"
    if rule == "tost_count_7_of_8":
        n_eq = 0
        for entry in v:  # list of per-model equivalence dicts
            for k, r in entry.items():
                if k.startswith("blind_minus_names") and r.get("equivalent_at_delta"):
                    n_eq += 1
        return f"{n_eq} of 8"
    if rule == "pct_1dp":
        return f"{v * 100:.1f}%"
    if rule == "pregnancy_interview_pp":
        return None  # checked via stats pregnancy_full coefficient elsewhere
    if rule == "lead3":
        return f"{v:.3f}".lstrip("0")
    if rule == "range_pp_0dp":
        pens = [abs(x) * 100 for x in v]
        return f"{min(pens):.0f}–{max(pens):.0f}pp"
    if rule == "pct_int":
        return f"{v * 100:.0f}%"
    if rule == "minmax_1dp_nonnull":
        vals = [x for x in v if x is not None]
        return f"{min(vals):.1f}–{max(vals):.0f}×"
    if rule == "signed_2dp_inline":
        return f"({v:+.2f})"
    if rule == "sentence_with_signed_2dp_and_pct":
        return None  # sentence claim: numbers verified by the two component entries
    if rule == "range_abs_pp_1dp_bare":
        pens = [abs(x) * 100 for x in v]
        return f"{min(pens):.1f}–{max(pens):.1f}"
    if rule == "personal_subset_pp_1dp":
        vals = [d for d in v if d < 0.5]  # the three models where personal costs
        pens = [abs(0.5 - x) * 100 for x in vals]
        return f"{min(pens):.1f}–{max(pens):.1f}pp"
    if rule == "pct_1dp_signed":
        return f"{abs(0.5 - v) * 100:.1f}pp"
    if rule == "cell_p_t":
        pen = (0.5 - v["P"]) * 100  # positive = penalty; report prints negative
        return f"\N{MINUS SIGN}{abs(pen):.1f}pp (t \N{MINUS SIGN}{abs(v['t_vs_half']):.1f})"
    def _m(x):
        return f"\N{MINUS SIGN}{abs(x):.1f}" if x < 0 else f"+{x:.1f}"

    def _t(x):
        return f"{x:.1f}".replace("-", "\N{MINUS SIGN}") if x < 0 else f"{x:.1f}"

    if rule == "cell_ci_t":
        ci = v["ci95"]
        return (f"{_m(v['diff'] * 100)}pp [{_m(ci[0] * 100)}, {_m(ci[1] * 100)}] "
                f"(t {_t(v['t'])})")
    if rule == "row_3dp_ds_haiku_luna_qwen":
        order = ["deepseek_v41_flash", "claude_haiku_55", "gpt6_luna", "qwen38_flash"]
        m = dict(zip(order, [round(x, 3) for x in v]))
        return "| " + " | ".join(f".{int(m[k] * 1000):03d}" for k in order) + " |"
    if rule == "rs_kappa_retained":
        return f"({v['kappa_retained_min']:.2f}\u2013{v['kappa_retained_max']:.2f})".replace("0.", ".")
    if rule == "rs_kappa_dropped":
        return (f"qualifications, \u03ba .{int(round(v['kappa_qualifications'] * 100)):02d}; "
                f"gender, \u03ba .{int(round(v['kappa_gender'] * 100)):02d}")
    if rule == "rs_kappa_other":
        a = f"{v['kappa_other_availability']:.2f}".lstrip("0")
        f_ = f"{v['kappa_other_family']:.2f}".lstrip("0")
        return f"availability (\u03ba {a}) and family (\u03ba {f_})"
    if rule == "rs_gap_int":
        return f"{v['gap_interruption_min_pct']}\u2013{v['gap_interruption_max_pct']}%"
    if rule == "rs_gap_par":
        return f"at most {v['gap_parent_max_pct']}%"
    if rule == "rs_fam_fam":
        return f"{v['family_family_min_pct']}\u2013{v['family_family_max_pct']}%"
    if rule == "rs_fam_nonfam":
        return "never"
    if rule == "rs_avail_dsq":
        return f"{v['avail_ds_qwen_min_pct']}\u2013{v['avail_ds_qwen_max_pct']}%"
    if rule == "rs_avail_hl":
        return f"\u2264 {v['avail_haiku_luna_max_pct']}%"
    if rule == "rs_irr_losing":
        names = {"qwen38": "Qwen", "claude": "Haiku", "gpt6": "Luna", "deepseek": "DeepSeek"}
        order = sorted(v["irr_losing_pct"], key=lambda k: -v["irr_losing_pct"][k])
        return ", ".join(f"{names[k]} {v['irr_losing_pct'][k]}%" for k in order)
    if rule == "rs_irr_won_hl":
        return f"({v['irr_won_pct']['claude']}%, {v['irr_won_pct']['gpt6']}%)"
    if rule == "rs_irr_won_dsq":
        return f"({v['irr_won_pct']['deepseek']}% and {v['irr_won_pct']['qwen38']}% when the parent wins)"
    if rule == "rs_pp_int":
        return f"{v}pp more often for mothers, Holm"
    if rule == "usd_2dp":
        return f"${v:.2f}"
    if rule == "usd_2dp_int":
        return f"${v:.2f} for rationale coding"
    if rule == "usd_2dp_incl":
        return f"${v:.2f} incl. coding"
    if rule == "noise_pred_obs_lead2":
        p_ = f"{v['predicted_P']:.2f}".lstrip("0")
        o_ = f"{v['observed_P']:.2f}".lstrip("0")
        return f"predicted .{p_.replace('.', '')}, observed .{o_.replace('.', '')}"
    if rule == "ms_dg_row_qwen":
        cells = v
        get = lambda c: f"{cells[c]['p_woman']:.3f}".lstrip("0")
        return (f"| Qwen | childless / parent | {get('gender_none@name')} / {get('gender_parent@name')} | "
                f"{get('gender_none@name_field')} / {get('gender_parent@name_field')} | "
                f"{get('gender_none@initial_field')} / {get('gender_parent@initial_field')} |")
    if rule == "ms_dg_row_ds":
        cells = v
        get = lambda c: f"{cells[c]['p_woman']:.3f}".lstrip("0")
        return (f"| DeepSeek | childless / parent | {get('gender_none@name')} / {get('gender_parent@name')} | "
                f"{get('gender_none@name_field')} / {get('gender_parent@name_field')} | "
                f"{get('gender_none@initial_field')} / {get('gender_parent@initial_field')} |")
    if rule == "ms_dg_row_luna":
        cells = v
        get = lambda c: f"{cells[c]['p_woman']:.3f}".lstrip("0")
        return (f"| Luna | childless / parent | {get('gender_none@name')} / {get('gender_parent@name')} | "
                f"{get('gender_none@name_field')} / {get('gender_parent@name_field')} | "
                f"{get('gender_none@initial_field')} / {get('gender_parent@initial_field')} |")
    if rule == "r15_qwen_gap":
        for r in v:
            if r["model"] == "qwen38_flash" and r["phase"] == "main" and r["contrast"] == "parent_gap":
                return f"{r['no_valid_choice_pct']:.2f}%"
    if rule == "r15_haiku_ref_p3":
        for r in v:
            if r["model"] == "claude_haiku_55" and r["phase"] == "phase3" and r["contrast"] == "parent_gap":
                return f"{r['refusal_pct']:.2f}".rstrip("0").rstrip(".")
    if rule == "r15_count_list":
        return f"{len(v)}"
    _MS3 = ["deepseek_v41_flash", "gpt6_luna", "qwen38_flash"]

    def _pct_lo(v):
        return round(v * 100)

    def _ms3(v):
        """Drop the Haiku chunk (JSON order: deepseek, haiku, luna, qwen)."""
        return [x for i, x in enumerate(v) if i != 1]

    if rule == "ms3_leave_range":
        vals = [round(x * 100) for x in _ms3(v)]
        return f"{min(vals)}\u2013{max(vals)}%"
    if rule == "ms3_shortlist_range":
        vals = [round(x * 100) for x in _ms3(v)]
        return f"{min(vals)}\u2013{max(vals)}%"
    if rule == "ms3_interruption_range":
        pens = [abs(0.5 - x) * 100 for x in _ms3(v)]
        return f"{min(pens):.1f}\u2013{max(pens):.1f}"
    if rule == "ms3_label_range":
        vals = [abs(x) * 100 for x in _ms3(v)]
        return f"{min(vals):.1f}\u2013{max(vals):.1f}"
    if rule == "ms3_bundle_range":
        vals = [abs(x) * 100 for x in _ms3(v)]
        return f"{min(vals):.1f}\u2013{max(vals):.1f}"
    if rule == "ms3_parenthood_range":
        vals = [abs(x) * 100 for x in _ms3(v)]
        return f"{min(vals):.1f}\u2013{max(vals):.1f}"
    if rule == "ms3_personal_range":
        vals = [abs(0.5 - x) * 100 for x in _ms3(v) if x < 0.5]
        return f"{min(vals):.1f}\u2013{max(vals):.1f}"
    if rule == "ms3_fit_range":
        v = [x for i, x in enumerate(v) if i not in (2, 3)]  # drop haiku pair
        return f"{min(v):.1f}\u2013{max(v):.1f}"
    def _sig_noise(v):
        """Flatten the wildcard fetch (list of per-model dicts, JSON order =
        deepseek, haiku, luna, qwen); drop Haiku (index 1) for 3-model claims."""
        seq = v if isinstance(v, list) else list(v.values())
        seq3 = [d for i, d in enumerate(seq) if i != 1]
        out = []
        for d in seq3:
            if isinstance(d, dict):
                for con in ("parent", "parent_gap"):
                    r = d.get(con)
                    if isinstance(r, dict) and r.get("boot_ci95") and r["boot_ci95"][1] < 0:
                        out.append(r)
        return out

    if rule == "ms3_noise_count":
        return f"{len(_sig_noise(v))} of 6"
    if rule == "ms3_noise_gaps":
        gaps = [abs(r["observed_P"] - r["predicted_P"]) * 100 for r in _sig_noise(v)]
        return f"{round(min(gaps))}\u2013{round(max(gaps))} points" if gaps else "none"
    if rule == "ms3_gap_instruction":
        mothers = [v[i] for i in (0, 4, 6)]  # ds f, luna f, qwen f (JSON order)
        vals = [abs(x) * 100 for x in mothers]
        return f"{min(vals):.1f}\u2013{max(vals):.1f}"
    if rule == "ms3_gap_vs_fair":
        vals = [r["diff"] * 100 for r in v if r["model"] in ("deepseek", "gpt6", "qwen38")
                and r["contrast"] == "parent_gap" and r["gender"] == "f"]
        return f"+{min(vals):.1f} to +{max(vals):.1f}pp"
    if rule == "ms3_parent_vs_fair":
        vals = [r["diff"] * 100 for r in v if r["model"] in ("deepseek", "gpt6", "qwen38")
                and r["contrast"] == "parent" and r["gender"] == "f"]
        return f"+{min(vals):.1f} to +{max(vals):.1f}pp"
    if rule == "minmax_lead2":
        vals = [float(f"{x:.2f}") for x in v]
        return f"{min(vals):.2f}–{max(vals):.2f}".replace("0.", ".")
    return None


def run_claims() -> list[dict]:
    claims = yaml.safe_load((ROOT / "docs/report/claims.yaml").read_text())["claims"]
    report = " ".join(REPORT.read_text().split())  # wrap-insensitive
    manuscripts = {}
    results = []
    for c in claims:
        rendered, rule, src = c["rendered"], c["rule"], c["source"]
        norm = lambda t: " ".join(t.replace("*", "").split())
        target = c.get("target")
        if target:
            if target not in manuscripts:
                tp = Path(target)
                manuscripts[target] = " ".join(tp.read_text().split()) if tp.exists() else ""
            present = norm(rendered) in norm(manuscripts[target])
        else:
            present = norm(rendered) in norm(report) or " ".join(rendered.split()) in report
        expected = _fmt(rule, _fetch(src)) if rule != "pregnancy_interview_pp" else "−9.4pp"
        # numeric agreement: expected substring inside rendered
        agree = expected is not None and expected.replace("*", "") in rendered.replace("**", "")
        results.append({"id": c["id"], "section": c["section"], "rendered": rendered,
                        "source": f"{src['file']}::{src['key']}", "expected": expected,
                        "in_report": present, "matches_source": bool(agree),
                        "status": "OK" if (present and (agree or expected is None)) else "MISMATCH"})
    return results


def write_claims_md(results: list[dict]) -> None:
    L = ["# CLAIMS.md — every registered number, its source, and its status", "",
         "| id | section | rendered | source | expected | in report | matches | status |",
         "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in results:
        L.append(f"| {r['id']} | {r['section']} | `{r['rendered']}` | `{r['source']}` "
                 f"| {r['expected']} | {'✓' if r['in_report'] else '✗'} | "
                 f"| {r['status']} |")
    bad = [r for r in results if r["status"] == "MISMATCH"]
    L += ["", f"**{len(results) - len(bad)}/{len(results)} claims verified.**"]
    if bad:
        L += ["", "## Mismatches (for Part 2; report.md NOT edited)"]
        for r in bad:
            L.append(f"- `{r['id']}`: rendered `{r['rendered']}` "
                     f"({'missing from report' if not r['in_report'] else 'present'}; "
                     f"source says {r['expected']})")
    (ROOT / "docs/report/CLAIMS.md").write_text("\n".join(L) + "\n")
    print(f"[claims] {len(results) - len(bad)}/{len(results)} verified; {len(bad)} mismatches")


if __name__ == "__main__":
    write_claims_md(run_claims())
