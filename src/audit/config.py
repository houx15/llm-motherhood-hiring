"""Config loading (pydantic v2) and repo paths."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
MATERIALS_DIR = DATA_DIR / "materials"
PLANS_DIR = DATA_DIR / "plans"
RUNS_DIR = ROOT / "runs"
PROMPTS_DIR = ROOT / "prompts"


class ProviderCfg(BaseModel):
    order: list[str] = Field(default_factory=list)
    allow_fallbacks: bool = False


class ModelCfg(BaseModel):
    key: str
    slug: str
    verified: bool = False
    provider: ProviderCfg = ProviderCfg()
    reasoning: dict[str, Any] = Field(default_factory=lambda: {"enabled": False})
    temperature: float | None = None
    max_tokens: int = 600
    price_per_mtok: dict[str, float] = Field(default_factory=dict)
    peak_multiplier: float = 1.0
    peak_hours_utc: list[str] | None = None

    def prices(self, peak: bool) -> tuple[float, float]:
        m = self.peak_multiplier if peak else 1.0
        return (
            self.price_per_mtok.get("input", 0.0) * m,
            self.price_per_mtok.get("output", 0.0) * m,
        )


class ModelsCfg(BaseModel):
    models: list[ModelCfg]


class BudgetCfg(BaseModel):
    total_cap_usd: float
    weekly_cap_usd: float | None = None
    reserve_usd: float
    phase_caps: dict[str, float]
    assume_peak_pricing: bool = True
    estimate_safety_factor: float = 1.15
    kill_switch: dict[str, Any] = Field(default_factory=dict)


class NamesCfg(BaseModel):
    female: list[str]
    male: list[str]
    surnames: list[str]

    def first_names(self, gender: Literal["female", "male"]) -> list[str]:
        return self.female if gender == "female" else self.male

    def full_name(self, gender: Literal["female", "male"], idx: int) -> str:
        return f"{self.first_names(gender)[idx]} {self.surnames[idx]}"


class Occupation(BaseModel):
    id: str
    title: str
    soc: str
    soc_aliases: list[str] = Field(default_factory=list)
    cell: dict[str, str]
    female_share: float | None = None
    median_wage: float | None = None
    time_demands: float | None = None
    in_e4: bool = False


class OccupationsCfg(BaseModel):
    occupations: list[Occupation] | None = None

    @classmethod
    def load(cls) -> "OccupationsCfg":
        raw = yaml.safe_load((CONFIG_DIR / "occupations.yaml").read_text())
        if isinstance(raw, dict):
            raw = raw.get("occupations", [])
        return cls(occupations=[Occupation(**o) for o in raw])

    def by_id(self) -> dict[str, Occupation]:
        return {o.id: o for o in self.occupations or []}


class ExperimentCfg(BaseModel):
    name: str
    phase: str
    enabled: bool = True
    models: list[str]
    occupations: str | list[str] = "all"  # "all" | "in_e4" | list of ids
    experiments: dict[str, Any] = Field(default_factory=dict)


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


@lru_cache(maxsize=None)
def load_models() -> ModelsCfg:
    return ModelsCfg(**_load_yaml(CONFIG_DIR / "models.yaml"))


@lru_cache(maxsize=None)
def load_budget() -> BudgetCfg:
    return BudgetCfg(**_load_yaml(CONFIG_DIR / "budget.yaml"))


@lru_cache(maxsize=None)
def load_names() -> NamesCfg:
    return NamesCfg(**_load_yaml(CONFIG_DIR / "names.yaml"))


@lru_cache(maxsize=None)
def load_family_cues() -> dict:
    return _load_yaml(CONFIG_DIR / "family_cues.yaml")


@lru_cache(maxsize=None)
def load_jd_variants() -> dict:
    return _load_yaml(CONFIG_DIR / "jd_variants.yaml")["variants"]


@lru_cache(maxsize=None)
def load_refusal_patterns() -> list[str]:
    return _load_yaml(CONFIG_DIR / "refusal_patterns.yaml")["patterns"]


@lru_cache(maxsize=None)
def load_benchmarks() -> dict:
    return _load_yaml(CONFIG_DIR / "benchmarks.yaml")


def load_experiment(name: str) -> ExperimentCfg:
    path = CONFIG_DIR / "experiments" / f"{name}.yaml"
    return ExperimentCfg(**_load_yaml(path))


def load_occupations_built() -> OccupationsCfg:
    """Occupations with moderators filled (data/materials/occupations.json)."""
    path = MATERIALS_DIR / "occupations.json"
    if path.exists():
        import json

        return OccupationsCfg(occupations=[Occupation(**o) for o in json.loads(path.read_text())])
    return OccupationsCfg.load()
