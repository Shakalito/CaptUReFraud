from pathlib import Path

from fastapi import APIRouter, Query

from src.api.config import (
    DEFAULT_DECISION_THRESHOLD,
    MAX_DECISION_THRESHOLD,
    MIN_DECISION_THRESHOLD,
)
from src.api.errors import ApiError
from src.api.schemas import EvaluationMetricsResponse
from src.common.spark import create_spark_session
from src.evaluation.model_metrics import calculate_model_performance_metrics
from src.simulation.engine import SimulationEngine
from src.simulation.predictor import FraudPredictor

router = APIRouter(prefix="/evaluation", tags=["evaluation"])

MODEL_PATH = Path("models/fraud_model")
TEST_DATA_PATH = Path("data/processed/test")


@router.get("/model", response_model=EvaluationMetricsResponse)
def get_model_evaluation(
    threshold: float = Query(
        DEFAULT_DECISION_THRESHOLD,
        ge=MIN_DECISION_THRESHOLD,
        le=MAX_DECISION_THRESHOLD,
    )
) -> EvaluationMetricsResponse:
    """Return evaluation metrics for threshold-based fraud decisions.

    The endpoint loads processed test data, uses the existing SimulationEngine
    to produce prediction records, applies the selected threshold to
    fraud_probability, and reuses src.evaluation.model_metrics to calculate
    confusion matrix and classification metrics.

    Mapping:
    - fraud_probability >= threshold -> 1
    - fraud_probability < threshold -> 0
    """
    return calculate_evaluation_response(threshold)


def calculate_evaluation_response(threshold: float) -> EvaluationMetricsResponse:
    """Calculate evaluation response for API output."""
    _validate_required_artifacts()

    spark = create_spark_session("CaptUReFraud API Evaluation")

    try:
        transactions_df = spark.read.parquet(str(TEST_DATA_PATH))

        predictor = FraudPredictor(spark, str(MODEL_PATH))
        engine = SimulationEngine(predictor=predictor)

        simulation_df = engine.simulate_batch(transactions_df)

        rows = simulation_df.select("label", "fraud_probability").collect()

        if not rows:
            raise ApiError(
                status_code=404,
                error="No transactions found",
                detail="No transactions found in processed test dataset.",
            )

        labels = [int(row["label"]) for row in rows]
        threshold_predictions = [
            _probability_to_binary_prediction(
                fraud_probability=float(row["fraud_probability"]),
                threshold=threshold,
            )
            for row in rows
        ]

        metrics = calculate_model_performance_metrics(
            labels=labels,
            predictions=threshold_predictions,
        )

        return EvaluationMetricsResponse(
            threshold=threshold,
            true_positives=metrics.true_positives,
            false_positives=metrics.false_positives,
            true_negatives=metrics.true_negatives,
            false_negatives=metrics.false_negatives,
            total=metrics.total,
            accuracy=metrics.accuracy,
            precision=metrics.precision,
            recall=metrics.recall,
            f1_score=metrics.f1_score,
            false_positive_rate=metrics.false_positive_rate,
            false_negative_rate=metrics.false_negative_rate,
        )
    finally:
        spark.stop()


def _probability_to_binary_prediction(
    fraud_probability: float,
    threshold: float,
) -> int:
    """Convert fraud probability into binary prediction using threshold."""
    return 1 if fraud_probability >= threshold else 0


def _validate_required_artifacts() -> None:
    """Validate local model and processed test data artifacts."""
    if not MODEL_PATH.exists():
        raise ApiError(
            status_code=404,
            error="Model not found",
            detail=(
                f"Model not found at /app/{MODEL_PATH}. "
                "Run scripts/train_model.py before using evaluation endpoints."
            ),
        )

    if not TEST_DATA_PATH.exists():
        raise ApiError(
            status_code=404,
            error="Test data not found",
            detail=(
                f"Test data not found at /app/{TEST_DATA_PATH}. "
                "Run scripts/prepare_data.py before using evaluation endpoints."
            ),
        )