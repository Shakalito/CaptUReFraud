from pathlib import Path

from src.common.spark import create_spark_session
from src.data.preprocess import (
    load_raw_dataset,
    prepare_ml_dataset,
    save_processed_datasets,
    split_train_test,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"
TRAIN_OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "train"
TEST_OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "test"


def main() -> None:
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Raw data directory not found: {RAW_DATA_PATH}. "
            "Download the dataset before running preprocessing."
        )

    raw_files = list(RAW_DATA_PATH.glob("*.csv"))

    if not raw_files:
        raise FileNotFoundError(
            f"No CSV files found in: {RAW_DATA_PATH}. "
            "Download the Kaggle dataset before running preprocessing."
        )

    spark = create_spark_session("PrepareFraudDataset")

    try:
        print(f"Loading raw data from: {RAW_DATA_PATH}")
        raw_df = load_raw_dataset(spark, RAW_DATA_PATH)

        print("Raw data schema:")
        raw_df.printSchema()

        print("Preparing ML dataset...")
        ml_df = prepare_ml_dataset(raw_df)

        print("Prepared dataset schema:")
        ml_df.printSchema()

        print("Class distribution:")
        ml_df.groupBy("label").count().show()

        print("Splitting dataset into train and test...")
        train_df, test_df = split_train_test(
            df=ml_df,
            train_ratio=0.8,
            seed=42,
        )

        print(f"Saving training dataset to: {TRAIN_OUTPUT_PATH}")
        print(f"Saving test dataset to: {TEST_OUTPUT_PATH}")

        save_processed_datasets(
            train_df=train_df,
            test_df=test_df,
            train_output_path=TRAIN_OUTPUT_PATH,
            test_output_path=TEST_OUTPUT_PATH,
        )

        print("Processed datasets saved successfully.")

        print("Training dataset preview:")
        train_df.show(5, truncate=False)

        print("Test dataset preview:")
        test_df.show(5, truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()