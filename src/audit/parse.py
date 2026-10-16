"""Response parsing: pydantic validation per experiment, fenced-JSON extraction,
refusal detection. No clamping — out-of-range = parse failure (spec §9)."""
from __future__ import annotations

import json
import re

from pydantic import BaseModel, Field, field_validator

from .config import load_refusal_patterns

RATING_KEYS = ["competence", "commitment", "promotability", "likability"]


def _to_int(v):
    if isinstance(v, bool):
        raise ValueError("boolean where integer expected")
    if isinstance(v, str):
        s = v.strip().replace("$", "").replace(",", "")
        if not s:
            raise ValueError("empty numeric string")
        return int(float(s))
    return int(v)


def _to_bool(v):
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in ("true", "yes", "1"):
        return True
    if s in ("false", "no", "0"):
        return False
    raise ValueError(f"not a boolean: {v!r}")


class Ratings(BaseModel):
    competence: int
    commitment: int
    promotability: int
    likability: int

    @field_validator("*", mode="before")
    @classmethod
    def _int(cls, v):
        return _to_int(v)


class E1Output(BaseModel):
    """E1 + E4 scoring output."""
    overall_fit: int
    interview: bool
    starting_salary_usd: int
    competence: int
    commitment: int
    promotability: int
    likability: int
    rationale: str = ""

    @field_validator("overall_fit", "competence", "commitment", "promotability", "likability", mode="before")
    @classmethod
    def _int(cls, v):
        return _to_int(v)

    @field_validator("starting_salary_usd", mode="before")
    @classmethod
    def _salary(cls, v):
        return _to_int(v)

    @field_validator("overall_fit")
    @classmethod
    def _fit_range(cls, v):
        if not 1 <= v <= 10:
            raise ValueError(f"overall_fit out of range: {v}")
        return v

    @field_validator("competence", "commitment", "promotability", "likability")
    @classmethod
    def _rating_range(cls, v):
        if not 1 <= v <= 7:
            raise ValueError(f"rating out of range: {v}")
        return v

    @field_validator("interview", mode="before")
    @classmethod
    def _bool(cls, v):
        return _to_bool(v)

    @field_validator("starting_salary_usd")
    @classmethod
    def _salary_range(cls, v):
        if not 0 <= v <= 2_000_000:
            raise ValueError(f"salary out of range: {v}")
        return v


class SideInfo(BaseModel):
    overall_fit: int
    starting_salary_usd: int
    competence: int
    commitment: int
    promotability: int
    likability: int

    @field_validator("*", mode="before")
    @classmethod
    def _int(cls, v):
        return _to_int(v)

    @field_validator("overall_fit")
    @classmethod
    def _fit(cls, v):
        if not 1 <= v <= 10:
            raise ValueError(f"overall_fit out of range: {v}")
        return v

    @field_validator("competence", "commitment", "promotability", "likability")
    @classmethod
    def _rating(cls, v):
        if not 1 <= v <= 7:
            raise ValueError(f"rating out of range: {v}")
        return v


class E2Output(BaseModel):
    chosen: str
    A: SideInfo
    B: SideInfo
    rationale: str = ""

    @field_validator("chosen", mode="before")
    @classmethod
    def _chosen(cls, v):
        s = str(v).strip().upper()
        if s not in ("A", "B"):
            raise ValueError(f"chosen must be A or B: {v!r}")
        return s


class E3Output(BaseModel):
    ranking: list[str]
    top_reason: str = ""

    @field_validator("ranking", mode="before")
    @classmethod
    def _rank(cls, v):
        if not isinstance(v, list):
            raise ValueError("ranking must be a list")
        return [str(x).strip().upper() for x in v]


class ManipOutput(BaseModel):
    """Phase-3 gender-perception manipulation check."""
    perceived_gender: str

    @field_validator("perceived_gender", mode="before")
    @classmethod
    def _gender(cls, v):
        s = str(v).strip().lower()
        if s not in ("female", "male", "unknown"):
            raise ValueError(f"perceived_gender must be female/male/unknown: {v!r}")
        return s


SCHEMAS = {"e1": E1Output, "e4": E1Output, "e2": E2Output, "e3": E3Output, "manip": ManipOutput}

FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)
OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_json(text: str) -> dict:
    """Extract the first JSON object, from a fenced block if present."""
    if not text:
        raise ValueError("empty response")
    m = FENCE_RE.search(text)
    candidates = []
    if m:
        candidates.append(m.group(1).strip())
    candidates.append(text.strip())
    for cand in candidates:
        try:
            obj = json.loads(cand)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            om = OBJ_RE.search(cand)
            if om:
                try:
                    obj = json.loads(om.group(0))
                    if isinstance(obj, dict):
                        return obj
                except json.JSONDecodeError:
                    continue
    raise ValueError("no JSON object found")


def is_refusal(text: str) -> bool:
    t = (text or "").lower()
    return any(p.lower() in t for p in load_refusal_patterns())


def parse_response(experiment: str, text: str, expected_labels: list[str] | None = None):
    """Returns (parsed_dict | None, parse_ok: bool, refusal_flag: bool, error: str | None)."""
    try:
        obj = extract_json(text)
    except Exception as e:  # noqa: BLE001
        refusal = is_refusal(text)
        return None, False, refusal, f"extract: {e}"
    schema = SCHEMAS.get(experiment)
    if schema is None:
        return obj, True, False, None
    try:
        parsed = schema.model_validate(obj)
    except Exception as e:  # noqa: BLE001
        refusal = is_refusal(text)
        return None, False, refusal, f"validate: {e}"
    if experiment == "e3":
        labels = parsed.ranking
        expected = expected_labels or [f"C{i}" for i in range(1, 7)]
        if sorted(labels) != sorted(expected):
            return None, False, False, f"ranking not a permutation of {expected}: {labels}"
    return parsed.model_dump(), True, False, None
