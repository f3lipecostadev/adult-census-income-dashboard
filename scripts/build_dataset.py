"""Build ``data/adult.csv`` from the original UCI Adult files.

The UCI "Adult" (Census Income) dataset is distributed as two files, ``adult.data``
(training split) and ``adult.test`` (test split), without a header row. This script
concatenates both splits, assigns the column names from the dataset documentation and
normalizes two quirks of the raw files:

* ``adult.test`` has a non-data first line (``|1x3 Cross validator``) that is skipped;
* ``adult.test`` writes the ``income`` labels with a trailing period (``<=50K.``).

Missing values (``?`` in the raw files) are written as empty cells. No row is dropped here;
cleaning decisions (duplicates, missing values) are made, and reported, by the dashboard.

Usage::

    python scripts/build_dataset.py --train adult.data --test adult.test --output data/adult.csv

Download the raw files from https://archive.ics.uci.edu/dataset/2/adult (Data Folder).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

COLUMNS = [
    "age",
    "workclass",
    "fnlwgt",
    "education",
    "education-num",
    "marital-status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "capital-gain",
    "capital-loss",
    "hours-per-week",
    "native-country",
    "income",
]


def _read_split(path: Path, skiprows: int = 0) -> pd.DataFrame:
    return pd.read_csv(
        path,
        names=COLUMNS,
        skipinitialspace=True,
        na_values="?",
        skiprows=skiprows,
    )


def build_dataset(train_path: Path, test_path: Path) -> pd.DataFrame:
    """Concatenate the train and test splits into a single, header-labelled DataFrame."""
    train = _read_split(Path(train_path))
    test = _read_split(Path(test_path), skiprows=1)
    test["income"] = test["income"].str.rstrip(".")
    return pd.concat([train, test], ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--train", type=Path, required=True, help="path to adult.data")
    parser.add_argument("--test", type=Path, required=True, help="path to adult.test")
    parser.add_argument("--output", type=Path, default=Path("data/adult.csv"))
    args = parser.parse_args()

    df = build_dataset(args.train, args.test)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"{len(df):,} rows x {df.shape[1]} columns written to {args.output}")


if __name__ == "__main__":
    main()
