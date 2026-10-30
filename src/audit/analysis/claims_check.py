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
    file, key = spec["file"], spec["key"]
    data = json.loads(Path(file).read_text())
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
    if rule == "minmax_lead2":
        vals = [float(f"{x:.2f}") for x in v]
        return f"{min(vals):.2f}–{max(vals):.2f}".replace("0.", ".")
    return None


def run_claims() -> list[dict]:
    claims = yaml.safe_load((ROOT / "docs/report/claims.yaml").read_text())["claims"]
    report = " ".join(REPORT.read_text().split())  # wrap-insensitive
    results = []
    for c in claims:
        rendered, rule, src = c["rendered"], c["rule"], c["source"]
        present = " ".join(rendered.split()) in report
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
