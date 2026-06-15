# Simulation engine

This document describes the simulation workflow used by CaptUReFraud.

---

## Prediction interface

The prediction interface is implemented in: `src/simulation/predictor.py`

It provides a reusable `FraudPredictor` class for loading a previously trained Spark MLlib `PipelineModel` and running predictions on processed transaction data.

The expected input data must contain a `features` column.

Main methods:

- `predict(transaction)` – predicts a single transaction
- `predict_batch(transactions)` – predicts multiple transactions
- `predict_dataframe(transactions_df)` – returns a Spark DataFrame with model output columns

The sample script is available in: `scripts/predict_sample.py`

Run it through Docker Compose from the project root:

```bash
docker compose exec app python3 scripts/predict_sample.py
```

## Decision logic

Decision logic is implemented in: `src/simulation/decision.py`

It converts model fraud probability into an operational transaction decision.

The default decision rule is:

`block` if fraud probability is greater than or equal to the configured threshold, otherwise `allow`.

Example:

```bash
docker compose exec app python3 scripts/decision_sample.py
```

The threshold can be adjusted without changing or retraining the model.

## Transaction simulation engine

The transaction simulation engine is implemented in: `src/simulation/engine.py`

It combines:

- model prediction,
- fraud probability extraction,
- threshold-based decision logic.

The default decision threshold is: `0.8`

The engine uses native Spark column operations and `vector_to_array` to extract fraud probability from the Spark ML probability vector, avoiding Python UDF serialization issues.

Run a sample batch simulation through Docker Compose:

```bash
docker compose exec app python3 scripts/simulate_batch.py
```

The simulation output contains:

- original processed transaction data,
- model prediction,
- fraud probability,
- decision: `allow` or `block`.

This module is reused by the backend API and frontend UI.

## Simulated incoming transaction batches

The backend uses the processed test split as the source of simulated incoming transactions.

The test split is not used for model training. It is reused after training to simulate transactions that the model has not seen during training.

The API endpoint:

```text
GET /simulation/batch
```

loads a random batch from `data/processed/test/`, applies the trained model, applies the selected threshold, and returns analyst-facing transaction records.

Each returned transaction includes a stable `transaction_id` generated from transaction fields. This makes it easier to refer to a transaction in the frontend review workflow.

The batch response also includes business fields preserved during preprocessing:

- `step`
- `type`
- `amount`
- `oldbalanceOrg`
- `newbalanceOrig`
- `oldbalanceDest`
- `newbalanceDest`

These fields are used by the frontend to display transaction details such as transaction type, amount, sender balance, and receiver balance.

## Feedback and outcome tracking

Feedback logic is implemented in: `src/simulation/feedback.py`

The simulation engine compares true labels with model predictions and analyst-facing decisions.

It tracks:

- prediction outcome: `TP`, `FP`, `TN`, `FN`
- whether fraud was correctly detected
- whether fraud was missed
- whether a legitimate transaction was correctly allowed
- whether a legitimate transaction was incorrectly blocked

Run a feedback sample through Docker Compose:

```bash
docker compose exec app python3 scripts/feedback_sample.py
```

Batch simulation also includes feedback columns:

```bash
docker compose exec app python3 scripts/simulate_batch.py
```

Aggregated results can be derived from simulation output and used to build confusion-matrix-like summaries.

## Business-level simulation metrics

Business metrics are implemented in: `src/simulation/metrics.py`

The metrics are calculated from simulation output, not directly from raw model output.

Tracked metrics include:

- fraud recall,
- detected frauds,
- missed frauds,
- blocked legitimate transactions,
- estimated fraud loss,
- estimated blocking cost,
- estimated total cost.

Run through Docker Compose:

```bash
docker compose exec app python3 scripts/evaluate_simulation.py
```

The estimated fraud loss is calculated from the transaction `amount` for missed fraud transactions.

The estimated blocking cost is intentionally simplified and uses a fixed cost for each legitimate transaction that is incorrectly blocked.

These metrics are used to show how model and decision thresholds can affect business outcomes, not only ML metrics.

## Frontend simulation workflow

The frontend uses the simulation API to provide an analyst-oriented workflow.

The user can:

- fetch a simulated incoming transaction batch,
- adjust the decision threshold,
- review fraud probability and system decision,
- filter transactions by type, risk level, amount, or probability,
- inspect alerts for suspicious or fraud-level transactions,
- make manual analyst decisions,
- reveal known labels after review,
- compare analyst decisions with system decisions.

Risk levels shown in the frontend are derived from fraud probability and threshold:

- `OK` – low fraud probability,
- `Suspicious` – medium fraud probability below the blocking threshold,
- `Fraud` – fraud probability greater than or equal to the selected threshold.

True labels are available in the dataset, but the frontend hides them until the user evaluates decisions.

## End-to-end batch simulation

The full batch simulation script is available in: `scripts/run_batch_simulation.py`

It runs the complete simulation pipeline on the processed test dataset:

- loads `data/processed/test/`,
- loads the trained model from `models/fraud_model/`,
- applies model prediction,
- calculates fraud probability,
- applies threshold-based decision logic,
- adds feedback and outcome tracking columns,
- calculates business-level metrics,
- saves final results to `data/processed/simulation_results/`.

Run through Docker Compose:

```bash
docker compose exec app python3 scripts/run_batch_simulation.py
```

The generated simulation output is stored as Parquet files and **is not** tracked by Git.

## Full raw-to-simulation workflow

From the project root, the complete local workflow is:

```bash
python scripts/download_data.py
docker compose up -d
docker compose exec app python3 scripts/prepare_data.py
docker compose exec app python3 scripts/train_model.py
docker compose exec app python3 scripts/run_batch_simulation.py
```

This workflow:

- downloads or verifies raw data,
- creates processed train/test datasets from raw data,
- trains and saves the model,
- runs full batch simulation on the processed test dataset.

The same setup can also be started with `start.bat` on Windows or `start.sh` on Linux/macOS.
