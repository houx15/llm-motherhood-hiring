"""Base résumé construction: Kaggle-derived (anonymized + normalized) and
O*NET-grounded synthetic résumés, generated once via the pinned model and frozen.
Validator fails the build on any residual PII / gender / family cue (spec §4.2)."""
from __future__ import annotations

import asyncio
import json
import os
import random
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ..budget import BudgetGuard, deepseek_off_peak, price_for
from ..client import OpenRouterClient, RefusalError, TransportFailure
from ..config import MATERIALS_DIR, RAW_DIR, load_names, load_occupations_built
from ..parse import extract_json
from ..runner import _append, _ledger_row
from .occupations import _load_onet_excel

KAGGLE_CSV = RAW_DIR / "Resume" / "Resume.csv"

# occupation -> (kaggle categories, include regex on text, exclude regex)
KAGGLE_MAP: dict[str, tuple[list[str], str, str]] = {
    "software_engineer": (["INFORMATION-TECHNOLOGY"], r"software (engineer|developer)|programmer|full.?stack", r"",
    ),
    "financial_analyst": (["FINANCE"], r"financial analyst|investment analyst|portfolio", r"",
    ),
    "mechanical_engineer": (["ENGINEERING"], r"mechanical", r"",
    ),
    "lawyer": (["ADVOCATE"], r"attorney|law (firm|school|degree)|litigat|bar admission|legal counsel", r"",
    ),
    "marketing_manager": (["BUSINESS-DEVELOPMENT", "PUBLIC-RELATIONS", "DIGITAL-MEDIA"], r"marketing", r"",
    ),
    "retail_store_manager": (["SALES", "BUSINESS-DEVELOPMENT"], r"store manager|retail", r"",
    ),
    "restaurant_manager": (["CHEF"], r"restaurant|food service|food & beverage|kitchen manager", r"",
    ),
    "customer_service_representative": (["BPO", "ADVOCATE", "HR"], r"customer service|customer support|call center", r"",
    ),
    "registered_nurse": (["HEALTHCARE"], r"registered nurse|\bRN\b|staff nurse|nurse", r"",
    ),
    "hr_manager": (["HR"], r"human resources|hr (manager|director|business partner)", r"",
    ),
    "accountant": (["ACCOUNTANT"], r"account", r"",
    ),
    "administrative_assistant": (["HR", "BPO", "ARTS"], r"administrative assistant|office assistant|executive assistant|admin", r"",
    ),
    "preschool_teacher": (["TEACHER"], r"preschool|pre.?school|early childhood|kindergarten|elementary", r"",
    ),
    "medical_assistant": (["HEALTHCARE"], r"medical assistant|clinical assistant", r"",
    ),
}

INDUSTRY_SEEDS = [
    "a mid-size regional firm", "a large national company", "a growing mid-market company",
    "a well-established local employer", "an industry-leading organization",
]

CUE_WORDS = [
    "mother", "father", " mom ", " mum ", " dad ", "wife", "husband", "spouse", "married",
    "marital", "children", "child", "kids", "baby", "babies", "pregnan", "maternity",
    "paternity", "parental", "parent", "pta", "family", "son", "daughter", "single",
    "divorced", "widow", " he ", " she ", " his ", " her ", "himself", "herself",
    "mr.", "ms.", "mrs.", "miss",
]

PII_PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+", re.I),
    "phone": re.compile(r"\(?\d{3}\)?[- .]?\d{3}[- .]?\d{4}"),
    "url": re.compile(r"https?://|www\.|linkedin|github\.com|\.com/\w", re.I),
    "street": re.compile(r"\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Blvd|Drive|Dr|Lane|Ln)\b"),
    "dob": re.compile(r"\b(19[5-9]\d|200[0-5])\b.*(born|birth|date of birth)|(born|dob).*(19[5-9]\d)", re.I),
    "study_names": re.compile(r"\b(Emily|Sarah|Anne|Greg|Matthew|Todd)\b"),
}


def month_index(s: str | int, default=None) -> int:
    if str(s).lower() == "present":
        return default if default is not None else 2026 * 12 + 10
    y, m = int(str(s)[:4]), int(str(s)[-2:])
    return y * 12 + m


def validate_resume(r: dict) -> list[str]:
    """Return list of violations (empty = valid)."""
    v: list[str] = []
    text = json.dumps(r, ensure_ascii=False).lower()
    for w in CUE_WORDS:
        word = w.strip()
        if re.search(rf"\b{re.escape(word)}\b", text):
            v.append(f"cue word: {word}")
    for name, pat in PII_PATTERNS.items():
        if pat.search(json.dumps(r, ensure_ascii=False)):
            v.append(f"PII pattern: {name}")
    exp = r.get("experience", [])
    if not 2 <= len(exp) <= 6:
        v.append(f"experience entries {len(exp)} not in 2-6")
        return v
    # total experience months (no gaps: contiguous), ends Present
    starts = [month_index(e["start"]) for e in exp]
    ends = [month_index(e.get("end", "Present")) for e in exp]
    order = sorted(range(len(exp)), key=lambda i: starts[i])
    for a, b in zip(order, order[1:]):
        if starts[b] > ends[a]:
            v.append(f"gap between entries {a}->{b}")
        if starts[b] < ends[a]:
            v.append(f"overlap between entries {a}->{b}")
    if str(exp[order[-1]].get("end", "Present")).lower() != "present":
        v.append("last job does not end at Present")
    total = sum(max(0, e - s) for s, e in zip(starts, ends))
    if not 90 <= total <= 150:
        v.append(f"total experience {total} months outside 8-12y window")
    if r.get("volunteer"):
        v.append("base resume has volunteer entries")
    if not (8 <= len(r.get("skills", [])) <= 20):
        v.append(f"skills count {len(r.get('skills', []))} outside 8-20")
    if not 1 <= len(r.get("education", [])) <= 2:
        v.append("education entries not in 1-2")
    return v


def select_kaggle_sources(occ: str, k: int = 2) -> list[tuple[int, str]]:
    """Deterministic top-k clean Kaggle resumes for an occupation."""
    if not KAGGLE_CSV.exists() or occ not in KAGGLE_MAP:
        return []
    cats, include, exclude = KAGGLE_MAP[occ]
    df = pd.read_csv(KAGGLE_CSV)
    sub = df[df["Category"].isin(cats)].copy()
    sub = sub[sub["Resume_str"].str.contains(include, case=False, regex=True, na=False)]
    if exclude:
        sub = sub[~sub["Resume_str"].str.contains(exclude, case=False, regex=True, na=False)]
    if sub.empty:
        return []
    def score(row):
        t = row["Resume_str"]
        s = 0.0
        L = len(t)
        s -= abs(L - 3500) / 3500  # prefer medium length
        s -= 2 * len(PII_PATTERNS["email"].findall(t))
        s -= 1 * len(PII_PATTERNS["phone"].findall(t))
        s -= 2 * len(PII_PATTERNS["url"].findall(t))
        s -= 3 * len(re.findall(r"mother|father|wife|husband|children|pregnan", t, re.I))
        s += len(re.findall(r"(19|20)\d{2}", t)) * 0.02  # has dates
        s -= t.count("＠") + t.count("·")
        return s
    sub["score"] = sub.apply(score, axis=1)
    sub = sub.sort_values(["score", "ID"], ascending=[False, True])
    out = []
    for _, row in sub.head(k * 3).iterrows():
        out.append((int(row["ID"]), row["Resume_str"]))
        if len(out) >= k:
            break
    return out


STRUCTURE_TMPL = """You are preparing anonymized research materials for a hiring study.

Convert the RAW RESUME TEXT below into a structured, anonymized, normalized JSON resume for the occupation "{title}".

STRICT RULES:
1. Remove ALL personal information: names, emails, phones, addresses, URLs, dates of birth, photos, citizenship. Employers become generic descriptors (e.g., "a regional logistics company", "a national retail chain") — no real company names.
2. Remove ALL mentions of gender, family, marital or parental status; use gender-neutral phrasing only.
3. Normalize work history: exactly 3-4 jobs, continuous full-time employment covering 8-12 years total with NO gaps or overlaps, most recent job ending "Present" (end "2026-09" is also acceptable ONLY if a Present job exists — always make the LAST job end "Present").
4. Keep only experience/skills plausibly relevant to {title}; do not inflate seniority beyond ~10 years.
5. Dates strictly "YYYY-MM"; education 1-2 entries, institution generic ("a state university").
6. summary: 1-2 sentences, gender-neutral. skills: 10-14 items. volunteer: [] (empty). notes: "".

OUTPUT ONLY a JSON object with keys:
resume_id (leave ""), occupation_id ("{occ}"), source ("kaggle"), summary, experience (list of title, employer, start, end, bullets[2-3 each]), education (list of degree, institution, year), skills, volunteer, notes.

RAW RESUME TEXT:
{raw}"""

SYNTH_TMPL = """You are preparing synthetic research materials for a hiring study.

Create ONE realistic, anonymized resume for the occupation "{title}" ({soc}).

GROUNDING — representative work activities for this occupation:
{tasks}

COMMON SKILLS: {skills}

PROFILE VARIANT (use for diversity): {variant}

STRICT RULES:
1. NO personal information, NO real company names (use generic descriptors like "{industry}"), NO gender or family or marital cues; gender-neutral phrasing only.
2. Exactly 3-4 jobs covering 8-12 years of continuous full-time experience, no gaps, no overlaps; LAST job ends "Present". Dates strictly "YYYY-MM".
3. Bullets grounded in the work activities above; quantified achievements fine. Do not exceed ~10 years total experience.
4. Education 1-2 entries, generic institutions; degree year consistent with experience start.
5. summary: 1-2 sentences. skills: 10-14 items. volunteer: [] (empty). notes: "".

OUTPUT ONLY a JSON object with keys:
resume_id (leave ""), occupation_id ("{occ}"), source ("synthetic"), summary, experience (list of title, employer, start, end, bullets[2-3]), education (list of degree, institution, year), skills, volunteer, notes."""


def _onet_grounding(occ_row) -> tuple[str, str]:
    tasks = _load_onet_excel(RAW_DIR, "Task Statements")
    skills = _load_onet_excel(RAW_DIR, "Essential Skills")
    prefixes = (occ_row["soc"], *occ_row.get("soc_aliases", []))
    tl = (
        tasks[tasks["O*NET-SOC Code"].astype(str).str.startswith(tuple(prefixes))]["Task"]
        .head(8)
        .tolist()
    ) if tasks is not None else []
    sl = (
        skills[
            skills["O*NET-SOC Code"].astype(str).str.startswith(tuple(prefixes))
            & (skills["Scale ID"] == "IM")
        ]
        .sort_values("Data Value", ascending=False)["Element Name"]
        .head(10)
        .tolist()
    ) if skills is not None else []
    return " | ".join(tl), ", ".join(sl)


def build_jobs(force: bool = False) -> list[dict]:
    """Assemble generation jobs for all occupations (4 base + 2 extras each)."""
    occs = load_occupations_built().occupations
    by_id = {o.id: o for o in occs}
    occ_df = {o.id: o.model_dump() for o in occs}
    jobs: list[dict] = []
    rng = random.Random(20261014)
    for occ in occs:
        out = MATERIALS_DIR / "base_resumes" / f"{occ.id}.json"
        if out.exists() and not force:
            continue
        tasks, skills = _onet_grounding(occ_df[occ.id])
        kaggle = select_kaggle_sources(occ.id, k=2)
        jobs_for_occ: list[dict] = []
        for idx in range(6):  # 0-3 base, 4-5 extras
            rid = f"{occ.id}_{idx:02d}"
            if idx < len(kaggle):
                kaggle_id, raw = kaggle[idx]
                prompt = STRUCTURE_TMPL.format(title=occ.title, occ=occ.id, raw=raw[:6000])
                job = {"kind": "structure", "resume_id": rid, "occ": occ.id,
                       "kaggle_id": kaggle_id, "prompt": prompt}
            else:
                variant = INDUSTRY_SEEDS[(idx + rng.randrange(3)) % len(INDUSTRY_SEEDS)]
                prompt = SYNTH_TMPL.format(
                    title=occ.title, soc=occ.soc, tasks=tasks or "typical occupation duties",
                    skills=skills or "core occupational skills", variant=variant,
                    occ=occ.id, industry=variant,
                )
                job = {"kind": "synth", "resume_id": rid, "occ": occ.id, "prompt": prompt}
            job["role"] = "base" if idx < 4 else "extra"
            jobs_for_occ.append(job)
        jobs.extend(jobs_for_occ)
    return jobs


async def generate_materials(
    model_key: str, jobs: list[dict], pricing: str | None = None, max_retries: int = 2
) -> dict:
    """Run generation jobs through the pinned model; freeze outputs; validate."""
    from ..config import load_models

    if not jobs:
        print("[materials] all resume files already frozen; nothing to generate")
        return {"generated": 0}
    models = load_models()
    mcfg = next(m for m in models.models if m.key == model_key)
    budget = BudgetGuard()
    peak = (pricing == "peak") if pricing else not deepseek_off_peak()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + f"-materials_gen-{model_key}"
    run_dir = __import__("audit.config", fromlist=["RUNS_DIR"]).RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "logs.jsonl"

    import hashlib

    def jid(j):
        return hashlib.sha256(json.dumps({k: j[k] for k in ("resume_id", "kind", "kaggle_id") if k in j}, sort_keys=True).encode()).hexdigest()[:16]

    est_in, est_out = 1500, 700
    pin, pout = price_for(mcfg, peak)
    estimate = len(jobs) * (est_in * pin + est_out * 1.3 * pout) / 1e6
    ok, msg = budget.check(estimate, phase="materials", allow_reserve=False)
    print(f"[budget] {msg}")
    if not ok:
        raise SystemExit(f"BUDGET GUARD REFUSED: {msg}")

    results: dict[str, dict] = {}
    problems: list[str] = []
    async with OpenRouterClient(os.environ["OPENROUTER_API_KEY"]) as client:
        live = None
        try:
            await client.fetch_live_prices()
            live = client.live_price(mcfg)
        except Exception as e:  # noqa: BLE001
            print(f"[materials] live price fetch failed: {e}")
        if live:
            pin, pout = price_for(mcfg, peak, live)

        sem = asyncio.Semaphore(6)
        total_cost = 0.0

        async def one(job):
            nonlocal total_cost
            async with sem:
                call_id = jid(job)
                req_ts = datetime.now(timezone.utc).isoformat()
                base = {
                    "run_id": run_id, "call_id": call_id, "experiment": "materials_gen",
                    "model_key": model_key, "slug": mcfg.slug, "occupation_id": job["occ"],
                    "resume_ids": job["resume_id"], "request_ts": req_ts,
                }
                for attempt in range(1 + max_retries):
                    try:
                        resp = await client.chat(mcfg, job["prompt"])
                    except (RefusalError, TransportFailure) as e:
                        _append(log_path, {**base, "finish_reason": "error", "cost_usd": 0.0,
                                           "parse_ok": False, "refusal_flag": isinstance(e, RefusalError),
                                           "raw_response": "", "error": str(e)[:500]})
                        problems.append(f"{job['resume_id']}: transport/refusal {e}")
                        return
                    cost = resp["cost_usd"]
                    if cost is None:
                        cost = ((resp["input_tokens"] or 0) * pin + (resp["output_tokens"] or 0) * pout) / 1e6
                    total_cost += float(cost)
                    try:
                        obj = extract_json(resp["content"])
                    except Exception:
                        _append(log_path, {**base, "finish_reason": resp["finish_reason"], "cost_usd": cost,
                                           "parse_ok": False, "refusal_flag": False,
                                           "raw_response": resp["content"][:4000], "error": "no json"})
                        problems.append(f"{job['resume_id']}: no json")
                        continue
                    obj.setdefault("resume_id", job["resume_id"])
                    obj["resume_id"] = job["resume_id"]
                    obj["occupation_id"] = job["occ"]
                    obj["source"] = "kaggle" if job["kind"] == "structure" else "synthetic"
                    obj["role"] = job["role"]
                    violations = validate_resume(obj)
                    _append(log_path, {**base, "finish_reason": resp["finish_reason"], "cost_usd": cost,
                                       "parse_ok": True, "refusal_flag": False,
                                       "raw_response": resp["content"][:4000],
                                       "error": "; ".join(violations) or None})
                    if violations:
                        problems.append(f"{job['resume_id']}: {violations}")
                        if attempt < max_retries:
                            continue
                    results[job["resume_id"]] = obj
                    return
                return

        await asyncio.gather(*(one(j) for j in jobs))

    # freeze per-occupation files (only if all 6 present and valid)
    by_occ: dict[str, list[dict]] = {}
    for rid, obj in results.items():
        occ = obj["occupation_id"]
        by_occ.setdefault(occ, []).append(obj)
    for occ, items in by_occ.items():
        items.sort(key=lambda r: r["resume_id"])
        if len(items) == 6:
            out = MATERIALS_DIR / "base_resumes" / f"{occ}.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(items, indent=2, ensure_ascii=False))
        else:
            problems.append(f"{occ}: only {len(items)}/6 valid resumes; file NOT written")
    summary = {
        "run_id": run_id, "jobs": len(jobs), "valid": len(results),
        "cost_usd": round(total_cost, 4), "problems": problems,
    }
    (run_dir / "manifest.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"[materials] generated {len(results)}/{len(jobs)} valid; cost ${total_cost:.2f}")
    if problems:
        print(f"[materials] problems: {len(problems)}")
        for p in problems[:20]:
            print("  -", p)
    return summary


def run_materials(model_key: str, force: bool = False, pricing: str | None = None) -> None:
    jobs = build_jobs(force=force)
    if jobs:
        asyncio.run(generate_materials(model_key, jobs, pricing=pricing))
    # final validation of everything on disk
    failures = []
    for f in sorted((MATERIALS_DIR / "base_resumes").glob("*.json")):
        for r in json.loads(f.read_text()):
            for v in validate_resume(r):
                failures.append(f"{r['resume_id']}: {v}")
    if failures:
        raise SystemExit(f"RESUME VALIDATOR FAILED ({len(failures)}):\n" + "\n".join(failures[:40]))
    print("[materials] all frozen resumes pass the validator")
