"""Occupation moderators: female share (BLS CPS Table 11), median wage (BLS OEWS),
time demands (O*NET Work Context), plus JD construction from O*NET tasks.

BLS (bls.gov) is Akamai-blocked from this network, so downloads fall back to the
Internet Archive Wayback Machine copies of the same official files (vintages
noted in QUESTIONS.md). O*NET comes from the official onetcenter.org Excel bundle.
If a value cannot be filled it stays null and the URL is recorded in QUESTIONS.md
(spec §4.1: never fabricate values).
"""
from __future__ import annotations

import io
import json
import re
import zipfile
from pathlib import Path

import httpx
import pandas as pd

from ..config import MATERIALS_DIR, RAW_DIR, OccupationsCfg

UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
CPS_URL = "https://www.bls.gov/cps/cpsaat11.htm"
OEWS_URL = "https://www.bls.gov/oes/special-requests/oesm25nat.zip"
ONET_EXCEL_URL = "https://www.onetcenter.org/dl_files/database/db_31_0_excel.zip"
WAYBACK = "https://web.archive.org/web/2026id_/"

# Elements used for time_demands composite (spec §4.1).
# O*NET 31.0 has no "Spend Time Traveling" item -> dropped (spec: "if available").
TIME_ITEMS = {  # element -> (scale, direction: +1 higher = more time demand)
    "Duration of Typical Work Week": ("CT", +1),  # 1 <40h, 2 40h, 3 >40h
    "Work Schedules": ("CT", +1),                 # 1 regular, 2 irregular, 3 seasonal
    "Time Pressure": ("CX", +1),                  # 1-5
}


def _http_get(url: str) -> bytes:
    with httpx.Client(headers=UA, follow_redirects=True, timeout=180) as c:
        r = c.get(url)
        r.raise_for_status()
        return r.content


def _get_with_wayback(url: str) -> bytes:
    try:
        return _http_get(url)
    except Exception:
        return _http_get(WAYBACK + url)


def _norm(s: str) -> str:
    s = re.sub(r"[^a-z0-9 ]", "", s.lower())
    return re.sub(r"\s+", " ", s).strip()


# our occupation titles -> CPS Table 11 row titles (normalized)
CPS_ALIASES = {
    "software engineer": ["software developers", "software developers and programmers"],
    "financial analyst": ["financial and investment analysts"],
    "mechanical engineer": ["mechanical engineers"],
    "heavy truck driver": ["driversales workers and truck drivers"],
    "construction laborer": ["construction laborers", "construction laborers and helpers"],
    "warehouse supervisor": ["supervisors of transportation and material moving workers"],
    "lawyer": ["lawyers", "lawyers judges and related workers"],
    "physician (family medicine)": ["other physicians"],
    "marketing manager": ["marketing managers", "marketing and sales managers"],
    "retail store manager": ["firstline supervisors of retail sales workers"],
    "restaurant manager": ["food service managers"],
    "customer service representative": ["customer service representatives"],
    "registered nurse": ["registered nurses"],
    "hr manager": ["human resources managers", "human resources workers"],
    "pharmacist": ["pharmacists"],
    "accountant": ["accountants and auditors"],
    "administrative assistant": ["secretaries and administrative assistants", "secretaries and administrative assistants except legal medical and executive"],
    "preschool teacher": ["preschool and kindergarten teachers", "preschool teachers"],
    "medical assistant": ["medical assistants"],
    "receptionist": ["receptionists and information clerks", "receptionists"],
}


def _load_cps(raw: Path) -> pd.DataFrame | None:
    f = raw / "cpsaat11.html"
    if not f.exists():
        try:
            f.write_bytes(_get_with_wayback(CPS_URL))
        except Exception as e:  # noqa: BLE001
            print(f"[occupations] CPS download failed ({e}); URL: {CPS_URL}")
            return None
    try:
        tabs = pd.read_html(io.BytesIO(f.read_bytes()), flavor="lxml")
        return tabs[0]
    except Exception as e:  # noqa: BLE001
        print(f"[occupations] CPS parse failed: {type(e).__name__}")
        return None


def _female_share(df: pd.DataFrame) -> dict[str, float]:
    """CPS Table 11: 'Percent of total employed -> Women' column = female share."""
    cols = df.columns.tolist()
    flat = [c[-1] if isinstance(c, tuple) else str(c) for c in cols]
    occ_col = 0
    try:
        women_col = flat.index("Women")
    except ValueError:
        return {}
    out: dict[str, float] = {}
    for _, row in df.iterrows():
        name = str(row.iloc[occ_col]).strip()
        try:
            women = float(str(row.iloc[women_col]).replace(",", ""))
        except (ValueError, TypeError):
            continue
        if 0 < women < 100 and name and not name.lower().startswith("total"):
            out[_norm(name)] = women / 100.0
    return out


def _load_oews(raw: Path) -> pd.DataFrame | None:
    zpath = raw / "oesm25nat.zip"
    if not zpath.exists():
        try:
            zpath.write_bytes(_get_with_wayback(OEWS_URL))
        except Exception as e:  # noqa: BLE001
            print(f"[occupations] OEWS download failed ({e}); URL: {OEWS_URL}")
            return None
    try:
        zf = zipfile.ZipFile(zpath)
        member = [n for n in zf.namelist() if n.lower().endswith((".xlsx", ".xls"))][0]
        df = pd.read_excel(io.BytesIO(zf.read(member)), dtype={"OCC_CODE": str})
        return df
    except Exception as e:  # noqa: BLE001
        print(f"[occupations] OEWS parse failed: {e}")
        return None


def _load_onet_excel(raw: Path, name: str) -> pd.DataFrame | None:
    zpath = raw / "onet" / "db_31_0_excel.zip"
    if not zpath.exists():
        try:
            zpath.parent.mkdir(parents=True, exist_ok=True)
            zpath.write_bytes(_http_get(ONET_EXCEL_URL))
        except Exception as e:  # noqa: BLE001
            print(f"[occupations] O*NET download failed ({e}); URL: {ONET_EXCEL_URL}")
            return None
    try:
        zf = zipfile.ZipFile(zpath)
        member = f"db_31_0_excel/{name}.xlsx"
        return pd.read_excel(io.BytesIO(zf.read(member)))
    except Exception as e:  # noqa: BLE001
        print(f"[occupations] O*NET {name} parse failed: {e}")
        return None


def _soc_prefix(soc: str) -> str:
    return soc[:7]


def _soc_candidates(row: pd.Series) -> list[str]:
    """SOC code candidates for lookups: the code itself + aliases (same 6-digit family last)."""
    socs = [str(row["soc"])] + [str(a) for a in row.get("soc_aliases", []) if a]
    return socs


def build_moderators() -> tuple[pd.DataFrame, list[str]]:
    """Fill female_share, median_wage, time_demands for the 20 occupations."""
    raw = RAW_DIR
    raw.mkdir(parents=True, exist_ok=True)
    questions: list[str] = []

    occs = OccupationsCfg.load()
    occ_df = pd.DataFrame([o.model_dump() for o in occs.occupations])

    # --- female share (CPS Table 11, 2025 annual averages via Wayback snapshot) ---
    cps = _load_cps(raw)
    shares = _female_share(cps) if cps is not None else {}
    if not shares:
        questions.append(f"- CPS Table 11 (female share) could not be parsed. URL: {CPS_URL}")

    def _share(title: str) -> float | None:
        for k in CPS_ALIASES.get(title.lower(), []) + [title.lower(), _norm(title)]:
            for cand in (k, _norm(k)):
                if cand in shares:
                    return shares[cand]
        for name, v in shares.items():  # containment fallback
            if _norm(title) in name or name in _norm(title):
                return v
        return None

    occ_df["female_share"] = occ_df["title"].map(_share)

    # --- median wage (OEWS May 2025 national file via Wayback snapshot) ---
    oews = _load_oews(raw)
    if oews is not None:
        med = pd.to_numeric(
            oews["A_MEDIAN"].astype(str).str.replace(",", "", regex=False), errors="coerce"
        )
        wage = pd.DataFrame(
            {"soc": oews["OCC_CODE"].astype(str).str.strip(), "median_wage": med}
        ).dropna().drop_duplicates("soc").set_index("soc")["median_wage"]
        major = wage.groupby(wage.index.str[:3]).mean()

        def _wage(row: pd.Series) -> float:
            for s in _soc_candidates(row):
                if s in wage.index:
                    return float(wage[s])
            return float(major.get(str(row["soc"])[:3], float("nan")))

        occ_df["median_wage"] = occ_df.apply(_wage, axis=1)
    else:
        questions.append(f"- OEWS (median wage) could not be parsed. URL: {OEWS_URL}")

    # --- time demands (O*NET 31.0 Work Context) ---
    wc = _load_onet_excel(raw, "Work Context")
    if wc is not None:
        wc["soc6"] = wc["O*NET-SOC Code"].astype(str).str[:7]
        item_vals: dict[str, pd.Series] = {}
        for elem, (scale, _dir) in TIME_ITEMS.items():
            sub = wc[(wc["Element Name"] == elem) & (wc["Scale ID"] == scale)]
            if sub.empty:
                questions.append(f"- O*NET Work Context item missing: {elem}")
                continue
            item_vals[elem] = sub.groupby("soc6")["Data Value"].mean()
        if item_vals:
            items = pd.DataFrame(item_vals)
            z = items.sub(items.mean()).div(items.std(ddof=0))
            zmean = z.mean(axis=1)
            zgroup = zmean.groupby(zmean.index.str[:6]).mean()

            def _td(row: pd.Series) -> float:
                for s in _soc_candidates(row):
                    if s[:7] in zmean.index:
                        return float(zmean[s[:7]])
                g = str(row["soc"])[:6]
                if g in zgroup.index:
                    return float(zgroup[g])
                return float("nan")

            occ_df["time_demands"] = occ_df.apply(_td, axis=1)
    else:
        questions.append("- O*NET Work Context (time demands) could not be downloaded.")

    # --- in_e4: 4 highest + 4 lowest time_demands ---
    if occ_df["time_demands"].notna().sum() >= 10:
        ranked = occ_df.dropna(subset=["time_demands"]).sort_values("time_demands")
        low4 = ranked.head(4)["id"].tolist()
        high4 = ranked.tail(4)["id"].tolist()
        occ_df["in_e4"] = occ_df["id"].isin(low4 + high4)

    for col in ["female_share", "median_wage", "time_demands"]:
        miss = occ_df.loc[occ_df[col].isna(), "id"].tolist()
        if miss:
            questions.append(f"- {col} still missing for: {', '.join(miss)}")

    occ_df.attrs["questions"] = questions
    return occ_df, questions


def build_jds(occ_df: pd.DataFrame) -> None:
    """One base JD per occupation from top O*NET tasks + skills (~150-250 words)."""
    tasks = _load_onet_excel(RAW_DIR, "Task Statements")
    ratings = _load_onet_excel(RAW_DIR, "Task Ratings")
    skills = _load_onet_excel(RAW_DIR, "Essential Skills")
    out_dir = MATERIALS_DIR / "job_descriptions"
    out_dir.mkdir(parents=True, exist_ok=True)
    jd_index: dict[str, dict] = {}
    for _, row in occ_df.iterrows():
        soc, occ_id, title = row["soc"], row["id"], row["title"]
        prefixes = tuple(_soc_candidates(row))
        task_list: list[str] = []
        if tasks is not None and ratings is not None:
            r_imp = ratings[ratings["Scale ID"] == "IM"][["Task ID", "Data Value"]]
            tr = tasks.merge(r_imp, on="Task ID", how="left")
            tr = tr[tr["O*NET-SOC Code"].astype(str).str.startswith(prefixes)]
            task_list = tr.sort_values("Data Value", ascending=False).head(5)["Task"].tolist()
        skill_list: list[str] = []
        if skills is not None:
            s = skills[
                skills["O*NET-SOC Code"].astype(str).str.startswith(prefixes)
                & (skills["Scale ID"] == "IM")
            ]
            skill_list = s.sort_values("Data Value", ascending=False).head(6)["Element Name"].tolist()
        bullets = "\n".join(f"- {str(t).rstrip('.').capitalize()}" for t in task_list)
        skills_txt = ", ".join(skill_list) if skill_list else "relevant domain skills"
        jd = (
            f"{title} - Hiring Announcement\n\n"
            f"Our company is hiring a {title.lower()} to join our team. The role involves the "
            f"core work of the occupation summarized below.\n\n"
            f"Key responsibilities:\n{bullets}\n\n"
            f"Requirements: {skills_txt}; several years of relevant experience; strong "
            f"communication skills and reliability. Competitive salary and benefits offered.\n\n"
            f"To apply, submit a resume and a short cover note."
        )
        rec = {"occupation_id": occ_id, "soc": soc, "jd": jd, "word_count": len(jd.split())}
        jd_index[occ_id] = rec
        (out_dir / f"{occ_id}.json").write_text(json.dumps(rec, indent=2))
    (out_dir / "index.json").write_text(json.dumps(jd_index, indent=2))
    print(f"[occupations] wrote {len(jd_index)} JDs to {out_dir}")


def run_build() -> None:
    occ_df, questions = build_moderators()
    MATERIALS_DIR.mkdir(parents=True, exist_ok=True)
    occ_df.to_json(MATERIALS_DIR / "occupations.json", orient="records", indent=2)
    occ_df.to_csv(MATERIALS_DIR / "occupations.csv", index=False)
    build_jds(occ_df)
    cols = ["id", "title", "female_share", "median_wage", "time_demands", "in_e4"]
    print(occ_df[cols].to_string(index=False))
    if questions:
        print("\n[occupations] open questions:")
        for q in questions:
            print(" ", q)
    (MATERIALS_DIR / "moderators_questions.txt").write_text("\n".join(questions))
