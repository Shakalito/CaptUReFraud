from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, sum as spark_sum


@dataclass(frozen=True)
class BusinessMetrics:
    total_transactions: int
    total_frauds: int
    detected_frauds: int
    missed_frauds: int
    blocked_legit_transactions: int
    fraud_recall: float
    estimated_fraud_loss: float
    estimated_blocking_cost: float
    estimated_total_cost: float


@dataclass(frozen=True)
class CostConfig:
    missed_fraud_cost: float = 1000.0
    blocked_legit_cost: float = 50.0


def calculate_business_metrics(
    simulation_df: DataFrame,
    cost_config: CostConfig | None = None,
) -> BusinessMetrics:
    config = cost_config or CostConfig()

    required_columns = {
        "label",
        "fraud_correctly_detected",
        "fraud_missed",
        "legit_incorrectly_blocked",
    }

    missing_columns = required_columns.difference(simulation_df.columns)

    if missing_columns:
        raise ValueError(f"Simulation DataFrame is missing columns: {sorted(missing_columns)}")

    metrics_row = simulation_df.select(
        spark_sum(col("label")).alias("total_frauds"),
        spark_sum(col("fraud_correctly_detected").cast("int")).alias("detected_frauds"),
        spark_sum(col("fraud_missed").cast("int")).alias("missed_frauds"),
        spark_sum(col("legit_incorrectly_blocked").cast("int")).alias(
            "blocked_legit_transactions"
        ),
    ).collect()[0]

    total_transactions = simulation_df.count()
    total_frauds = int(metrics_row["total_frauds"] or 0)
    detected_frauds = int(metrics_row["detected_frauds"] or 0)
    missed_frauds = int(metrics_row["missed_frauds"] or 0)
    blocked_legit_transactions = int(metrics_row["blocked_legit_transactions"] or 0)

    fraud_recall = detected_frauds / total_frauds if total_frauds > 0 else 0.0

    estimated_fraud_loss = missed_frauds * config.missed_fraud_cost
    estimated_blocking_cost = blocked_legit_transactions * config.blocked_legit_cost
    estimated_total_cost = estimated_fraud_loss + estimated_blocking_cost

    return BusinessMetrics(
        total_transactions=total_transactions,
        total_frauds=total_frauds,
        detected_frauds=detected_frauds,
        missed_frauds=missed_frauds,
        blocked_legit_transactions=blocked_legit_transactions,
        fraud_recall=fraud_recall,
        estimated_fraud_loss=estimated_fraud_loss,
        estimated_blocking_cost=estimated_blocking_cost,
        estimated_total_cost=estimated_total_cost,
    )


def business_metrics_to_dict(metrics: BusinessMetrics) -> Dict[str, float | int]:
    return {
        "total_transactions": metrics.total_transactions,
        "total_frauds": metrics.total_frauds,
        "detected_frauds": metrics.detected_frauds,
        "missed_frauds": metrics.missed_frauds,
        "blocked_legit_transactions": metrics.blocked_legit_transactions,
        "fraud_recall": metrics.fraud_recall,
        "estimated_fraud_loss": metrics.estimated_fraud_loss,
        "estimated_blocking_cost": metrics.estimated_blocking_cost,
        "estimated_total_cost": metrics.estimated_total_cost,
    }
