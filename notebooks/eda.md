# Dataset Overview – Fraud Detection (ML-Oriented)

## Dataset

Synthetic financial transaction data (PaySim simulation)

File:
`data/raw/PS_20174392719_1491204439457_log.csv`

---

## Target Variable

| Column  | Description                               |
| ------- | ----------------------------------------- |
| isFraud | Binary target (1 = fraud, 0 = legitimate) |

---

## Data Size

* Rows: ~6.36 million
* Features: 10 (excluding target)

---

## Class Imbalance

* Fraud: ~0.13%
* Legitimate: ~99.87%

→ Extreme imbalance problem

### Implications:

* Accuracy is misleading
* Use:

  * Precision / Recall
  * F1-score
  * ROC-AUC / PR-AUC
* Consider:

  * class weighting
  * undersampling / oversampling
  * anomaly detection methods

---

## Feature Groups

### 1. Transaction Metadata

| Feature | Notes                                 |
| ------- | ------------------------------------- |
| type    | Categorical (important)               |
| step    | Time index (can derive time features) |

---

### 2. Monetary Features

| Feature | Description       |
| ------- | ----------------- |
| amount  | Transaction value |

Characteristics:

* Strong right skew
* Contains outliers

→ Apply:

* log transformation (`log1p`)
* scaling (optional)

---

### 3. Account Balance Features

| Feature        |
| -------------- |
| oldbalanceOrg  |
| newbalanceOrig |
| oldbalanceDest |
| newbalanceDest |

High predictive potential.

---

## Recommended Feature Engineering

### ✔ Balance Consistency Features

```text
deltaOrig = oldbalanceOrg - newbalanceOrig
deltaDest = newbalanceDest - oldbalanceDest
```

→ Detect inconsistencies (common in fraud)

---

### ✔ Transaction Validity Checks

```text
expected_newbalanceOrig = oldbalanceOrg - amount
```

→ Compare with actual value

---

### ✔ Binary Flags

```text
isBalanceErrorOrig
isBalanceErrorDest
```

---

### ✔ Encoding

* `type` → One-hot encoding

---

### ✔ Transformations

* `amount` → `log1p(amount)`

---

## Key Behavioral Patterns

### Fraud occurs mainly in:

* TRANSFER
* CASH_OUT

→ Strong signal

---

### Fraud characteristics:

* Often high-value transactions
* Balance inconsistencies
* Specific transaction types

---

## Data Quality

* No missing values
* No imputation required

---

## Modeling Considerations

### Algorithms (recommended)

* Logistic Regression (baseline)
* Random Forest
* Gradient Boosting (XGBoost / LightGBM)
* Isolation Forest (optional)

---

### Evaluation Strategy

Use:

* Stratified split
* Cross-validation

Metrics:

* Recall (fraud detection priority)
* Precision
* F1-score
* PR-AUC (preferred over ROC)

---

## Risks

* Severe class imbalance
* Potential data leakage (balance features must be handled carefully)
* Overfitting to majority class

---

## Summary

Dataset is well-structured and clean, but highly imbalanced.

Strong predictive signals:

* transaction type
* balance inconsistencies
* transaction amount (after transformation)

Requires careful handling of imbalance and feature engineering.
