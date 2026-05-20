from pathlib import Path

from src.common.spark import create_spark_session
from src.model.train import (
    add_class_weights,
    load_training_data,
    save_model,
    train_random_forest_pipeline,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAIN_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "train"
MODEL_OUTPUT_PATH = PROJECT_ROOT / "models" / "fraud_model"


def main() -> None:
    if not TRAIN_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Training data not found: {TRAIN_DATA_PATH}. "
            "Run preprocessing before model training."
        )

    spark = create_spark_session("TrainFraudModel")

    try:
        train_df = load_training_data(spark, TRAIN_DATA_PATH)

        print("Training data schema:")
        train_df.printSchema()

        print("Class distribution:")
        train_df.groupBy("label").count().show()

        weighted_train_df = add_class_weights(train_df)

        print("Class weights preview:")
        weighted_train_df.select("label", "class_weight").distinct().show()

        model = train_random_forest_pipeline(weighted_train_df)

        save_model(
            model=model,
            output_path=MODEL_OUTPUT_PATH,
            overwrite=True,
        )

        print(f"Model saved to: {MODEL_OUTPUT_PATH}")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()