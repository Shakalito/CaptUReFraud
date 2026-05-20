from pathlib import Path

from src.common.spark import create_spark_session
from src.simulation.engine import SimulationConfig, SimulationEngine
from src.simulation.metrics import CostConfig, calculate_business_metrics
from src.simulation.predictor import FraudPredictor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "fraud_model"
TEST_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "test"


def print_business_metrics(metrics) -> None:
    print("Business-level simulation metrics")
    print("---------------------------------")
    print(f"Total transactions:              {metrics.total_transactions}")
    print(f"Total frauds:                    {metrics.total_frauds}")
    print(f"Detected frauds:                 {metrics.detected_frauds}")
    print(f"Missed frauds:                   {metrics.missed_frauds}")
    print(f"Blocked legit transactions:      {metrics.blocked_legit_transactions}")
    print(f"Fraud recall:                    {metrics.fraud_recall:.4f}")
    print(f"Estimated fraud loss:            {metrics.estimated_fraud_loss:.2f}")
    print(f"Estimated blocking cost:         {metrics.estimated_blocking_cost:.2f}")
    print(f"Estimated total cost:            {metrics.estimated_total_cost:.2f}")


def main() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}. Run model training first."
        )

    if not TEST_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Test data not found: {TEST_DATA_PATH}. Run preprocessing first."
        )

    spark = create_spark_session("EvaluateSimulation")

    try:
        transactions_df = spark.read.parquet(str(TEST_DATA_PATH))

        predictor = FraudPredictor(
            spark=spark,
            model_path=MODEL_PATH,
        )

        engine = SimulationEngine(
            predictor=predictor,
            config=SimulationConfig(threshold=0.8),
        )

        simulation_df = engine.simulate_batch(transactions_df)

        metrics = calculate_business_metrics(
            simulation_df=simulation_df,
            cost_config=CostConfig(
                missed_fraud_cost=1000.0,
                blocked_legit_cost=50.0,
            ),
        )

        print_business_metrics(metrics)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
