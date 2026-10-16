"""Statistical helpers for the report: CIs, tests, standardized effects,
Correll et al. (2007) benchmark comparison, cross-model meta-summary."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

Z95 = 1.959963984540054


def wilson_ci(k: int | float, n: int, z: float = Z95) -> tuple[float, float, float]:
    """Wilson score interval for a proportion. Returns (p, lo, hi)."""
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return p, max(0.0, center - half), min(1.0, center + half)


def binom_test_phalf(k: int, n: int) -> float:
    """Two-sided exact binomial test of H0: p = 0.5 (normal approx, fine for n>=30)."""
    if n == 0:
        return float("nan")
    p = k / n
    se = math.sqrt(0.25 / n)
    z = (p - 0.5) / se
    return 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


def paired_d(x: pd.Series) -> tuple[float, float, float, int]:
    """Mean paired difference with 95% CI and standardized d (mean / sd).

    Returns (mean, ci_lo, ci_hi, n)."""
    x = x.dropna()
    n = len(x)
    if n < 2:
        return float("nan"), float("nan"), float("nan"), n
    m = x.mean()
    se = x.std(ddof=1) / math.sqrt(n)
    return m, m - Z95 * se, m + Z95 * se, n


def cohens_d_from_means(m1, sd1, n1, m2, sd2, n2):
    """d = (m1 - m2) / pooled sd."""
    sp = math.sqrt(((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / max(n1 + n2 - 2, 1))
    return (m1 - m2) / sp if sp else float("nan")


def meta_summary(effects: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    """Inverse-variance fixed-effects meta-analysis of (coef, se) pairs.

    Returns (pooled, se, z, heterogeneity_I2_percent)."""
    eff = [(c, s) for c, s in effects if np.isfinite(c) and np.isfinite(s) and s > 0]
    if len(eff) < 2:
        c, s = eff[0]
        return c, s, c / s, 0.0
    w = np.array([1 / s**2 for _, s in eff])
    coefs = np.array([c for c, _ in eff])
    pooled = (w * coefs).sum() / w.sum()
    se = math.sqrt(1 / w.sum())
    q = (w * (coefs - pooled) ** 2).sum()
    dof = len(eff) - 1
    i2 = max(0.0, (q - dof) / q * 100) if q > 0 else 0.0
    return float(pooled), float(se), float(pooled / se), float(i2)


def correll_comparison(our_salary_pct: float, our_interview_pp: float) -> pd.DataFrame:
    """Side-by-side with Correll, Benard & Paik (2007) lab benchmarks
    (config/benchmarks.yaml values; mothers vs childless women)."""
    rows = [
        ("Recommended salary (% vs childless women)", -7.4, our_salary_pct),
        ("Recommend hire / interview (pp vs childless women)", -27.0, our_interview_pp),
        ("Competence (std. diff, approx.)", -0.36, float("nan")),
        ("Commitment (std. diff, approx.)", -0.87, float("nan")),
    ]
    return pd.DataFrame(rows, columns=["Outcome", "Correll et al. 2007 (human lab)", "This audit (LLM, mother vs childless)"])
