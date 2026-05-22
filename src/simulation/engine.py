from __future__ import annotations

from dataclasses import dataclass
from typing import List

from pyspark.ml.functions import vector_to_array
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when

from src.simulation.predictor import FraudPredictor


@dataclass(frozen=True)
class SimulationConfig:
    threshold: float = 0.8


class SimulationEngine:
    def __init__(
        self,
        predictor: FraudPredictor,
        config: SimulationConfig | None = None,
    ) -> None:
        self.predictor = predictor
        self.config = config or SimulationConfig()
        self._validate_config()

    def simulate_batch(self, transactions_df: DataFrame) -> DataFrame:
        predictions_df = self.predictor.predict_dataframe(transactions_df)

        result_df = predictions_df.withColumn(
            "probability_array",
            vector_to_array(col("probability")),
        ).withColumn(
            "fraud_probability",
            col("probability_array")[1],
        ).withColumn(
            "decision",
            when(col("fraud_probability") >= self.config.threshold, "block").otherwise("allow"),
        ).withColumn(
            "prediction_outcome",
            when((col("label") == 1) & (col("prediction") == 1), "TP")
            .when((col("label") == 0) & (col("prediction") == 1), "FP")
            .when((col("label") == 0) & (col("prediction") == 0), "TN")
            .otherwise("FN"),
        ).withColumn(
            "fraud_correctly_detected",
            (col("label") == 1) & (col("decision") == "block"),
        ).withColumn(
            "fraud_missed",
            (col("label") == 1) & (col("decision") == "allow"),
        ).withColumn(
            "legit_correctly_allowed",
            (col("label") == 0) & (col("decision") == "allow"),
        ).withColumn(
            "legit_incorrectly_blocked",
            (col("label") == 0) & (col("decision") == "block"),
        )

        return result_df.drop("probability_array")

    def simulate_batch_records(self, transactions_df: DataFrame) -> List[dict]:
        result_df = self.simulate_batch(transactions_df)

        rows = result_df.select(
            "features",
            "label",
            "prediction",
            "fraud_probability",
            "decision",
            "prediction_outcome",
            "fraud_correctly_detected",
            "fraud_missed",
            "legit_correctly_allowed",
            "legit_incorrectly_blocked",
        ).collect()

        return [
            {
                "features": row["features"],
                "label": int(row["label"]) if row["label"] is not None else None,
                "prediction": int(row["prediction"]),
                "fraud_probability": float(row["fraud_probability"]),
                "decision": row["decision"],
                "prediction_outcome": row["prediction_outcome"],
                "fraud_correctly_detected": bool(row["fraud_correctly_detected"]),
                "fraud_missed": bool(row["fraud_missed"]),
                "legit_correctly_allowed": bool(row["legit_correctly_allowed"]),
                "legit_incorrectly_blocked": bool(row["legit_incorrectly_blocked"]),
            }
            for row in rows
        ]

    def aggregate_results(self, simulation_df: DataFrame) -> DataFrame:
        return simulation_df.groupBy(
            "prediction_outcome",
            "decision",
        ).count()

    def _validate_config(self) -> None:
        if not 0.0 <= self.config.threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0.")