import pytest

from src.data.preprocess import FEATURE_COLUMNS, split_train_test, validate_raw_schema


def test_feature_columns_have_expected_order():
    assert FEATURE_COLUMNS == [
        "amount_log",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
        "deltaOrig",
        "deltaDest",
        "isBalanceErrorOrig",
        "isBalanceErrorDest",
        "type_index",
    ]


def test_validate_raw_schema_rejects_missing_columns(spark):
    df = spark.createDataFrame(
        [
            {
                "amount": 100.0,
                "isFraud": 0,
            }
        ]
    )

    with pytest.raises(ValueError):
        validate_raw_schema(df)


def test_split_train_test_rejects_invalid_train_ratio(spark):
    df = spark.createDataFrame(
        [
            {"label": 0},
            {"label": 1},
        ]
    )

    with pytest.raises(ValueError):
        split_train_test(df=df, train_ratio=1.5)