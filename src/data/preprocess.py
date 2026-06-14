from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Tuple, Union

from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import abs as spark_abs
from pyspark.sql.functions import col, log1p, when


RAW_REQUIRED_COLUMNS = {
    "step",
    "type",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "isFraud",
}

FEATURE_COLUMNS = [
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

BUSINESS_COLUMNS = [
    "step",
    "type",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
]

def load_raw_dataset(spark: SparkSession, raw_data_path: Union[str, Path]) -> DataFrame:
    path = Path(raw_data_path)

    return (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(path / "*.csv"))
    )


def validate_raw_schema(
    df: DataFrame,
    required_columns: Iterable[str] = RAW_REQUIRED_COLUMNS,
) -> None:
    missing_columns = set(required_columns).difference(df.columns)

    if missing_columns:
        raise ValueError(
            f"Raw dataset is missing required columns: {sorted(missing_columns)}"
        )


def add_engineered_features(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("amount_log", log1p(col("amount")))
        .withColumn("deltaOrig", col("oldbalanceOrg") - col("newbalanceOrig"))
        .withColumn("deltaDest", col("newbalanceDest") - col("oldbalanceDest"))
        .withColumn(
            "isBalanceErrorOrig",
            when(
                spark_abs((col("oldbalanceOrg") - col("amount")) - col("newbalanceOrig")) > 0.01,
                1.0,
            ).otherwise(0.0),
        )
        .withColumn(
            "isBalanceErrorDest",
            when(
                spark_abs((col("oldbalanceDest") + col("amount")) - col("newbalanceDest")) > 0.01,
                1.0,
            ).otherwise(0.0),
        )
        .withColumn("label", col("isFraud").cast("int"))
    )


def add_type_index(df: DataFrame) -> DataFrame:
    indexer = StringIndexer(
        inputCol="type",
        outputCol="type_index",
        handleInvalid="keep",
    )

    indexer_model = indexer.fit(df)

    return indexer_model.transform(df)


def assemble_features(
    df: DataFrame,
    feature_columns: List[str] = FEATURE_COLUMNS,
) -> DataFrame:
    assembler = VectorAssembler(
        inputCols=feature_columns,
        outputCol="features",
        handleInvalid="keep",
    )

    output_columns = [
        "features",
        "label",
        *BUSINESS_COLUMNS,
    ]

    return assembler.transform(df).select(*output_columns)


def prepare_ml_dataset(raw_df: DataFrame) -> DataFrame:
    validate_raw_schema(raw_df)

    engineered_df = add_engineered_features(raw_df)
    indexed_df = add_type_index(engineered_df)

    return assemble_features(indexed_df)


def split_train_test(
    df: DataFrame,
    train_ratio: float = 0.8,
    seed: int = 42,
) -> Tuple[DataFrame, DataFrame]:
    if not 0.0 < train_ratio < 1.0:
        raise ValueError("train_ratio must be between 0.0 and 1.0.")

    test_ratio = 1.0 - train_ratio

    train_df, test_df = df.randomSplit([train_ratio, test_ratio], seed=seed)

    return train_df, test_df


def save_processed_datasets(
    train_df: DataFrame,
    test_df: DataFrame,
    train_output_path: Union[str, Path],
    test_output_path: Union[str, Path],
) -> None:
    train_df.coalesce(4).write.mode("overwrite").parquet(str(train_output_path))
    test_df.coalesce(2).write.mode("overwrite").parquet(str(test_output_path))