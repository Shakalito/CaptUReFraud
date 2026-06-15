# ML Dataset Overview

## Dataset Location

- `data/processed/train/`
- `data/processed/test/`

These directories are generated locally and are not tracked by Git.

---

## Structure

Each processed row contains the ML columns used by Spark MLlib:

- `features` → assembled Spark ML feature vector
- `label` → binary target (`isFraud`)

The processed dataset also keeps selected business transaction fields used by the backend API, simulation endpoints, and frontend analyst view:

- `step`
- `type`
- `amount`
- `oldbalanceOrg`
- `newbalanceOrig`
- `oldbalanceDest`
- `newbalanceDest`

These extra fields are not used as separate model input columns at prediction time. They are preserved so that simulated transactions can be displayed and evaluated in a business-readable way.

---

## Feature Pipeline

Data is derived from the raw dataset via:

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
- feature assembly:
  - engineered fields are assembled into the `features` vector

---

## Naming Convention

- `df` → full dataset
- `train_df` → training dataset
- `test_df` → test dataset

---

## ML Training Guidelines

### Data usage

- Always train on `data/processed/train/`
- Always evaluate on `data/processed/test/`
- Never mix splits during model training

The test split is also reused after training as the source of simulated incoming transaction batches in the API and frontend.

---

### Target

- `label` = `isFraud`

Label meaning:

- `0` → legitimate transaction
- `1` → fraud transaction

---

### Evaluation

Accuracy alone is not enough for this dataset because fraud is rare.

Use:

- Recall
- Precision
- F1-score
- False positives / false negatives
- Business metrics based on missed frauds and blocked legitimate transactions

---

### Class imbalance

- Fraud ≈ 0.13%

The model training pipeline handles this with class weighting.

---

### Reproducibility

Generated via:

```bash
python3 scripts/prepare_data.py
```

When running through Docker Compose from the project root:

```bash
docker compose exec app python3 scripts/prepare_data.py
```
