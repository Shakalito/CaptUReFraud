from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, Query

from src.api.schemas import PredictionResponse
from src.common.spark import create_spark_session
from src.simulation.predictor import FraudPredictor


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "models" / "fraud_model"
TEST_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "test"

router = APIRouter(
    prefix="/prediction",
    tags=["prediction"],
)


@router.get("/sample", response_model=PredictionResponse)
def predict_sample(
    threshold: float = Query(default=0.8, ge=0.0, le=1.0),
) -> PredictionResponse:
    if not MODEL_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                f"Model not found at {MODEL_PATH}. "
                "Run scripts/train_model.py before using prediction endpoints."
            ),
        )

    if not TEST_DATA_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                f"Test data not found at {TEST_DATA_PATH}. "
                "Run scripts/prepare_data.py before using prediction endpoints."
            ),
        )

    spark = create_spark_session("ApiPredictionSample")

    try:
        transactions_df = spark.read.parquet(str(TEST_DATA_PATH)).limit(1)

        if transactions_df.count() == 0:
            raise HTTPException(
                status_code=404,
                detail="No transactions found in processed test dataset.",
            )

        predictor = FraudPredictor(
            spark=spark,
            model_path=MODEL_PATH,
        )

        prediction_df = predictor.predict_dataframe(transactions_df)

        row = prediction_df.select(
            "prediction",
            "probability",
        ).collect()[0]

        probability_values: List[float] = [
            float(value) for value in row["probability"].toArray().tolist()
        ]

        fraud_probability = probability_values[1]

        return PredictionResponse(
            prediction=int(row["prediction"]),
            fraud_probability=fraud_probability,
            threshold=threshold,
            probability=probability_values,
        )

    finally:
        spark.stop()