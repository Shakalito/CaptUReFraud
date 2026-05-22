# Simulation engine

This document describes the simulation workflow _(implemented in EPIC #3.)_

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

Run it inside the Docker container:

```bash
python3 scripts/predict_sample.py
```

## Decision logic

Decision logic is implemented in: `src/simulation/decision.py`

It converts model fraud probability into an operational transaction decision.

The default decision rule is:

`block` if fraud probability is greater than or equal to the configured threshold, otherwise `allow`.

Example:

```bash
python3 scripts/decision_sample.py
```

The threshold can be adjusted without changing the model.


## Transaction simulation engine

The transaction simulation engine is implemented in: `src/simulation/engine.py`

It combines:

- model prediction,
- fraud probability extraction,
- threshold-based decision logic.

The default decision threshold is: `0.8`

The engine uses native Spark column operations and `vector_to_array` to extract fraud probability from the Spark ML probability vector, avoiding Python UDF serialization issues.

Run a sample batch simulation inside the Docker container:

```bash
python3 scripts/simulate_batch.py
```

The simulation output contains:

- original processed transaction data,
- model prediction,
- fraud probability,
- decision: allow or block.

This module is designed to be reused later by the backend API and frontend UI.

## Feedback and outcome tracking

Feedback logic is implemented in: `src/simulation/feedback.py`

The simulation engine compares true labels with model predictions and analyst-facing decisions.

It tracks:

- prediction outcome: `TP`, `FP`, `TN`, `FN`
- whether fraud was correctly detected
- whether fraud was missed
- whether a legitimate transaction was incorrectly blocked

Run a feedback sample inside the Docker container:

```bash
python3 scripts/feedback_sample.py
```

Batch simulation also includes feedback columns:
```bash
python3 scripts/simulate_batch.py
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

Run inside the Docker container:

```bash
python3 scripts/evaluate_simulation.py
```

The cost estimation is intentionally simplified. It is used to show how model and decision thresholds can affect business outcomes, not only ML metrics.


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

Run inside the Docker container:

```bash
python3 scripts/run_batch_simulation.py
```
The generated simulation output is stored as Parquet files and **is not** tracked by Git.

## Full raw-to-simulation workflow

Inside the Docker container, the complete local workflow is:

```bash
python3 scripts/prepare_data.py
python3 scripts/train_model.py
python3 scripts/run_batch_simulation.py
```

This workflow:

creates processed train/test datasets from raw data,
trains and saves the model,
runs full batch simulation on the processed test dataset.