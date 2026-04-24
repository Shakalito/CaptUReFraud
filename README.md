# CapUReFraud


- `data/raw/` – raw downloaded dataset (not tracked)
- `data/processed/` – cleaned datasets and intermediate artifacts
- `notebooks/` – exploratory analysis and experiments
- `src/` – source code (data processing, modeling)
- `scripts/` – utility scripts (e.g., dataset download)
- `models/` – trained models (not tracked)


## Dataset

This project uses a dataset from Kaggle.

To download the dataset automatically run
```bash
python scripts/download_data.py
```
or place it manually from [here](https://www.kaggle.com/datasets/rupakroy/online-payments-fraud-detection-dataset) and place it in `/data/raw`

For detailed setup instructions see [here](scripts/README.md).

