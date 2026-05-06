# ML Dataset Overview

## Dataset Location

- `/data/processed/train`
- `/data/processed/test`

---

## Structure

Each row contains:

- `features` → vector (assembled features)
- `label` → binary target (`isFraud`)

---

## Feature Pipeline

Data is derived from raw dataset via:

- removal of identifiers (`nameOrig`, `nameDest`)
- feature engineering:
  - `deltaOrig`
  - `deltaDest`
  - `isBalanceErrorOrig`
  - `isBalanceErrorDest`
- transformation:
  - `amount_log`
- encoding:
  - `type` → `type_index`

---

## Naming Convention

- `df` → full dataset
- `train_df` → training dataset
- `test_df` → test dataset

---

## ML Training Guidelines

### Data usage

- Always train on `/data/processed/train`
- Always evaluate on `/data/processed/test`
- Never mix splits (prevents data leakage)

---

### Target

- `label` = `isFraud`

---

### Evaluation (critical)

Avoid accuracy.

Use:
- Recall
- Precision
- F1-score
- PR-AUC

---

### Class imbalance

- Fraud ≈ 0.13%

---

### Reproducibility

Generated via:
- `02_preprocessing.ipynb`
- `03_dataset_preparation.ipynb`