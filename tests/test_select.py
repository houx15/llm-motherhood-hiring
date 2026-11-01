"""Round 14 guard: no run_id substring selection in the analysis layer."""
import re
import subprocess
import sys
from pathlib import Path


def test_no_phase_substring_selection():
    """run_id.str.contains('phase...') admits phase-4 rows and repair runs;
    selection must go through audit.analysis.select (call-id membership)."""
    bad = []
    for p in Path("src/audit").rglob("*.py"):
        if p.name == "select.py":
            continue
        for i, line in enumerate(p.read_text().splitlines(), 1):
            if re.search(r'str\.contains\(\s*["\']phase', line):
                bad.append(f"{p}:{i}: {line.strip()}")
    assert not bad, "substring phase selection found:\n" + "\n".join(bad)


def test_select_membership_counts():
    from audit.analysis.select import main_run_ids, phase3_ids, phase4_ids

    assert len(main_run_ids()) > 200_000
    assert len(phase3_ids()) > 300_000
    assert len(phase4_ids()) == 48_000
    assert not (main_run_ids() & phase3_ids()), "main/p3 id overlap"
    assert not (main_run_ids() & phase4_ids()), "main/p4 id overlap"
