import math

import pandas as pd
import pytest

from adult_dashboard.formatting import format_br, format_int
from adult_dashboard.stats import (
    correlation_strength,
    find_outliers,
    skew_direction,
    tukey_limits,
)

# Textbook example: seven days of sales, with 100 as the obvious outlier.
SALES = pd.Series([10, 15, 20, 25, 30, 35, 100])


def test_tukey_limits_use_pandas_linear_quartiles():
    limits = tukey_limits(SALES)
    assert (limits.q1, limits.q3, limits.iqr) == (17.5, 32.5, 15.0)
    assert (limits.lower, limits.upper) == (-5.0, 55.0)


def test_find_outliers_flags_only_the_extreme_value():
    assert find_outliers(SALES).tolist() == [100]


def test_no_outliers_in_symmetric_data():
    assert find_outliers(pd.Series(range(1, 11))).empty


@pytest.mark.parametrize(
    ("g1", "expected"),
    [(0.0, "symmetric"), (0.5, "symmetric"), (-0.5, "symmetric"),
     (0.56, "positive"), (11.9, "positive"), (-0.6, "negative")],
)  # fmt: skip
def test_skew_direction_thresholds(g1, expected):
    assert skew_direction(g1) == expected


@pytest.mark.parametrize(
    ("r", "expected"),
    [(0.0, "weak"), (0.39, "weak"), (0.4, "moderate"), (-0.69, "moderate"),
     (0.7, "strong"), (-0.99, "strong")],
)  # fmt: skip
def test_correlation_strength_thresholds(r, expected):
    assert correlation_strength(r) == expected


def test_format_br():
    assert format_br(1234.567) == "1.234,57"
    assert format_br(0.1439, 3) == "0,144"
    assert format_int(48842) == "48.842"
    assert format_br(math.nan) == "—"
