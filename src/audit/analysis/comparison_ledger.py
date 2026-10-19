"""Emit the full comparison ledger (E1 scoring, E2 pair, E3 ranking) with explicit
comparators, main run (4 models) + phase-3 DeepSeek. Numbers pulled from
docs/report/stats.json and phase-3 run logs; nothing hand-typed."""
import json

import pandas as pd

from audit.analysis.phase3_stats import (
    cue_level_penalties,
    gender_preference,
    placebo_decomposition,
)

S = json.load(open("docs/report/stats.json"))
MODELS = ["deepseek_v41_flash", "claude_haiku_55", "gpt6_luna", "qwen38_flash"]
SHORT = {m: k for k, m in zip(["DS", "Haiku", "Luna", "Qwen"], MODELS)}


def e1_block() -> None:
    print("\n== E1 — SCORING: treatment cell minus `none` cell, same gender & occupation ==")
    print("(women; each model scores ONE candidate per call; salary excl. withheld $0)")
    print(f"{'':10} {'fit':>22} {'interview':>16} {'salary $':>24}")
    print(f"{'':10} {'parent':>10} {'gap':>10} {'parent':>7} {'gap':>7} {'parent':>11} {'gap':>11}")
    for m in MODELS:
        g = S["models"][m]["e1_gaps_women"]
        f, i, s = g["overall_fit"], g["interview"], g["starting_salary_usd"]
        print(f"{SHORT[m]:10} {f['parent_minus_none']:>10.2f} {f['parent_gap_minus_none']:>10.2f} "
              f"{i['parent_minus_none']:>7.3f} {i['parent_gap_minus_none']:>7.3f} "
              f"{s['parent_minus_none']:>11.0f} {s['parent_gap_minus_none']:>11.0f}")


def main() -> None:
    # ---- E1 ----
    e1_block()
    for m in MODELS:
        mm = S["models"][m]

    # ---- E2 main run ----
    print("\n== E2 — PAIR: P(treatment candidate chosen) vs the childless candidate in the SAME prompt ==")
    print("(parity = 0.50; cluster t-tests over 40 résumé-pair clusters; all |t| >= 5)")
    hdr = f"{'contrast':26}" + "".join(f"{SHORT[m]:>8}" for m in MODELS)
    rows = {}
    for con in ["parent", "parent_committed", "parent_gap"]:
        for g, gl in [("female", "mother"), ("male", "father")]:
            key = f"{con}|{g}"
            rows[f"{con} {gl}"] = [S["models"][m]["e2_clustered"]["cells"][key]["p"] for m in MODELS]
    print(hdr)
    for label, vals in rows.items():
        print(f"{label:26}" + "".join(f"{v:>8.3f}" for v in vals))

    print("\n== E2 mother minus father (same contrast, women's pairs minus men's pairs; Holm over 12 tests) ==")
    hdr2 = f"{'contrast':26}" + "".join(f"{SHORT[m]:>14}" for m in MODELS)
    print(hdr2)
    for con in ["parent", "parent_committed", "parent_gap"]:
        vals = [S["models"][m]["e2_clustered"]["gender_diff"][con]["mothers_minus_fathers"] for m in MODELS]
        holm = [S["gender_diff_holm"].get(f"{m}|{con}") for m in MODELS]
        print(f"{con:26}" + "".join((f"{v:>9.3f} H:{h:.2f}" if h is not None else f"{v:>14.3f}") for v, h in zip(vals, holm)))

    print("\n== E2 paired salary (mother minus her paired childless woman; withheld $0 excluded) ==")
    for m in MODELS:
        mm = S["models"][m]
        a, b = mm["e2_parent_salary_f"], mm["e2_parent_gap_salary_f"]
        print(f"{SHORT[m]:8} parent ${a['diff']:>6} ({a['pct']:+.2f}% of ${a['base']:,})   "
              f"leave gap ${b['diff']:>6} ({b['pct']:+.2f}% of ${b['base']:,})")

    # ---- E3 main run ----
    print("\n== E3 — RANKING: token parent vs THE SAME résumés shown childless (pools of 6) ==")
    print("(top-3 rate; naive = raw share ratio; adjusted = résumé-FE impact ratio)")
    for m in MODELS:
        fe = S["models"][m]["e3_fe"]
        f, ml = fe["F"], fe["M"]
        print(f"{SHORT[m]:8} mothers naive {f['naive_ratio']:.2f} -> FE {f['adjusted_ratio']:.2f} (t {f['fe_z']:.1f})   "
              f"fathers naive {ml['naive_ratio']:.2f} -> FE {ml['adjusted_ratio']:.2f} (t {ml['fe_z']:.1f})")

    # ---- phase 3 DeepSeek ----
    print("\n== PHASE 3 (DeepSeek only; other models running) ==")
    print("\nE2-v3 cue levels: P(parent chosen) vs paired childless candidate, by gender-explicitness")
    cl = cue_level_penalties("deepseek_v41_flash")
    piv = cl.pivot_table(index=["contrast"], columns=["level", "gender"], values="P(parent)")
    cols = [c for c in piv.columns if c[1] in ("female", "male", None)]
    print(piv[cols].round(3).to_string())

    print("\nE2-v3 placebo decomposition (P(treatment chosen), differences between conditions)")
    print(placebo_decomposition("deepseek_v41_flash").to_string(index=False))

    print("\nE2-v3 direct gender contrasts: P(woman chosen) vs the man in the same prompt (parity 0.50)")
    gp = gender_preference("deepseek_v41_flash")
    pw = gp[gp["stat"] == "P(woman chosen)"]
    print(pw.to_string(index=False))

    # E3-v3 top-3 ratio by cue level (naive; parent vs childless members within comp a/b pools)
    from audit.analysis.phase3_stats import _tables_for
    e3 = _tables_for("deepseek_v41_flash").get("e3")
    if e3 is not None and not e3.empty:
        print("\nE3-v3 top-3 ratio: token parent vs childless members, by cue level (comps a+b, naive)")
        for lvl in ["name", "name_field", "initial_field", "blind"]:
            sub = e3[(e3.cue_level == lvl) & (e3.composition.isin(["a", "b"]))]
            if sub.empty:
                continue
            par = sub[sub.parent == 1]["top3"].mean()
            non = sub[sub.parent == 0]["top3"].mean()
            print(f"  {lvl:14}: parent {par:.3f} / childless {non:.3f}  ratio {par/non:.2f}  (n={len(sub)//6} pools)")


if __name__ == "__main__":
    main()
