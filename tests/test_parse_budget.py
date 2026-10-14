import json
from pathlib import Path

import pandas as pd
import pytest

from audit.budget import BudgetGuard, Ledger, estimate_cost
from audit.config import BudgetCfg
from audit.parse import E1Output, E2Output, E3Output, extract_json, is_refusal, parse_response

GOOD = """```json
{"overall_fit": 8, "interview": true, "starting_salary_usd": "95000",
 "competence": "6", "commitment": 5, "promotability": 6, "likability": 7,
 "rationale": "Strong experience."}
```"""

MALFORMED = "Here is my evaluation: {overall_fit: 8-ish, ...} great candidate!"
REFUSAL = "I'm sorry, but I cannot evaluate candidates based on personal characteristics."


def test_parse_valid_fenced():
    parsed, ok, refusal, err = parse_response("e1", GOOD)
    assert ok and not refusal
    assert parsed["overall_fit"] == 8
    assert parsed["interview"] is True
    assert parsed["competence"] == 6  # coerced from string
    assert parsed["starting_salary_usd"] == 95000


def test_parse_malformed_is_failure_not_refusal():
    parsed, ok, refusal, err = parse_response("e1", MALFORMED)
    assert not ok and not refusal and err


def test_parse_refusal_flag():
    assert is_refusal(REFUSAL)
    parsed, ok, refusal, err = parse_response("e1", REFUSAL)
    assert not ok and refusal


def test_parse_out_of_range_fails_no_clamp():
    bad = json.dumps(
        {"overall_fit": 11, "interview": True, "starting_salary_usd": 1,
         "competence": 6, "commitment": 5, "promotability": 6, "likability": 7,
         "rationale": ""}
    )
    parsed, ok, refusal, err = parse_response("e1", bad)
    assert not ok and "range" in str(err)


def test_parse_e2():
    obj = {
        "chosen": "a",
        "A": {"overall_fit": 7, "starting_salary_usd": 90000, "competence": 5,
               "commitment": 5, "promotability": 5, "likability": 6},
        "B": {"overall_fit": 8, "starting_salary_usd": 95000, "competence": 6,
               "commitment": 6, "promotability": 6, "likability": 6},
        "rationale": "B stronger",
    }
    parsed, ok, refusal, err = parse_response("e2", "```json\n" + json.dumps(obj) + "\n```")
    assert ok and parsed["chosen"] == "A"  # coerced to upper


def test_parse_e3_permutation():
    good = json.dumps({"ranking": ["C2", "C1", "C6", "C3", "C5", "C4"], "top_reason": "x"})
    parsed, ok, refusal, err = parse_response("e3", good)
    assert ok
    bad = json.dumps({"ranking": ["C1", "C1", "C6", "C3", "C5", "C4"], "top_reason": "x"})
    parsed, ok, refusal, err = parse_response("e3", bad)
    assert not ok and "permutation" in err


def test_extract_json_plain():
    assert extract_json('{"a": 1}') == {"a": 1}
    assert extract_json('prefix text {"a": {"b": 2}} suffix') == {"a": {"b": 2}}


# ---------------- budget guard ----------------


def _guard(tmp_path, spent_rows):
    (tmp_path / "run").mkdir(parents=True, exist_ok=True)
    with (tmp_path / "run" / "logs.jsonl").open("w") as f:
        for i, (ts, cost) in enumerate(spent_rows):
            f.write(json.dumps({"run_id": "run", "call_id": str(i), "cost_usd": cost,
                                "request_ts": ts, "parse_ok": True}) + "\n")
    cfg = BudgetCfg(
        total_cap_usd=200.0, weekly_cap_usd=200.0, reserve_usd=20.0,
        phase_caps={"pilot": 5.0, "phase1_deepseek": 35.0},
        assume_peak_pricing=True, estimate_safety_factor=1.15, kill_switch={},
    )
    g = BudgetGuard.__new__(BudgetGuard)
    g.cfg = cfg
    g.ledger = Ledger(runs_dir=tmp_path)
    return g


def test_budget_guard_refuses_over_cap(tmp_path):
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc).isoformat()
    g = _guard(tmp_path, [(now, 100.0)] * 2)  # spent 200? -> use 2x100=200
    ok, msg = g.check(1.0, phase="pilot")
    assert not ok


def test_budget_guard_reserve_blocks_until_approved(tmp_path):
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    g = _guard(tmp_path, [(now, 170.0)])  # spent 170; cap-reserve = 180
    ok, _ = g.check(15.0, allow_reserve=False)
    assert not ok  # 185 > 180 (cap - reserve)
    ok, _ = g.check(15.0, allow_reserve=True)
    assert ok  # 185 <= 200 total cap once reserve is explicitly allowed
    ok, _ = g.check(31.0, allow_reserve=True)
    assert not ok  # 201 > 200 hard cap


def test_budget_guard_phase_cap(tmp_path):
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    g = _guard(tmp_path, [(now, 1.0)])
    ok, _ = g.check(6.0, phase="pilot")  # 1 + 6 > pilot cap 5
    assert not ok
    ok, _ = g.check(3.5, phase="pilot")
    assert ok


def test_kill_switch_overrun():
    cfg = BudgetCfg(total_cap_usd=200, weekly_cap_usd=200, reserve_usd=20,
                    phase_caps={}, estimate_safety_factor=1.0,
                    kill_switch={"overrun_fraction": 0.2})
    g = BudgetGuard.__new__(BudgetGuard)
    g.cfg = cfg
    g.ledger = None
    hit, why = g.kill_switch(estimate=1.0, run_actual=1.3, cumulative_spent=5)
    assert hit and "estimate" in why
    hit, _ = g.kill_switch(estimate=1.0, run_actual=1.1, cumulative_spent=185)
    assert hit  # cumulative reached cap-reserve
    hit, _ = g.kill_switch(estimate=1.0, run_actual=1.1, cumulative_spent=100)
    assert not hit
