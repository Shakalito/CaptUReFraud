from dataclasses import dataclass

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, coalesce, count, lit, sum as spark_sum, when


@dataclass(frozen=True)
class CostConfig:
    missed_fraud_cost: float = 1000.0
    blocked_legit_cost: float = 50.0


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


def calculate_business_metrics(
    simulation_df: DataFrame,
    cost_config: CostConfig,
) -> BusinessMetrics:
    total_frauds_expr = _total_frauds_expression(simulation_df)
    fraud_loss_expr = _estimated_fraud_loss_expression(
        simulation_df=simulation_df,
        cost_config=cost_config,
    )

    metrics_row = simulation_df.select(
        count(lit(1)).alias("total_transactions"),
        total_frauds_expr.alias("total_frauds"),
        _count_flag("fraud_correctly_detected").alias("detected_frauds"),
        _count_flag("fraud_missed").alias("missed_frauds"),
        _count_flag("legit_incorrectly_blocked").alias("blocked_legit_transactions"),
        fraud_loss_expr.alias("estimated_fraud_loss"),
        _estimated_blocking_cost_expression(cost_config).alias("estimated_blocking_cost"),
    ).collect()[0]

    total_transactions = _to_int(metrics_row["total_transactions"])
    total_frauds = _to_int(metrics_row["total_frauds"])
    detected_frauds = _to_int(metrics_row["detected_frauds"])
    missed_frauds = _to_int(metrics_row["missed_frauds"])
    blocked_legit_transactions = _to_int(metrics_row["blocked_legit_transactions"])
    estimated_fraud_loss = _to_float(metrics_row["estimated_fraud_loss"])
    estimated_blocking_cost = _to_float(metrics_row["estimated_blocking_cost"])

    fraud_recall = detected_frauds / total_frauds if total_frauds > 0 else 0.0
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


def _total_frauds_expression(simulation_df: DataFrame):
    if "label" in simulation_df.columns:
        return spark_sum(when(col("label") == 1, 1).otherwise(0))

    return _count_flag("fraud_correctly_detected") + _count_flag("fraud_missed")


def _estimated_fraud_loss_expression(
    simulation_df: DataFrame,
    cost_config: CostConfig,
):
    if "amount" in simulation_df.columns:
        missed_fraud_amount = coalesce(
            col("amount").cast("double"),
            lit(cost_config.missed_fraud_cost),
        )

        return spark_sum(
            when(col("fraud_missed") == True, missed_fraud_amount).otherwise(lit(0.0))
        )

    return spark_sum(
        when(col("fraud_missed") == True, lit(cost_config.missed_fraud_cost)).otherwise(lit(0.0))
    )


def _estimated_blocking_cost_expression(cost_config: CostConfig):
    return spark_sum(
        when(col("legit_incorrectly_blocked") == True, lit(cost_config.blocked_legit_cost))
        .otherwise(lit(0.0))
    )


def _count_flag(column_name: str):
    return spark_sum(when(col(column_name) == True, 1).otherwise(0))


def _to_int(value) -> int:
    return int(value or 0)


def _to_float(value) -> float:
    return float(value or 0.0)

def business_metrics_to_dict(metrics: BusinessMetrics) -> dict:
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