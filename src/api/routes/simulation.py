from pathlib import Path
from typing import List

from fastapi import APIRouter, Query
from pyspark.sql.functions import col, concat, concat_ws, lit, rand, sha2, substring, upper

from src.api.config import (
    DEFAULT_DECISION_THRESHOLD,
    DEFAULT_SIMULATION_BATCH_LIMIT,
    MAX_DECISION_THRESHOLD,
    MAX_SIMULATION_BATCH_LIMIT,
    MIN_DECISION_THRESHOLD,
)
from src.api.errors import ApiError
from src.api.schemas import BatchSimulationResponse, BusinessMetricsResponse, SimulationRecordResponse
from src.common.spark import create_spark_session
from src.simulation.engine import SimulationConfig, SimulationEngine
from src.simulation.metrics import CostConfig, calculate_business_metrics
from src.simulation.predictor import FraudPredictor


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "models" / "fraud_model"
TEST_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "test"


router = APIRouter(
    prefix="/simulation",
    tags=["simulation"],
)


def validate_simulation_artifacts() -> None:
    if not MODEL_PATH.exists():
        raise ApiError(
            status_code=503,
            error="Model not found",
            detail=(
                f"Model not found at {MODEL_PATH}. "
                "Run scripts/train_model.py before using simulation endpoints."
            ),
        )

    if not TEST_DATA_PATH.exists():
        raise ApiError(
            status_code=503,
            error="Test data not found",
            detail=(
                f"Test data not found at {TEST_DATA_PATH}. "
                "Run scripts/prepare_data.py before using simulation endpoints."
            ),
        )


def add_transaction_id(transactions_df):
    transaction_fingerprint = concat_ws(
        "|",
        col("step").cast("string"),
        col("type").cast("string"),
        col("amount").cast("string"),
        col("oldbalanceOrg").cast("string"),
        col("newbalanceOrig").cast("string"),
        col("oldbalanceDest").cast("string"),
        col("newbalanceDest").cast("string"),
    )

    return transactions_df.withColumn(
        "transaction_id",
        concat(
            lit("TX-"),
            upper(substring(sha2(transaction_fingerprint, 256), 1, 12)),
        ),
    )


def create_simulation_engine(spark, threshold: float) -> SimulationEngine:
    predictor = FraudPredictor(
        spark=spark,
        model_path=MODEL_PATH,
    )

    return SimulationEngine(
        predictor=predictor,
        config=SimulationConfig(threshold=threshold),
    )


@router.get("/batch", response_model=BatchSimulationResponse)
def run_batch_simulation(
    limit: int = Query(default=DEFAULT_SIMULATION_BATCH_LIMIT, ge=1, le=MAX_SIMULATION_BATCH_LIMIT),
    threshold: float = Query(
        default=DEFAULT_DECISION_THRESHOLD,
        ge=MIN_DECISION_THRESHOLD,
        le=MAX_DECISION_THRESHOLD,
    ),
) -> BatchSimulationResponse:
    validate_simulation_artifacts()

    spark = create_spark_session("ApiBatchSimulation")

    try:
        transactions_df = (
            spark.read.parquet(str(TEST_DATA_PATH))
            .orderBy(rand())
            .limit(limit)
        )

        transactions_df = add_transaction_id(transactions_df)

        if transactions_df.count() == 0:
            raise ApiError(
                status_code=404,
                error="No transactions found",
                detail="No transactions found in processed test dataset.",
            )

        engine = create_simulation_engine(
            spark=spark,
            threshold=threshold,
        )

        simulation_df = engine.simulate_batch(transactions_df)

        rows = simulation_df.select(
            "transaction_id",
            "label",
            "prediction",
            "fraud_probability",
            "decision",
            "prediction_outcome",
            "fraud_correctly_detected",
            "fraud_missed",
            "legit_correctly_allowed",
            "legit_incorrectly_blocked",
            "step",
            "type",
            "amount",
            "oldbalanceOrg",
            "newbalanceOrig",
            "oldbalanceDest",
            "newbalanceDest",
        ).collect()

        records: List[SimulationRecordResponse] = [
            SimulationRecordResponse(
                transaction_id=str(row["transaction_id"]),
                label=int(row["label"]),
                prediction=int(row["prediction"]),
                fraud_probability=float(row["fraud_probability"]),
                decision=row["decision"],
                prediction_outcome=row["prediction_outcome"],
                fraud_correctly_detected=bool(row["fraud_correctly_detected"]),
                fraud_missed=bool(row["fraud_missed"]),
                legit_correctly_allowed=bool(row["legit_correctly_allowed"]),
                legit_incorrectly_blocked=bool(row["legit_incorrectly_blocked"]),
                step=int(row["step"]) if row["step"] is not None else None,
                type=row["type"],
                amount=float(row["amount"]) if row["amount"] is not None else None,
                oldbalanceOrg=float(row["oldbalanceOrg"])
                if row["oldbalanceOrg"] is not None
                else None,
                newbalanceOrig=float(row["newbalanceOrig"])
                if row["newbalanceOrig"] is not None
                else None,
                oldbalanceDest=float(row["oldbalanceDest"])
                if row["oldbalanceDest"] is not None
                else None,
                newbalanceDest=float(row["newbalanceDest"])
                if row["newbalanceDest"] is not None
                else None,
            )
            for row in rows
        ]

        return BatchSimulationResponse(
            threshold=threshold,
            count=len(records),
            records=records,
        )

    finally:
        spark.stop()


@router.get("/metrics", response_model=BusinessMetricsResponse)
def get_simulation_metrics(
    threshold: float = Query(
        default=DEFAULT_DECISION_THRESHOLD,
        ge=MIN_DECISION_THRESHOLD,
        le=MAX_DECISION_THRESHOLD,
    ),
) -> BusinessMetricsResponse:
    validate_simulation_artifacts()

    spark = create_spark_session("ApiSimulationMetrics")

    try:
        transactions_df = spark.read.parquet(str(TEST_DATA_PATH))

        if transactions_df.count() == 0:
            raise ApiError(
                status_code=404,
                error="No transactions found",
                detail="No transactions found in processed test dataset.",
            )

        engine = create_simulation_engine(
            spark=spark,
            threshold=threshold,
        )

        simulation_df = engine.simulate_batch(transactions_df)

        metrics = calculate_business_metrics(
            simulation_df=simulation_df,
            cost_config=CostConfig(
                missed_fraud_cost=1000.0,
                blocked_legit_cost=50.0,
            ),
        )

        return BusinessMetricsResponse(
            total_transactions=metrics.total_transactions,
            total_frauds=metrics.total_frauds,
            detected_frauds=metrics.detected_frauds,
            missed_frauds=metrics.missed_frauds,
            blocked_legit_transactions=metrics.blocked_legit_transactions,
            fraud_recall=metrics.fraud_recall,
            estimated_fraud_loss=metrics.estimated_fraud_loss,
            estimated_blocking_cost=metrics.estimated_blocking_cost,
            estimated_total_cost=metrics.estimated_total_cost,
        )

    finally:
        spark.stop()