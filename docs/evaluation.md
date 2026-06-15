# Evaluation

CaptUReFraud includes an evaluation layer for measuring model performance, threshold-based decision quality, business impact, and analyst decision quality.

The goal of evaluation is to answer four separate questions:

1. How well does the fraud model separate fraud from legitimate transactions?
2. How does the selected decision threshold affect false positives and false negatives?
3. What is the business impact of missed frauds and blocked legitimate transactions?
4. Does the analyst improve or worsen the system decision during manual review?

Evaluation is based on the processed test dataset and the trained local model.

## Required local artifacts

Evaluation depends on the same local artifacts as prediction and simulation:

```text
data/processed/test/
models/fraud_model/
```

If these artifacts are missing, run from the project root after starting Docker Compose:

```bash
docker compose exec app python3 scripts/prepare_data.py
docker compose exec app python3 scripts/train_model.py
```

The evaluation endpoints and frontend evaluation dashboard do not train the model. They use the existing trained model and processed test data.

## Evaluation layers

CaptUReFraud uses several evaluation perspectives.

### 1. Model and system decision evaluation

Model/system evaluation compares known labels with threshold-based system decisions.

The model produces a fraud probability. The API then applies a decision threshold:

```text
fraud_probability >= threshold -> fraud / block
fraud_probability < threshold  -> legitimate / allow
```

The default threshold is:

```text
0.8
```

Changing the threshold changes system decisions without retraining the model.

Evaluation metrics are exposed through:

```text
GET /evaluation/model?threshold=0.8
```

Example response structure:

```json
{
  "threshold": 0.8,
  "true_positives": 1595,
  "false_positives": 6,
  "true_negatives": 1270013,
  "false_negatives": 14,
  "total": 1271628,
  "accuracy": 0.9999842721298996,
  "precision": 0.9962523422860712,
  "recall": 0.9912989434431324,
  "f1_score": 0.9937694704049844,
  "false_positive_rate": 0.000004724338769734941,
  "false_negative_rate": 0.00870105655686762
}
```

### 2. Business evaluation

Business evaluation focuses on operational cost rather than only model correctness.

It answers questions such as:

- how many frauds were missed
- how many legitimate transactions were blocked
- how much estimated fraud loss remains, calculated from the amounts of missed fraud transactions
- how much estimated blocking cost was introduced for legitimate transactions incorrectly blocked
- what the total estimated cost is

Business metrics are exposed through:

```text
GET /simulation/metrics?threshold=0.8
```

Business metrics and classification metrics are related, but they are not the same.

Classification metrics explain prediction quality.

Business metrics explain operational impact. In the current implementation, missed fraud loss is amount-based, while blocking cost is a simplified fixed operational cost per blocked legitimate transaction.

Example response structure:

```json
{
  "total_transactions": 1271628,
  "total_frauds": 1609,
  "detected_frauds": 1595,
  "missed_frauds": 14,
  "blocked_legit_transactions": 6,
  "fraud_recall": 0.9912989434431324,
  "estimated_fraud_loss": 6426570.9799999995,
  "estimated_blocking_cost": 300.0,
  "estimated_total_cost": 6426870.9799999995
}
```

### 3. Analyst decision evaluation

The frontend includes a simplified analyst review simulation.

The analyst can:

1. load a batch of simulated transactions
2. review model prediction, fraud probability, and system decision
3. make an analyst decision: allow or block
4. reveal known labels after review
5. evaluate analyst decision quality

Before evaluation, true labels and prediction outcomes are hidden.

After evaluation, the UI reveals:

- true label
- prediction outcome
- whether the analyst decision was correct
- analyst accuracy
- frauds missed by analyst
- legitimate transactions blocked by analyst

This is intentionally frontend-only at this stage. Analyst decisions are stored in browser state and are reset when a new batch is loaded.

### 4. Analyst vs system comparison

The frontend also compares analyst decisions with system decisions.

This answers whether the analyst agreed with or overrode the automated system.

Definitions:

```text
Agreement:
analyst decision equals system decision

Override:
analyst decision differs from system decision

Correct override:
system decision was wrong and analyst decision matches the known label

Incorrect override:
system decision was correct and analyst changed it incorrectly
```

The UI summarizes:

- reviewed transactions
- analyst/system agreements
- analyst/system overrides
- correct analyst overrides
- incorrect analyst overrides

This helps evaluate whether manual analyst intervention added value or reduced decision quality.

## Confusion matrix

The confusion matrix compares actual labels with predicted or threshold-based decisions.

In this project:

```text
label = 1 -> fraud transaction
label = 0 -> legitimate transaction
prediction = 1 -> predicted fraud / blocked
prediction = 0 -> predicted legitimate / allowed
```

### True Positive

A true positive means that the transaction was fraud and the system detected it as fraud.

```text
Actual: fraud
Predicted: fraud
Decision: block
```

Meaning:

```text
Fraud correctly detected.
```

### False Positive

A false positive means that the transaction was legitimate, but the system marked it as fraud.

```text
Actual: legitimate
Predicted: fraud
Decision: block
```

Meaning:

```text
Legitimate transaction incorrectly blocked or flagged.
```

Business interpretation:

```text
This can create customer friction and blocking cost.
```

### True Negative

A true negative means that the transaction was legitimate and the system correctly allowed it.

```text
Actual: legitimate
Predicted: legitimate
Decision: allow
```

Meaning:

```text
Legitimate transaction correctly allowed.
```

### False Negative

A false negative means that the transaction was fraud, but the system missed it.

```text
Actual: fraud
Predicted: legitimate
Decision: allow
```

Meaning:

```text
Fraud transaction missed by the system.
```

Business interpretation:

```text
This can create direct fraud loss.
```

## Classification metrics

Classification metrics are calculated from the confusion matrix.

Let:

```text
TP = true positives
FP = false positives
TN = true negatives
FN = false negatives
```

### Accuracy

Accuracy measures the share of all predictions that were correct.

```text
accuracy = (TP + TN) / (TP + FP + TN + FN)
```

High accuracy can be misleading in fraud detection because fraud datasets are usually highly imbalanced. If almost all transactions are legitimate, a model can have high accuracy while still missing fraud.

### Precision

Precision measures how many predicted fraud cases were actually fraud.

```text
precision = TP / (TP + FP)
```

High precision means that when the system blocks or flags a transaction, it is usually correct.

Low precision means the system creates many false positives.

Business interpretation:

```text
Precision is related to customer friction and unnecessary blocking.
```

### Recall

Recall measures how many actual fraud cases were detected.

```text
recall = TP / (TP + FN)
```

High recall means the system catches most frauds.

Low recall means the system misses many frauds.

Business interpretation:

```text
Recall is related to fraud loss prevention.
```

### F1 score

F1 score combines precision and recall into one metric.

```text
F1 = 2 * (precision * recall) / (precision + recall)
```

It is useful when both false positives and false negatives matter.

A high F1 score means the model balances precision and recall well.

### False positive rate

False positive rate measures how many legitimate transactions were incorrectly flagged as fraud.

```text
false_positive_rate = FP / (FP + TN)
```

Business interpretation:

```text
Higher false positive rate means more legitimate users may be blocked.
```

### False negative rate

False negative rate measures how many fraud transactions were missed.

```text
false_negative_rate = FN / (FN + TP)
```

Business interpretation:

```text
Higher false negative rate means more fraud is allowed through the system.
```

## Threshold trade-off

The decision threshold controls how strict the system is.

Lower threshold:

```text
fraud_probability >= lower threshold -> more transactions blocked
```

Usually causes:

- higher recall
- fewer missed frauds
- more false positives
- more blocked legitimate transactions
- potentially higher blocking cost

Higher threshold:

```text
fraud_probability must be higher before blocking
```

Usually causes:

- fewer false positives
- fewer blocked legitimate transactions
- more false negatives
- more missed frauds
- potentially higher fraud loss

Example from the current local model:

```text
threshold = 0.8
TP = 1595
FP = 6
FN = 14
precision ~= 99.63%
recall ~= 99.13%
```

```text
threshold = 0.5
TP = 1599
FP = 91
FN = 10
precision ~= 94.62%
recall ~= 99.38%
```

This shows the expected trade-off:

```text
Lower threshold catches more fraud but blocks more legitimate transactions.
```

## Business metrics vs evaluation metrics

CaptUReFraud separates classification metrics from business metrics.

### Evaluation metrics

Evaluation metrics answer:

```text
How accurate are the model/system decisions compared with known labels?
```

Examples:

- true positives
- false positives
- true negatives
- false negatives
- precision
- recall
- F1 score

### Business metrics

Business metrics answer:

```text
What is the estimated operational cost of those decisions?
```

Examples:

- missed frauds
- blocked legitimate transactions
- estimated fraud loss
- estimated blocking cost
- estimated total cost

Both perspectives are needed.

A model can have strong classification metrics but still produce an unfavorable business trade-off if the cost assumptions are different.

## Frontend evaluation dashboard

The frontend displays evaluation results in the fraud monitoring dashboard.

The evaluation section includes:

- precision
- recall
- F1 score
- false positive rate
- false negative rate
- confusion matrix
- false positive / false negative interpretation

The frontend also displays risk levels and suspicious/fraud alerts for the currently loaded transaction batch. These are UI-level indicators derived from fraud probability and the selected threshold.

When the user changes the threshold and applies it, the frontend refreshes:

- simulation batch
- business metrics
- evaluation metrics

The evaluation section is designed to support interpretation without replacing the main analyst workflow.

## Analyst workflow interpretation

The analyst workflow is a simulation.

The user does not see true labels before making decisions.

The user sees:

- model prediction
- fraud probability
- system decision

The user chooses:

```text
allow
block
```

After clicking evaluation, the UI reveals known labels and calculates analyst performance.

This better reflects a real review process where the final truth is usually not known at the moment of decision.

However, because this is a simulation dataset, known labels are available for evaluation after the review step.


