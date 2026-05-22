from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, Query

from src.api.schemas import BatchSimulationResponse, SimulationRecordResponse
from src.common.spark import create_spark_session
from src.simulation.engine import SimulationConfig, SimulationEngine
from src.simulation.predictor import FraudPredictor


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "models" / "fraud_model"
TEST_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "test"


router = APIRouter(
    prefix="/simulation",
    tags=["simulation"],
)


@router.get("/batch", response_model=BatchSimulationResponse)
def run_batch_simulation(
    limit: int = Query(default=10, ge=1, le=100),
    threshold: float = Query(default=0.8, ge=0.0, le=1.0),
) -> BatchSimulationResponse:
    if not MODEL_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                f"Model not found at {MODEL_PATH}. "
                "Run scripts/train_model.py before using simulation endpoints."
            ),
        )

    if not TEST_DATA_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                f"Test data not found at {TEST_DATA_PATH}. "
                "Run scripts/prepare_data.py before using simulation endpoints."
            ),
        )

    spark = create_spark_session("ApiBatchSimulation")

    try:
        transactions_df = spark.read.parquet(str(TEST_DATA_PATH)).limit(limit)

        if transactions_df.count() == 0:
            raise HTTPException(
                status_code=404,
                detail="No transactions found in processed test dataset.",
            )

        predictor = FraudPredictor(
            spark=spark,
            model_path=MODEL_PATH,
        )

        engine = SimulationEngine(
            predictor=predictor,
            config=SimulationConfig(threshold=threshold),
        )

        simulation_df = engine.simulate_batch(transactions_df)

        rows = simulation_df.select(
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

        records: List[SimulationRecordResponse] = [
            SimulationRecordResponse(
                label=int(row["label"]),
                prediction=int(row["prediction"]),
                fraud_probability=float(row["fraud_probability"]),
                decision=row["decision"],
                prediction_outcome=row["prediction_outcome"],
                fraud_correctly_detected=bool(row["fraud_correctly_detected"]),
                fraud_missed=bool(row["fraud_missed"]),
                legit_correctly_allowed=bool(row["legit_correctly_allowed"]),
                legit_incorrectly_blocked=bool(row["legit_incorrectly_blocked"]),
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