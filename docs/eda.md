# EDA notes – Fraud Detection Dataset

## Dataset

Synthetic financial transaction data from the PaySim simulation.

Expected raw file location:

```text
data/raw/PS_20174392719_1491204439457_log.csv
```

Raw data is not tracked by Git.

---

## Target variable

| Column  | Description                               |
| ------- | ----------------------------------------- |
| isFraud | Binary target (1 = fraud, 0 = legitimate) |

---

## Data size

- Rows: ~6.36 million
- Features: 10 raw columns excluding the target

---

## Class imbalance

- Fraud: ~0.13%
- Legitimate: ~99.87%

This is an extreme class imbalance problem.

### Implications

Accuracy alone is misleading for this dataset.

More useful metrics include:

- precision
- recall
- F1-score
- false positives / false negatives
- business-level fraud loss and blocking cost

In this project, imbalance is handled during model training with class weights.

---

## Feature groups

### 1. Transaction metadata

| Feature | Notes                                 |
| ------- | ------------------------------------- |
| type    | Transaction type, encoded for ML       |
| step    | Time step from the PaySim simulation   |

---

### 2. Monetary features

| Feature | Description       |
| ------- | ----------------- |
| amount  | Transaction value |

The amount distribution is strongly skewed, so the preprocessing pipeline creates a log-transformed amount feature.

---

### 3. Account balance features

| Feature        | Description                        |
| -------------- | ---------------------------------- |
| oldbalanceOrg  | Sender balance before transaction  |
| newbalanceOrig | Sender balance after transaction   |
| oldbalanceDest | Receiver balance before transaction |
| newbalanceDest | Receiver balance after transaction  |

These fields are used both for feature engineering and for analyst-facing transaction details in the frontend.

Some PaySim transaction types can have destination balances equal to zero, especially for merchant-like or cash-agent flows. The frontend displays these values as they appear in the dataset.

---

## Feature engineering used in the project

### Balance delta features

```text
deltaOrig = oldbalanceOrg - newbalanceOrig
deltaDest = newbalanceDest - oldbalanceDest
```

These features help detect balance changes around a transaction.

---

### Balance error flags

```text
isBalanceErrorOrig
isBalanceErrorDest
```

These binary flags capture inconsistencies between transaction amount and observed balance changes.

---

### Encoding

```text
type -> type_index
```

Transaction type is converted into a numeric feature for Spark MLlib.

---

### Transformation

```text
amount -> amount_log
```

The log-transformed amount reduces the impact of extreme transaction amounts.

---

## Key behavioral patterns

Fraud occurs mainly in:

- TRANSFER
- CASH_OUT

Common fraud signals include:

- specific transaction types
- high transaction amounts
- balance inconsistencies

---

## Data quality

- No missing values were observed in the dataset during exploration.
- No imputation step is required in the current pipeline.

---

## Modeling direction

The project uses a Spark MLlib Random Forest classifier.

Model evaluation focuses on:

- recall, because missed frauds are costly
- precision, because false positives create customer friction
- F1-score
- confusion matrix
- threshold-based business metrics

---

## Summary

The dataset is clean and well-structured, but highly imbalanced.

The strongest predictive signals are:

- transaction type
- transaction amount
- sender and receiver balance behavior
- balance consistency features

The processed dataset is later used for model training, test evaluation, and simulated incoming transaction batches.
