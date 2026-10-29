"""Pin the figures quoted in adult_dashboard/findings.py to the actual data."""

import numpy as np
import pytest

from adult_dashboard.stats import find_outliers, tukey_limits


@pytest.fixture(scope="module")
def numeric(df):
    return df.select_dtypes(include="number")


@pytest.mark.parametrize(
    ("column", "g1"),
    [("capital-gain", 11.89), ("capital-loss", 4.57), ("fnlwgt", 1.44),
     ("age", 0.56), ("hours-per-week", 0.24), ("education-num", -0.31)],
)  # fmt: skip
def test_skewness(numeric, column, g1):
    assert round(numeric[column].skew(), 2) == g1


def test_zero_inflation_of_capital_columns(df):
    assert round(100 * (df["capital-gain"] == 0).mean(), 1) == 91.7
    assert round(100 * (df["capital-loss"] == 0).mean(), 1) == 95.3
    assert round(df["capital-gain"].mean()) == 1080
    positive = df.loc[df["capital-gain"] > 0, "capital-gain"]
    assert len(positive) == 4035
    assert positive.median() == 7298


@pytest.mark.parametrize(
    ("column", "count", "percent"),
    [("hours-per-week", 13_486, 27.6), ("capital-gain", 4035, 8.3), ("capital-loss", 2282, 4.7),
     ("education-num", 1787, 3.7), ("fnlwgt", 1453, 3.0), ("age", 215, 0.4)],
)  # fmt: skip
def test_tukey_outliers(numeric, column, count, percent):
    outliers = find_outliers(numeric[column])
    assert len(outliers) == count
    assert round(100 * len(outliers) / len(numeric), 1) == percent


def test_tukey_context_quoted_in_text(numeric):
    assert tukey_limits(numeric["age"]).upper == 78
    assert tukey_limits(numeric["education-num"]).lower == 4.5
    assert tukey_limits(numeric["capital-gain"]).iqr == 0
    assert tukey_limits(numeric["hours-per-week"]).iqr == 5
    assert round(100 * (numeric["hours-per-week"] == 40).mean(), 1) == 46.7


def test_ceiling_values(df):
    gains = df["capital-gain"]
    assert (gains == 99_999).sum() == 244
    assert gains[gains < 99_999].max() == 41_310
    assert (df["age"] == 90).sum() == 54
    assert (df["age"] == 89).sum() == 2


def test_correlations_are_all_weak(numeric):
    upper = np.triu(np.ones((len(numeric.columns),) * 2, dtype=bool), k=1)
    pearson = numeric.corr().where(upper).abs()
    spearman = numeric.corr(method="spearman").where(upper).abs()
    assert round(pearson.max().max(), 3) == 0.144
    assert round(spearman.max().max(), 3) == 0.165
    assert round(numeric["education-num"].corr(numeric["hours-per-week"]), 2) == 0.14
    assert round(numeric["age"].corr(numeric["hours-per-week"], method="spearman"), 2) == 0.15


def test_income_profile(df):
    assert round(100 * (df["income"] == ">50K").mean(), 1) == 23.9
    medians = df.groupby("income", observed=True)[["age", "education-num", "hours-per-week"]]
    medians = medians.median()
    assert medians.loc[">50K"].tolist() == [43, 12, 40]
    assert medians.loc["<=50K"].tolist() == [34, 9, 40]
    gain_share = df.groupby("income", observed=True)["capital-gain"].apply(lambda s: (s > 0).mean())
    assert round(100 * gain_share[">50K"], 1) == 21.3
    assert round(100 * gain_share["<=50K"], 1) == 4.2
    means = df.groupby("income", observed=True)["hours-per-week"].mean()
    assert (round(means[">50K"], 1), round(means["<=50K"], 1)) == (45.5, 38.8)
