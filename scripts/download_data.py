from pathlib import Path
import shutil
import subprocess
import sys
import zipfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
DATASET = "rupakroy/online-payments-fraud-detection-dataset"


def check_kaggle_auth() -> None:
    kaggle_path = Path.home() / ".kaggle" / "kaggle.json"

    if not kaggle_path.exists():
        print("ERROR: Kaggle API key was not found.")
        print("Expected location:")
        print(f"  {kaggle_path}")
        print()
        print("Create a Kaggle API token from:")
        print("  https://www.kaggle.com/settings")
        print()
        print("Alternatively, download the dataset manually and place the CSV file in:")
        print(f"  {DATA_DIR}")
        sys.exit(1)


def check_kaggle_cli() -> None:
    if shutil.which("kaggle") is None:
        print("ERROR: Kaggle CLI was not found.")
        print("Install it with:")
        print("  pip install kaggle")
        print()
        print("Alternatively, download the dataset manually and place the CSV file in:")
        print(f"  {DATA_DIR}")
        sys.exit(1)


def dataset_exists() -> bool:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    csv_files = list(DATA_DIR.glob("*.csv"))

    if csv_files:
        print("Dataset already exists. Skipping download.")
        print(f"Found CSV file(s) in: {DATA_DIR}")
        return True

    return False


def download_dataset() -> None:
    print("Downloading dataset from Kaggle...")
    print(f"Target directory: {DATA_DIR}")

    try:
        subprocess.run(
            [
                "kaggle",
                "datasets",
                "download",
                "-d",
                DATASET,
                "-p",
                str(DATA_DIR),
            ],
            check=True,
        )
    except subprocess.CalledProcessError as error:
        print("ERROR: Kaggle dataset download failed.")
        print(f"Command exited with status: {error.returncode}")
        sys.exit(error.returncode)


def unzip_archives() -> None:
    zip_files = list(DATA_DIR.glob("*.zip"))

    if not zip_files:
        print("No zip archives found to extract.")
        return

    print("Extracting downloaded archive(s)...")

    for zip_path in zip_files:
        print(f"Extracting: {zip_path.name}")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(DATA_DIR)


def clean_archives() -> None:
    zip_files = list(DATA_DIR.glob("*.zip"))

    for zip_path in zip_files:
        zip_path.unlink()

    if zip_files:
        print("Removed downloaded zip archive(s).")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if dataset_exists():
        return

    check_kaggle_cli()
    check_kaggle_auth()

    download_dataset()
    unzip_archives()
    clean_archives()

    if not dataset_exists():
        print("ERROR: Download finished, but no CSV file was found.")
        print(f"Check the dataset directory: {DATA_DIR}")
        sys.exit(1)

    print("Dataset setup completed successfully.")


if __name__ == "__main__":
    main()