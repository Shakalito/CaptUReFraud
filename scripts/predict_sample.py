import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


from src.common.spark import create_spark_session
from src.simulation.predictor import FraudPredictor


MODEL_PATH = PROJECT_ROOT / "models" / "fraud_model"
TEST_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "test"


def main() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}. "
            "Run training before prediction."
        )

    if not TEST_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Test data not found: {TEST_DATA_PATH}. "
            "Run preprocessing before prediction."
        )

    spark = create_spark_session("PredictSample")

    try:
        test_df = spark.read.parquet(str(TEST_DATA_PATH)).limit(5)

        print("Input schema:")
        test_df.printSchema()

        predictor = FraudPredictor(
            spark=spark,
            model_path=MODEL_PATH,
        )

        predictions_df = predictor.predict_dataframe(test_df)

        predictions_df.select(
            "prediction",
            "probability",
        ).show(truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()