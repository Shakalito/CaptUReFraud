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
        ).collect()

        return [
            {
                "features": row["features"],
                "label": int(row["label"]) if row["label"] is not None else None,
                "prediction": int(row["prediction"]),
                "fraud_probability": float(row["fraud_probability"]),
                "decision": row["decision"],
            }
            for row in rows
        ]

    def _validate_config(self) -> None:
        if not 0.0 <= self.config.threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0.")
