import os
import subprocess
import sys
import zipfile


# Where to save data and what to download from Kaggle
DATA_DIR = "../data/raw"
DATASET = "rupakroy/online-payments-fraud-detection-dataset"


def check_kaggle_auth():
    kaggle_path = os.path.expanduser("~/.kaggle/kaggle.json")
    if not os.path.exists(kaggle_path):
        print("Kaggle API key not found.")
        print("Please download it from https://www.kaggle.com/settings")
        sys.exit(1)

def dataset_exists():
    exists = any(fname.endswith(".csv") for fname in os.listdir(DATA_DIR))
    if exists:
        print("Dataset already exists. Skipping download.")
    return exists

def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    if dataset_exists():
        print("Dataset already exists. Skipping download.")
        return

    check_kaggle_auth()

    print("Downloading dataset...")
    subprocess.run([
        "kaggle", "datasets", "download",
        "-d", DATASET,
        "-p", DATA_DIR
    ], check=True)

    print("Unzipping...")
    for file in os.listdir(DATA_DIR):
        if file.endswith(".zip"):
            zip_path = os.path.join(DATA_DIR, file)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(DATA_DIR)

    print("Cleaning...")
    for file in os.listdir(DATA_DIR):
        if file.endswith(".zip"):
            os.remove(os.path.join(DATA_DIR, file))

    print("Done.")


if __name__ == "__main__":
    main()