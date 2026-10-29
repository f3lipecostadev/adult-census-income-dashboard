import pandas as pd
import pytest

from adult_dashboard.data import UNKNOWN_LABEL, clean_dataset, load_dataset


def test_quality_report_matches_the_official_dataset(dataset):
    _, report = dataset
    assert report.raw_rows == 48_842
    assert report.columns == 15
    assert report.missing_cells == 6_465
    assert report.duplicate_rows == 52
    assert report.clean_rows == 48_790


def test_cleaned_dataset_has_no_missing_values(df):
    assert df.isna().sum().sum() == 0


def test_column_types_are_inferred_correctly(df):
    numeric = df.select_dtypes(include="number").columns.tolist()
    assert numeric == [
        "age", "fnlwgt", "education-num", "capital-gain", "capital-loss", "hours-per-week",
    ]  # fmt: skip
    categorical = df.columns.difference(numeric)
    assert all(isinstance(df[c].dtype, pd.CategoricalDtype) for c in categorical)


def test_income_labels_are_normalized(df):
    assert sorted(df["income"].unique()) == ["<=50K", ">50K"]


def test_missing_text_values_become_unknown(df):
    assert UNKNOWN_LABEL in df["workclass"].cat.categories


def test_clean_dataset_handles_whitespace_numeric_nulls_and_duplicates():
    raw = pd.DataFrame(
        {
            "age": [30, 30, None, 50],
            "workclass": [" Private", " Private", None, "Gov "],
            "income": [" <=50K.", " <=50K.", ">50K", ">50K"],
        }
    )
    clean = clean_dataset(raw)
    assert len(clean) == 3  # one exact duplicate dropped
    assert clean["age"].tolist() == [30.0, 40.0, 50.0]  # null -> median of 30 and 50
    assert clean["workclass"].tolist() == ["Private", UNKNOWN_LABEL, "Gov"]
    assert clean["income"].tolist() == ["<=50K", ">50K", ">50K"]


def test_load_dataset_raises_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_dataset(tmp_path / "does-not-exist.csv")
