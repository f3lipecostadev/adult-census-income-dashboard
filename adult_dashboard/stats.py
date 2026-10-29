"""Descriptive-statistics helpers: Tukey outliers, skewness and correlation labels."""

from __future__ import annotations

from typing import Literal, NamedTuple

import pandas as pd

SKEW_THRESHOLD = 0.5
STRONG_CORRELATION = 0.7
MODERATE_CORRELATION = 0.4


class TukeyLimits(NamedTuple):
    """Quartiles, IQR and the fences used by Tukey's rule."""

    q1: float
    q3: float
    iqr: float
    lower: float
    upper: float


def tukey_limits(series: pd.Series, factor: float = 1.5) -> TukeyLimits:
    """Compute ``Q1 - factor * IQR`` and ``Q3 + factor * IQR``.

    Quartiles use pandas' default linear interpolation. Textbook examples that take the
    median of each half of the data can give slightly different quartiles for small samples.
    """
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    return TukeyLimits(q1, q3, iqr, q1 - factor * iqr, q3 + factor * iqr)


def find_outliers(series: pd.Series, limits: TukeyLimits | None = None) -> pd.Series:
    """Return the values of ``series`` that fall outside the Tukey fences."""
    limits = limits or tukey_limits(series)
    return series[(series < limits.lower) | (series > limits.upper)]


def skew_direction(g1: float) -> Literal["symmetric", "positive", "negative"]:
    """Classify the Fisher-Pearson skewness coefficient (``|g1| <= 0.5`` is symmetric)."""
    if abs(g1) <= SKEW_THRESHOLD:
        return "symmetric"
    return "positive" if g1 > 0 else "negative"


def correlation_strength(r: float) -> Literal["strong", "moderate", "weak"]:
    """Classify ``|r|``: strong from 0.7, moderate from 0.4, otherwise weak."""
    if abs(r) >= STRONG_CORRELATION:
        return "strong"
    if abs(r) >= MODERATE_CORRELATION:
        return "moderate"
    return "weak"
