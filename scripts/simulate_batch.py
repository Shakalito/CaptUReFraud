from pathlib import Path

from src.common.spark import create_spark_session
from src.simulation.engine import SimulationConfig, SimulationEngine
from src.simulation.predictor import FraudPredictor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "fraud_model"
TEST_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "test"


def main() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}. Run model training first."
        )

    if not TEST_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Test data not found: {TEST_DATA_PATH}. Run preprocessing first."
        )

    spark = create_spark_session("SimulateBatch")

    try:
        transactions_df = spark.read.parquet(str(TEST_DATA_PATH)).limit(10)

        predictor = FraudPredictor(
            spark=spark,
            model_path=MODEL_PATH,
        )

        engine = SimulationEngine(
            predictor=predictor,
            config=SimulationConfig(threshold=0.8),
        )

        result_df = engine.simulate_batch(transactions_df)

        result_df.select(
            "label",
            "prediction",
            "fraud_probability",
            "decision",
            "prediction_outcome",
            "fraud_correctly_detected",
            "fraud_missed",
            "legit_incorrectly_blocked",
        ).show(truncate=False)

        print("Aggregated simulation results:")
        engine.aggregate_results(result_df).show(truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
