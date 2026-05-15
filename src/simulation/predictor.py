from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, Union

from pyspark.ml import PipelineModel
from pyspark.ml.linalg import DenseVector, SparseVector, Vector, Vectors
from pyspark.sql import DataFrame, SparkSession


FeatureValue = Union[Vector, Sequence[float]]
TransactionInput = Mapping[str, Any]
BatchInput = Union[DataFrame, Iterable[TransactionInput]]


@dataclass(frozen=True)
class PredictionResult:
    prediction: int
    probability: float


class FraudPredictor:
    def __init__(
        self,
        spark: SparkSession,
        model_path: Union[str, Path],
        features_col: str = "features",
        prediction_col: str = "prediction",
        probability_col: str = "probability",
    ) -> None:
        self.spark = spark
        self.model_path = str(model_path)
        self.features_col = features_col
        self.prediction_col = prediction_col
        self.probability_col = probability_col
        self.model = PipelineModel.load(self.model_path)

    def predict(self, transaction: TransactionInput) -> PredictionResult:
        return self.predict_batch([transaction])[0]

    def predict_batch(self, transactions: BatchInput) -> list[PredictionResult]:
        input_df = self._to_dataframe(transactions)
        output_df = self.model.transform(input_df)

        rows = output_df.select(
            self.prediction_col,
            self.probability_col,
        ).collect()

        return [
            PredictionResult(
                prediction=int(row[self.prediction_col]),
                probability=self._get_fraud_probability(row[self.probability_col]),
            )
            for row in rows
        ]

    def predict_dataframe(self, transactions_df: DataFrame) -> DataFrame:
        self._validate_dataframe(transactions_df)
        return self.model.transform(transactions_df)

    def _to_dataframe(self, transactions: BatchInput) -> DataFrame:
        if isinstance(transactions, DataFrame):
            self._validate_dataframe(transactions)
            return transactions

        rows = []

        for transaction in transactions:
            if self.features_col not in transaction:
                raise ValueError(f"Missing required column: {self.features_col}")

            row = dict(transaction)
            row[self.features_col] = self._to_vector(row[self.features_col])
            rows.append(row)

        if not rows:
            raise ValueError("Prediction input cannot be empty.")

        return self.spark.createDataFrame(rows)

    def _validate_dataframe(self, transactions_df: DataFrame) -> None:
        if self.features_col not in transactions_df.columns:
            raise ValueError(f"Input DataFrame must contain column: {self.features_col}")

    @staticmethod
    def _to_vector(value: FeatureValue) -> Vector:
        if isinstance(value, (DenseVector, SparseVector)):
            return value

        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return Vectors.dense([float(item) for item in value])

        raise TypeError("Features must be a Spark vector or a numeric sequence.")

    @staticmethod
    def _get_fraud_probability(probability: Any) -> float:
        if probability is None:
            raise ValueError("Missing probability column in model output.")

        if len(probability) < 2:
            raise ValueError("Probability vector must contain two class probabilities.")

        return float(probability[1])