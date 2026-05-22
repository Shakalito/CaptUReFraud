from __future__ import annotations

from pathlib import Path
from typing import Union

from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.classification import RandomForestClassifier
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit, when


DEFAULT_FEATURES_COL = "features"
DEFAULT_LABEL_COL = "label"
DEFAULT_WEIGHT_COL = "class_weight"


def load_training_data(spark: SparkSession, path: Union[str, Path]) -> DataFrame:
    return spark.read.parquet(str(path))


def add_class_weights(
    train_df: DataFrame,
    label_col: str = DEFAULT_LABEL_COL,
    weight_col: str = DEFAULT_WEIGHT_COL,
) -> DataFrame:
    class_counts = {
        row[label_col]: row["count"]
        for row in train_df.groupBy(label_col).count().collect()
    }

    if 0 not in class_counts or 1 not in class_counts:
        raise ValueError("Training data must contain both classes: 0 and 1.")

    majority_count = max(class_counts.values())

    legit_weight = majority_count / class_counts[0]
    fraud_weight = majority_count / class_counts[1]

    return train_df.withColumn(
        weight_col,
        when(col(label_col) == 1, lit(float(fraud_weight))).otherwise(lit(float(legit_weight))),
    )


def train_random_forest_pipeline(
    train_df: DataFrame,
    features_col: str = DEFAULT_FEATURES_COL,
    label_col: str = DEFAULT_LABEL_COL,
    weight_col: str = DEFAULT_WEIGHT_COL,
) -> PipelineModel:
    classifier = RandomForestClassifier(
        featuresCol=features_col,
        labelCol=label_col,
        weightCol=weight_col,
        predictionCol="prediction",
        probabilityCol="probability",
        rawPredictionCol="rawPrediction",
        numTrees=50,
        maxDepth=8,
        seed=42,
    )

    pipeline = Pipeline(stages=[classifier])

    return pipeline.fit(train_df)


def save_model(
    model: PipelineModel,
    output_path: Union[str, Path],
    overwrite: bool = True,
) -> None:
    writer = model.write()

    if overwrite:
        writer = writer.overwrite()

    writer.save(str(output_path))