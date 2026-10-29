from pathlib import Path

import pytest

from adult_dashboard.data import load_dataset

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "adult.csv"


@pytest.fixture(scope="session")
def dataset():
    """Cleaned dataset and its quality report, loaded once per test session."""
    return load_dataset(DATA_PATH)


@pytest.fixture(scope="session")
def df(dataset):
    return dataset[0]
