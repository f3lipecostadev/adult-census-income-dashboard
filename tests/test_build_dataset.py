from scripts.build_dataset import COLUMNS, build_dataset

TRAIN = (
    "39, State-gov, 77516, Bachelors, 13, Never-married, Adm-clerical, Not-in-family, "
    "White, Male, 2174, 0, 40, United-States, <=50K\n"
    "50, ?, 83311, HS-grad, 9, Married-civ-spouse, ?, Husband, White, Male, 0, 0, 13, ?, >50K\n"
)
TEST = (
    "|1x3 Cross validator\n"
    "25, Private, 226802, 11th, 7, Never-married, Machine-op-inspct, Own-child, Black, Male, "
    "0, 0, 40, United-States, <=50K.\n"
)


def test_build_dataset_merges_splits_and_normalizes(tmp_path):
    train, test = tmp_path / "adult.data", tmp_path / "adult.test"
    train.write_text(TRAIN)
    test.write_text(TEST)

    df = build_dataset(train, test)

    assert list(df.columns) == COLUMNS
    assert len(df) == 3  # header line of adult.test skipped
    assert df["income"].tolist() == ["<=50K", ">50K", "<=50K"]  # trailing period removed
    assert df.loc[1, ["workclass", "occupation", "native-country"]].isna().all()  # "?" -> NaN
    assert df.loc[0, "workclass"] == "State-gov"  # leading spaces stripped
