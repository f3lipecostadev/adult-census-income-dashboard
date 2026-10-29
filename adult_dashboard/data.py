"""Loading and cleaning of the UCI Adult (Census Income) dataset."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

MISSING_MARKERS = ["?"]
UNKNOWN_LABEL = "Desconhecido"


@dataclass(frozen=True)
class QualityReport:
    """Data-quality figures measured on the raw file, before any cleaning."""

    raw_rows: int
    columns: int
    missing_cells: int
    duplicate_rows: int
    clean_rows: int


def clean_dataset(raw: pd.DataFrame) -> pd.DataFrame:
    """Apply the cleaning rules and return a new DataFrame.

    * exact duplicate rows are dropped;
    * numeric missing values are filled with the column median (none in this dataset);
    * text columns are stripped, the ``income`` labels lose any trailing period, missing
      values become ``"Desconhecido"`` and the columns are converted to ``category``.
    """
    df = raw.drop_duplicates().copy()

    numeric = df.select_dtypes(include="number").columns
    df[numeric] = df[numeric].fillna(df[numeric].median())

    for column in df.select_dtypes(exclude="number").columns:
        text = df[column].str.strip()
        if column == "income":
            text = text.str.rstrip(".")
        df[column] = text.fillna(UNKNOWN_LABEL).astype("category")

    return df.reset_index(drop=True)


def load_dataset(path: Path | str) -> tuple[pd.DataFrame, QualityReport]:
    """Read the CSV and return the cleaned DataFrame with its quality report.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
    """
    raw = pd.read_csv(path, skipinitialspace=True, na_values=MISSING_MARKERS)
    clean = clean_dataset(raw)
    report = QualityReport(
        raw_rows=len(raw),
        columns=raw.shape[1],
        missing_cells=int(raw.isna().sum().sum()),
        duplicate_rows=int(raw.duplicated().sum()),
        clean_rows=len(clean),
    )
    return clean, report
