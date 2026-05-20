# Data pipeline

This document describes the data processing workflow used to prepare the fraud detection dataset for machine learning.

---

## Source dataset

The project uses the Kaggle Online Payments Fraud Detection Dataset.

Dataset setup instructions are available in: [`docs/data_setup.md`](data_setup.md)

Raw data is expected in: `data/raw/`

Raw data is **not** tracked by Git.

## Exploratory data analysis

Exploratory analysis was initially performed in: `notebooks/01_eda.ipynb`

The EDA stage focuses on:

- dataset schema inspection,
- row and column count,
- fraud vs legitimate transaction distribution,
- transaction type distribution,
- transaction amount patterns,
- initial observations about class imbalance.

Additional EDA notes are available in: [`docs/eda.md`](eda.md)

## Data preprocessing

Data preprocessing is implemented in PySpark and was initially developed in: `notebooks/02_preprocessing.ipynb`

The preprocessing pipeline includes:

- basic data validation,
- feature engineering,
- balance delta calculation,
- error flag creation,
- log transformation of transaction amount,
- categorical encoding,
- output export to `data/processed/`.

Processed data is not tracked by Git.

## Reproducible preprocessing script

The raw-to-processed data preparation can be run without notebooks using:

```bash
python3 scripts/prepare_data.py
```

The script:

- loads raw CSV files from data/raw/,
- validates the expected raw schema,
- applies feature engineering,
- creates amount_log,
- creates balance delta features,
- creates balance error flags,
- indexes transaction type into type_index,
- assembles the final features vector,
- creates the binary label column,
- splits the dataset into train and test sets,
- writes processed datasets to:
- data/processed/train/
- data/processed/test/

This script makes the project reproducible from the downloaded raw dataset to ML-ready Spark datasets.

## ML dataset preparation

Final ML-ready dataset preparation was initially developed in: `notebooks/03_dataset_preparation.ipynb`

The ML dataset contains:

- `features` column: Spark ML vector used by the model,
- `label` column: binary target variable.

Label meaning:

- `0` – legitimate transaction,
- `1` – fraud transaction.

The prepared dataset is split into:

- `data/processed/train/`
- `data/processed/test/`

The training dataset is used for model training.

The test dataset is used later as the source of simulated incoming transactions.

Additional ML dataset details are available in: [`docs/ml_dataset.md`](ml_dataset.md)

## Important notes

The dataset is highly imbalanced, with fraud transactions representing only a small percentage of all transactions.

This imbalance is handled later during model training by using class weights.

The test dataset must not be used for model training. In this project, it is reused as the source for transaction simulation after the model has already been trained.
