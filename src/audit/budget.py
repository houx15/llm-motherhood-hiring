"""Budget estimation + hard cap enforcement (spec §7). The ledger is the source
of truth for spent_so_far — never memory."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from .config import RUNS_DIR, BudgetCfg, ModelCfg, load_budget

# Default token estimates per call (input, output) before pilot measurement (spec §7).
TOKEN_EST = {
    "e1": (1300, 300),
    "e2": (2100, 350),
    "e3": (4850, 200),
    "e4": (1350, 300),
    "e5": (1000, 700),
    "pretest": (1300, 300),
    "materials_gen": (1500, 700),
}


def estimate_cost(
    plan: pd.DataFrame,
    price_in: float,
    price_out: float,
    safety: float = 1.0,
) -> float:
    """Estimated USD for a plan given per-Mtok prices."""
    total = 0.0
    for exp, grp in plan.groupby("experiment"):
        in_tok, out_tok = TOKEN_EST.get(exp, (1500, 400))
        n = len(grp)
        total += n * (in_tok * price_in + out_tok * safety * price_out) / 1e6
    return total


class Ledger:
    """Append-only ledger across runs; rebuilt from per-run JSONL logs (raw logs
    are never modified)."""

    def __init__(self, runs_dir: Path = RUNS_DIR):
        self.runs_dir = runs_dir
        self.parquet = runs_dir / "ledger.parquet"

    def load(self) -> pd.DataFrame:
        rows: list[dict] = []
        for f in sorted(self.runs_dir.glob("*/logs.jsonl")):
            for line in f.read_text().splitlines():
                try:
                    r = json.loads(line)
                    if r.get("cost_usd") is not None:
                        rows.append(
                            {
                                "run_id": r.get("run_id"),
                                "call_id": r.get("call_id"),
                                "experiment": r.get("experiment"),
                                "model_key": r.get("model_key"),
                                "cost_usd": float(r.get("cost_usd") or 0),
                                "request_ts": r.get("request_ts"),
                                "parse_ok": bool(r.get("parse_ok")),
                            }
                        )
                except json.JSONDecodeError:
                    continue
        return pd.DataFrame(rows)

    def spent_total(self) -> float:
        df = self.load()
        return float(df["cost_usd"].sum()) if not df.empty else 0.0

    def spent_since(self, since: datetime) -> float:
        df = self.load()
        if df.empty:
            return 0.0
        ts = pd.to_datetime(df["request_ts"], errors="coerce", utc=True)
        mask = ts >= pd.Timestamp(since)
        return float(df.loc[mask, "cost_usd"].sum())

    def flush(self, df: pd.DataFrame) -> None:
        """Write consolidated ledger parquet (safe to rewrite; raw JSONL is canonical)."""
        if df.empty:
            return
        if self.parquet.exists():
            old = pd.read_parquet(self.parquet)
            df = pd.concat([old, df]).drop_duplicates(subset=["run_id", "call_id"])
        self.parquet.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(self.parquet, index=False)


def deepseek_off_peak(now: datetime | None = None) -> bool:
    """DeepSeek peak = UTC 00:30-16:30; off-peak = 16:30-00:30."""
    now = now or datetime.now(timezone.utc)
    mins = now.hour * 60 + now.minute
    return not (30 <= mins < 16 * 60 + 30)


class BudgetGuard:
    def __init__(self, cfg: BudgetCfg | None = None):
        self.cfg = cfg or load_budget()
        self.ledger = Ledger()

    def check(
        self,
        estimate: float,
        phase: str | None = None,
        allow_reserve: bool = False,
        run_spend_so_far: float = 0.0,
    ) -> tuple[bool, str]:
        c = self.cfg
        spent = self.ledger.spent_total()
        weekly_cap = c.weekly_cap_usd
        spent_week = self.ledger.spent_since(datetime.now(timezone.utc) - timedelta(days=7)) if weekly_cap else 0.0
        limit = c.total_cap_usd - (0 if allow_reserve else c.reserve_usd)
        msgs = [
            f"spent={spent:.2f} weekly={spent_week:.2f} reserve={c.reserve_usd:.2f} "
            f"limit={limit:.2f} estimate={estimate:.2f} (+run so far {run_spend_so_far:.2f})"
        ]
        if spent + run_spend_so_far + estimate > limit:
            return False, "OVER TOTAL CAP (minus reserve): " + msgs[0]
        if weekly_cap and spent_week + run_spend_so_far + estimate > weekly_cap:
            return False, "OVER WEEKLY CAP: " + msgs[0]
        if phase and phase in c.phase_caps:
            phase_cap = c.phase_caps[phase]
            if run_spend_so_far + estimate > phase_cap:
                return False, f"OVER PHASE CAP ({phase}: {phase_cap}): " + msgs[0]
        return True, "OK: " + msgs[0]

    def kill_switch(
        self, estimate: float, run_actual: float, cumulative_spent: float
    ) -> tuple[bool, str]:
        c = self.cfg
        overrun = c.kill_switch.get("overrun_fraction", 0.20)
        limit = c.total_cap_usd - c.reserve_usd
        if run_actual > estimate * (1 + overrun):
            return True, f"run actual {run_actual:.2f} > estimate*{1+overrun:.2f} {estimate:.2f}"
        if cumulative_spent >= limit:
            return True, f"cumulative {cumulative_spent:.2f} reached cap-reserve {limit:.2f}"
        return False, ""

    def status_line(self) -> str:
        c = self.cfg
        spent = self.ledger.spent_total()
        week = self.ledger.spent_since(datetime.now(timezone.utc) - timedelta(days=7))
        return (
            f"cap={c.total_cap_usd:.2f} spent={spent:.2f} "
            f"weekly={week:.2f}/{c.weekly_cap_usd or '-'} reserve={c.reserve_usd:.2f} "
            f"remaining={c.total_cap_usd - spent:.2f}"
        )


def price_for(cfg: ModelCfg, peak: bool, live: tuple[float, float] | None = None) -> tuple[float, float]:
    pin, pout = cfg.prices(peak)
    if live:
        # live prices are off-peak now (OpenRouter returns current price); scale for peak
        lin, lout = live
        if peak:
            lin *= cfg.peak_multiplier
            lout *= cfg.peak_multiplier
        pin, pout = max(pin, lin), max(pout, lout)
    return pin, pout
