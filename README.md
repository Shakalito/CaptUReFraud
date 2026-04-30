# CaptUReFraud


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

## Running the project
In the root directory: 
```bash
docker compose up --build
```
Then open: http://localhost:8888
(Token: _fraud123_)

## Data Preprocessing

Data preprocessing is implemented in PySpark and available in:
`notebooks/02_preprocessing.ipynb`

The pipeline includes:
- feature engineering (balance deltas, error flags)
- log transformation of transaction amount
- categorical encoding
- cleaned dataset export to `/data/processed/`

## Data Pipeline

- `notebooks/01_eda.ipynb` – exploratory data analysis
- `notebooks/02_preprocessing.ipynb` – data cleaning and feature engineering
- `notebooks/03_dataset_preparation.ipynb` – final dataset preparation for ML

Additional details about dataset and ML setup are available in:
- `docs/eda.md`
- `docs/ml_dataset.md`