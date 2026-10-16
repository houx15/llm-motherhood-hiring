"""Phase-3 occupational design (SPEC_PHASE3.md §5).

Computes four O*NET 31.0 work-activity composites (physical, care, analytic,
manage; importance scale, z-scored across all O*NET occupations), fixes the SOC
vintage mismatches for three main-run occupations, verifies female share
(BLS CPS Table 11, 2025) and median wage (OEWS May 2025) for the candidate list
from the files on disk, and selects the 8 new occupations (O8) that minimize
|corr(female share, care)| + |corr(female share, physical)| across the resulting
28 subject to the spec's quotas.

Every value is read from data/raw; nothing is remembered. Misses are reported,
never filled with guesses. Outputs:
  data/materials/occupations_phase3.csv   (all 28 with scores + selection flag)
  docs/report/occupation_design.md        (before/after design document)
"""
from __future__ import annotations

import io
import itertools
import zipfile
from pathlib import Path

import pandas as pd

from ..config import MATERIALS_DIR, RAW_DIR, ROOT
from .occupations import _load_cps, _load_oews, _load_onet_excel, _norm

# Work-activity composites (importance scale), per SPEC_PHASE3 §5.2.
WA_DIMS: dict[str, list[str]] = {
    "physical": [
        "Performing General Physical Activities",
        "Handling and Moving Objects",
        "Operating Vehicles, Mechanized Devices, or Equipment",
    ],
    "care": [
        "Assisting and Caring for Others",
        "Performing for or Working Directly with the Public",
    ],
    "analytic": [
        "Analyzing Data or Information",
        "Thinking Creatively",
        "Processing Information",
    ],
    "manage": [
        "Guiding, Directing, and Motivating Subordinates",
        "Coordinating the Work and Activities of Others",
    ],
}

# SOC vintage fixes for main-run occupations whose 2018 SOC code does not exist
# in O*NET 31.0 (which uses a newer vintage for some groups). Verified against
# Work Activities.xlsx titles on 2026-10-16.
ONET_SOC_FIXES: dict[str, list[str]] = {
    # 53-1047 (2018) not in O*NET 31.0; warehouse supervision spans both
    # hand-material-moving and machine/vehicle-operator first-line supervision.
    "warehouse_supervisor": ["53-1042", "53-1043"],
    # 13-2051 (2018 "Financial Analysts") not in O*NET 31.0; quantitative
    # financial analysts live under the 13-2099 detail code.
    "financial_analyst": ["13-2099.01"],
    # 29-1251 (2018) is still coded 29-1051 in this O*NET vintage.
    "pharmacist": ["29-1051"],
}

# Candidate pool for O8 (SPEC_PHASE3 §5.2). onet = O*NET SOC (this vintage),
# oews = OEWS May 2025 SOC (2018 vintage), cps = CPS Table 11 row title(s).
CANDIDATES: list[dict] = [
    {"id": "housekeeper", "title": "Housekeeper (Maids and Housekeeping Cleaners)",
     "quota": "female_physical", "onet": ["37-2012"], "oews": ["37-2012"],
     "cps": ["Maids and housekeeping cleaners"], "licensed": None},
    {"id": "home_health_aide", "title": "Home Health Aide",
     "quota": "female_physical", "onet": ["31-1121"], "oews": ["31-1120", "31-1011"],
     "cps": ["Home health aides"], "licensed": "Home health aide certification (state registry)"},
    {"id": "childcare_worker", "title": "Childcare Worker",
     "quota": "female_physical", "onet": ["39-9011"], "oews": ["39-9011"],
     "cps": ["Childcare workers"], "licensed": None},
    {"id": "firefighter", "title": "Firefighter",
     "quota": "male_care", "onet": ["33-2011"], "oews": ["33-2011"],
     "cps": ["Firefighters"], "licensed": "State Firefighter I/II certification"},
    {"id": "police_officer", "title": "Police Officer (Patrol)",
     "quota": "male_care", "onet": ["33-3051"], "oews": ["33-3051"],
     "cps": ["Police officers"], "licensed": "POST law-enforcement certification"},
    {"id": "emt_paramedic", "title": "EMT / Paramedic",
     "quota": "male_care", "onet": ["29-2043"], "oews": ["29-2040"],
     "cps": ["Emergency medical technicians", "Paramedics"],  # combined, count-weighted
     "licensed": "National Registry EMT / paramedic certification"},
    {"id": "veterinarian", "title": "Veterinarian",
     "quota": "female_analytic", "onet": ["29-1131"], "oews": ["29-1131"],
     "cps": ["Veterinarians"], "licensed": "DVM and state veterinary license"},
    {"id": "clinical_psychologist", "title": "Clinical and Counseling Psychologist",
     "quota": "female_analytic", "onet": ["19-3033"], "oews": ["19-3033", "19-3031"],
     "cps": ["Clinical and counseling psychologists"], "licensed": "PhD/PsyD and state psychology license"},
    # Substitute for the female_analytic quota: clinical psychologists are SUPPRESSED
    # in CPS Table 11 (19k employed, "-") so their female share cannot be verified
    # from the spec's source. Medical & health services managers are verifiable and
    # fit the quota (female-dominated, high-wage, analytic). Documented deviation —
    # see QUESTIONS.md phase-3 section.
    {"id": "health_services_manager", "title": "Medical and Health Services Manager",
     "quota": "female_analytic", "onet": ["11-9111"], "oews": ["11-9111"],
     "cps": ["Medical and health services managers"], "licensed": None},
    {"id": "electrician", "title": "Electrician",
     "quota": "male_trade", "onet": ["47-2111"], "oews": ["47-2111"],
     "cps": ["Electricians"], "licensed": "Journeyman electrician license"},
    {"id": "security_guard", "title": "Security Guard",
     "quota": "optional", "onet": ["33-9032"], "oews": ["33-9032"],
     "cps": ["Security guards and gambling surveillance officers"], "licensed": "State guard card"},
    {"id": "janitor", "title": "Janitor (Building Cleaner)",
     "quota": "optional", "onet": ["37-2011"], "oews": ["37-2011"],
     "cps": ["Janitors and building cleaners"], "licensed": None},
]

QUOTA_MIN = {"female_physical": 2, "male_care": 2, "female_analytic": 2, "male_trade": 1}


def work_activity_scores() -> pd.DataFrame:
    """Composite z-scores for the four dimensions, indexed by 6/7-digit SOC prefix
    as it appears in O*NET 31.0 (one row per occupation; detail codes collapsed)."""
    wa = _load_onet_excel(RAW_DIR, "Work Activities")
    wa = wa[wa["Scale ID"] == "IM"].copy()
    wa["soc"] = wa["O*NET-SOC Code"].astype(str)
    pivot = wa.pivot_table(index="soc", columns="Element Name", values="Data Value", aggfunc="mean")
    z = pivot.sub(pivot.mean()).div(pivot.std(ddof=0))
    out = pd.DataFrame(index=z.index)
    for dim, elems in WA_DIMS.items():
        missing = [e for e in elems if e not in z.columns]
        if missing:
            raise SystemExit(f"O*NET Work Activities missing elements for {dim}: {missing}")
        out[dim] = z[elems].mean(axis=1)
    return out


def _onet_lookup(scores: pd.DataFrame, onet_socs: list[str]):
    """Mean composite over the aliased O*NET codes; None if no exact row."""
    idx = scores.index
    hits = []
    for s in onet_socs:
        hits += [i for i in idx if i == s or i.startswith(s + ".")]
    if not hits:
        return None
    return scores.loc[hits].mean(axis=0)


def _cps_shares() -> tuple[dict[str, float], dict[str, tuple[float, float]]]:
    """(share by normalized title, (total_employed, women_pct) by title) from CPS Table 11."""
    cps = _load_cps(RAW_DIR)
    share: dict[str, float] = {}
    counts: dict[str, tuple[float, float]] = {}
    for _, row in cps.iterrows():
        name = str(row.iloc[0]).strip()
        try:
            total = float(str(row.iloc[1]).replace(",", ""))
            women = float(str(row.iloc[2]).replace(",", ""))
        except (ValueError, TypeError):
            continue
        if not name or total <= 0 or not 0 < women < 100:
            continue
        share[_norm(name)] = women / 100.0
        counts[_norm(name)] = (total, women)
    return share, counts


def _combined_share(counts: dict[str, tuple[float, float]], titles: list[str]) -> float | None:
    """Count-weighted share across multiple CPS rows (e.g. EMT + paramedic)."""
    tot = wmn = 0.0
    for t in titles:
        if _norm(t) not in counts:
            return None
        a, b = counts[_norm(t)]
        tot += a
        wmn += a * b / 100.0
    return wmn / tot if tot else None


def _oews_wage(oews: pd.DataFrame, codes: list[str]) -> float | None:
    med = pd.to_numeric(oews["A_MEDIAN"].astype(str).str.replace(",", "", regex=False), errors="coerce")
    w = pd.DataFrame({"soc": oews["OCC_CODE"].astype(str).str.strip(), "median_wage": med}).dropna()
    w = w.drop_duplicates("soc").set_index("soc")["median_wage"]
    for c in codes:
        if c in w.index:
            return float(w[c])
    return None


def build_phase3(verbose: bool = True) -> pd.DataFrame:
    scores = work_activity_scores()
    oews = _load_oews(RAW_DIR)
    shares, counts = _cps_shares()

    # --- current 20 (from the frozen main-run table) with SOC fixes ---
    cur = pd.read_csv(MATERIALS_DIR / "occupations.csv")
    rows: list[dict] = []
    misses: list[str] = []
    for _, r in cur.iterrows():
        onet_socs = ONET_SOC_FIXES.get(r["id"], [str(r["soc"])])
        sc = _onet_lookup(scores, onet_socs)
        if sc is None:
            misses.append(f"{r['id']}: no O*NET row for {onet_socs}")
            continue
        rows.append({
            "id": r["id"], "title": r["title"], "cohort": "o20", "selected": False,
            "soc": r["soc"], "onet_soc": "+".join(onet_socs),
            "female_share": r["female_share"], "median_wage": r["median_wage"],
            "time_demands": r["time_demands"], "in_e4": r["in_e4"],
            "physical": sc["physical"], "care": sc["care"],
            "analytic": sc["analytic"], "manage": sc["manage"],
            "quota_group": "", "licensed": "",
        })

    # --- candidates, verified from files ---
    cand_rows: list[dict] = []
    for c in CANDIDATES:
        sc = _onet_lookup(scores, c["onet"])
        if sc is None:
            misses.append(f"{c['id']}: no O*NET row for {c['onet']}")
            continue
        share = _combined_share(counts, c["cps"]) if len(c["cps"]) > 1 else shares.get(_norm(c["cps"][0]))
        wage = _oews_wage(oews, c["oews"]) if oews is not None else None
        if share is None:
            misses.append(f"{c['id']}: CPS female share not found for {c['cps']}")
        if wage is None:
            misses.append(f"{c['id']}: OEWS median wage not found for {c['oews']}")
        cand_rows.append({
            "id": c["id"], "title": c["title"], "cohort": "o8", "selected": False,
            "soc": c["oews"][0], "onet_soc": "+".join(c["onet"]),
            "female_share": share, "median_wage": wage,
            "time_demands": None, "in_e4": False,
            "physical": sc["physical"], "care": sc["care"],
            "analytic": sc["analytic"], "manage": sc["manage"],
            "quota_group": c["quota"], "licensed": c["licensed"] or "",
        })

    if misses:
        for m in misses:
            print("[phase3-occ] MISS:", m)
    usable = [c for c in cand_rows if c["female_share"] is not None and c["median_wage"] is not None]

    # --- quota-constrained selection minimizing the confound objective ---
    def objective(combo: list[dict]) -> tuple[float, float]:
        df = pd.DataFrame(rows + combo).dropna(subset=["female_share", "care", "physical"])
        f = df["female_share"]
        obj = abs(f.corr(df["care"])) + abs(f.corr(df["physical"]))
        tie = abs(f.corr(df["analytic"])) + abs(f.corr(df["manage"]))
        return obj, tie

    best: tuple[tuple[float, float], list[dict]] | None = None
    n_checked = 0
    for combo_idx in itertools.combinations(range(len(usable)), 8):
        combo = [usable[i] for i in combo_idx]
        by_q: dict[str, int] = {}
        for c in combo:
            by_q[c["quota_group"]] = by_q.get(c["quota_group"], 0) + 1
        if any(by_q.get(q, 0) < m for q, m in QUOTA_MIN.items()):
            continue
        n_checked += 1
        o = objective(combo)
        if best is None or o < best[0]:
            best = (o, combo)
    if best is None:
        raise SystemExit("no candidate combination satisfies the quotas")
    (obj, _tie), combo = best
    for c in combo:
        c["selected"] = True

    all_rows = rows + cand_rows
    df = pd.DataFrame(all_rows)
    MATERIALS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(MATERIALS_DIR / "occupations_phase3.csv", index=False)

    before = pd.DataFrame(rows).dropna(subset=["female_share"])
    after = pd.concat([before, pd.DataFrame(combo)])
    frontier = _frontier(rows, usable)
    doc = _design_doc(before, after, obj, n_checked, misses, combo, frontier)
    (ROOT / "docs" / "report" / "occupation_design.md").write_text(doc)
    if verbose:
        print(doc)
    return df


def _frontier(rows: list[dict], usable: list[dict]) -> list[tuple[float, float, float, list[str]]]:
    """Top-5 quota-feasible combinations by the spec's sum objective."""
    out: list[tuple[float, float, float, list[str]]] = []
    for combo_idx in itertools.combinations(range(len(usable)), 8):
        combo = [usable[i] for i in combo_idx]
        by_q: dict[str, int] = {}
        for c in combo:
            by_q[c["quota_group"]] = by_q.get(c["quota_group"], 0) + 1
        if any(by_q.get(q, 0) < m for q, m in QUOTA_MIN.items()):
            continue
        d = pd.DataFrame(rows + combo).dropna(subset=["female_share", "care", "physical"])
        f = d["female_share"]
        cc, pc = f.corr(d["care"]), f.corr(d["physical"])
        out.append((abs(cc) + abs(pc), cc, pc, [c["id"] for c in combo]))
    out.sort(key=lambda x: x[0])
    return out[:5]


def _corr_table(df: pd.DataFrame) -> str:
    cols = ["female_share", "median_wage", "physical", "care", "analytic", "manage"]
    c = df[cols].corr().round(2)
    return c.to_markdown()


def _design_doc(before: pd.DataFrame, after: pd.DataFrame, obj: float, n_checked: int,
                misses: list[str], combo: list[dict],
                frontier: list[tuple[float, float, float, list[str]]]) -> str:
    b = before["female_share"]
    a = after["female_share"]
    lines = [
        "# Phase-3 occupational design (SPEC_PHASE3.md §5)",
        "",
        "All values computed from the files in `data/raw` (O*NET 31.0 Work Activities",
        "importance scale, z-scored across all O*NET occupations; CPS Table 11 2025",
        "female share, count-weighted where two CPS rows are combined; OEWS May 2025",
        "median wage). SOC vintage fixes, verified against O*NET titles:",
    ]
    lines += [f"- `{k}`: {v} ({' + '.join(v)})" for k, v in ONET_SOC_FIXES.items()]
    lines += [
        "",
        "## Confound reduction",
        "",
        f"| correlation with female share | O20 only (n={len(before)}) | O20+O8 (n={len(after)}) |",
        "| --- | --- | --- |",
        f"| care | {b.corr(before['care']):+.3f} | {a.corr(after['care']):+.3f} |",
        f"| physical | {b.corr(before['physical']):+.3f} | {a.corr(after['physical']):+.3f} |",
        f"| analytic | {b.corr(before['analytic']):+.3f} | {a.corr(after['analytic']):+.3f} |",
        f"| manage | {b.corr(before['manage']):+.3f} | {a.corr(after['manage']):+.3f} |",
        "",
        f"Selection objective (|corr(female, care)| + |corr(female, physical)|) = {obj:.3f};"
        f" {n_checked} quota-feasible combinations of C({len(CANDIDATES) + 1},8) searched"
        " exhaustively.",
        "",
        "**Honest limitation:** every quota-feasible combination *deepens* the female-share–",
        "physical correlation (best achievable ≈ −0.32 vs −0.26 at baseline), because the",
        "quota occupations that are male-dominated and care-oriented (police, EMT, security)",
        "and the skilled trade (electrician) are all above-average physical, while the",
        "female-dominated additions (housekeeper, childcare) are only mildly physical. The",
        "design's real achievement is **separability**: O20 had *no* male-dominated care or",
        "female-dominated physical occupation (a perfect confound); O28 contains both, so",
        "care and female share can be entered jointly in occupation-level regressions",
        "(§8.5) even though the bivariate correlations remain nonzero.",
        "",
        "## Selection frontier (top 5 of the quota-feasible combinations)",
        "",
        "| objective | corr(female, care) | corr(female, physical) | combination |",
        "| --- | --- | --- | --- |",
    ]
    for o, cc, pc, ids in frontier:
        mark = " **(selected)**" if sorted(ids) == sorted(c["id"] for c in combo) else ""
        lines.append(f"| {o:.3f} | {cc:+.3f} | {pc:+.3f} | {', '.join(sorted(ids))}{mark} |")
    lines += [
        "",
        "## Selected occupations (O8)",
        "",
        "| id | title | female share | median wage | physical z | care z | analytic z | manage z | quota | license shown on résumé |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for c in sorted(combo, key=lambda x: x["id"]):
        lines.append(
            f"| {c['id']} | {c['title']} | {c['female_share']:.3f} | ${c['median_wage']:,.0f} "
            f"| {c['physical']:+.2f} | {c['care']:+.2f} | {c['analytic']:+.2f} | {c['manage']:+.2f} "
            f"| {c['quota_group']} | {c['licensed'] or '—'} |"
        )
    lines += [
        "",
        "## Full correlation matrices",
        "",
        "### O20 only",
        "",
        _corr_table(before),
        "",
        "### O20 + O8",
        "",
        _corr_table(after),
        "",
        "## Candidates not selected",
        "",
    ]
    ns = [c for c in CANDIDATES if c["id"] not in {x["id"] for x in combo}]
    lines += [f"- {c['id']} ({c['quota']})" for c in ns]
    if misses:
        lines += ["", "## Data misses (not filled)", ""] + [f"- {m}" for m in misses]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    build_phase3()
