# Backend API

This document describes the FastAPI backend used by CaptUReFraud.

The backend exposes REST endpoints for health checks, runtime metadata, threshold-based decision logic, model prediction, simulated incoming transaction batches, business metrics, and model evaluation.

The current frontend analyst workflow mainly uses:

```text
GET /health
GET /metadata
GET /simulation/batch
GET /simulation/metrics
GET /evaluation/model
```

---

## Runtime

The backend API is implemented with:

- Python
- FastAPI
- Uvicorn
- Apache Spark / PySpark
- Spark MLlib RandomForest model

The API is intended to run through Docker Compose together with the React/Vite frontend.

Default backend URL:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

---

## Starting the API

### Recommended full-stack startup

From the project root:

```bash
docker compose up -d
```

This starts the default application stack:

- FastAPI backend on `http://localhost:8000`
- React/Vite frontend on `http://localhost:5173`

Swagger UI is available at:

```text
http://localhost:8000/docs
```

### Automated startup scripts

The project also provides startup helper scripts:

```text
start.bat
start.sh
```

These scripts are intended to:

- check Docker availability,
- download/setup raw data if missing,
- build Docker images,
- start services,
- prepare processed data,
- train the model,
- run a sample prediction,
- open the frontend.

Stop scripts:

```text
stop.bat
stop.sh
```

They stop the Compose stack with:

```bash
docker compose down
```

### Manual backend-only startup

If only the backend container is needed:

```bash
docker compose up -d app
```

Then test the API:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

## Required local artifacts

Some endpoints are lightweight and do not require model or data artifacts:

```text
GET /
GET /health
GET /metadata
POST /decision
```

Model-dependent and simulation-dependent endpoints require local generated artifacts:

```text
data/processed/test/
models/fraud_model/
```

These artifacts are not tracked by Git.

To generate them manually, run from the project root:

```bash
python scripts/download_data.py
docker compose up -d app
docker compose exec app python3 scripts/prepare_data.py
docker compose exec app python3 scripts/train_model.py
```

On Linux/macOS, local Python may be called as `python3` instead of `python`.

The dataset download script saves raw CSV files to:
`data/raw/`


The data preparation script creates:

```text
data/processed/train/
data/processed/test/
```

The training script creates:

```text
models/fraud_model/
```

---

## CORS

The frontend runs on:

```text
http://localhost:5173
```

The backend runs on:

```text
http://localhost:8000
```

Because these are different browser origins, the backend must allow requests from the frontend origin.

The backend uses CORS middleware so the React frontend can call the FastAPI API during local development.

If a browser shows an error similar to:

```text
Access to fetch at 'http://localhost:8000/...' from origin 'http://localhost:5173'
has been blocked by CORS policy
```

then ensure the backend is running from the current project version and restart the Compose stack:

```bash
docker compose down
docker compose up -d --build
```

---

## Endpoints

## Root endpoint

```http
GET /
```

Returns basic API status.

Example response:

```json
{
  "name": "CaptUReFraud API",
  "status": "running"
}
```

PowerShell example:

```powershell
Invoke-RestMethod "http://localhost:8000/"
```

---

## Health check

```http
GET /health
```

Returns lightweight API health status.

This endpoint does not load Spark, data, or model artifacts.

Example response:

```json
{
  "status": "ok"
}
```

PowerShell example:

```powershell
Invoke-RestMethod "http://localhost:8000/health"
```

---

## Runtime metadata

```http
GET /metadata
```

Returns basic project and runtime information.

This endpoint does not load Spark, data, or model artifacts.

Example response:

```json
{
  "project": "CaptUReFraud",
  "api_version": "0.1.0",
  "model_type": "Spark MLlib Random Forest",
  "runtime": "Docker",
  "requires_model": false
}
```

PowerShell example:

```powershell
Invoke-RestMethod "http://localhost:8000/metadata"
```

---

## Decision endpoint

```http
POST /decision
```

Converts a fraud probability into an operational decision using threshold-based logic.

Default threshold:

```text
0.8
```

Decision rule:

```text
fraud_probability >= threshold -> block
fraud_probability < threshold  -> allow
```

This endpoint does not load Spark, data, or model artifacts.

Example request:

```json
{
  "fraud_probability": 0.82,
  "threshold": 0.8
}
```

Example response:

```json
{
  "fraud_probability": 0.82,
  "threshold": 0.8,
  "decision": "block"
}
```

PowerShell example:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/decision" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"fraud_probability": 0.82, "threshold": 0.8}'
```

---

## Sample prediction endpoint

```http
GET /prediction/sample
```

Runs model prediction for one sample transaction from:

```text
data/processed/test/
```

Required artifacts:

```text
data/processed/test/
models/fraud_model/
```

Query parameters:

| Parameter | Type  | Default | Description |
| --------- | ----- | ------- | ----------- |
| threshold | float | `0.8`   | Decision threshold used to convert probability into allow/block decision |

Example request:

```text
GET /prediction/sample?threshold=0.8
```

Example response shape:

```json
{
  "prediction": 0,
  "fraud_probability": 0.0753546140819208,
  "threshold": 0.8,
  "probability": [
    0.9246453859180792,
    0.0753546140819208
  ]
}
```

PowerShell example:

```powershell
Invoke-RestMethod "http://localhost:8000/prediction/sample?threshold=0.8"
```

This endpoint is mainly a smoke test that verifies that:

- processed test data exists,
- the trained Spark model can be loaded,
- prediction output can be produced.

The final analyst UI primarily uses `/simulation/batch` instead.

---

## Batch simulation endpoint

```http
GET /simulation/batch
```

Runs batch simulation on processed test data.

Required artifacts:

```text
data/processed/test/
models/fraud_model/
```

The processed test dataset acts as the source of simulated incoming transactions. Each request samples a random batch from held-out test data. The model was trained on the training split, so these transactions simulate new transactions not seen during model training.

Query parameters:

| Parameter | Type  | Default | Limit | Description |
| --------- | ----- | ------- | ----- | ----------- |
| limit     | int   | `10`    | `1-100` | Number of transactions returned in the batch |
| threshold | float | `0.8`   | `0-1` | Decision threshold for allow/block decision |

Example request:

```text
GET /simulation/batch?limit=5&threshold=0.8
```

PowerShell example:

```powershell
Invoke-RestMethod "http://localhost:8000/simulation/batch?limit=5&threshold=0.8"
```

Example response shape:

```json
{
  "threshold": 0.8,
  "count": 5,
  "records": [
    {
      "transaction_id": "TX-76656F5251CC",
      "label": 0,
      "prediction": 0,
      "fraud_probability": 0.0033444088338499874,
      "decision": "allow",
      "prediction_outcome": "TN",
      "fraud_correctly_detected": false,
      "fraud_missed": false,
      "legit_correctly_allowed": true,
      "legit_incorrectly_blocked": false,
      "step": 139,
      "type": "CASH_OUT",
      "amount": 41904.79,
      "oldbalanceOrg": 0.0,
      "newbalanceOrig": 0.0,
      "oldbalanceDest": 4602413.67,
      "newbalanceDest": 4912923.4
    }
  ]
}
```

### Response fields

| Field | Description |
| ----- | ----------- |
| `transaction_id` | Stable generated transaction identifier used in the analyst UI |
| `label` | Known label from the test dataset (`0 = legit`, `1 = fraud`) |
| `prediction` | Model prediction (`0 = legit`, `1 = fraud`) |
| `fraud_probability` | Probability score for class `1` |
| `decision` | Threshold-based system decision: `allow` or `block` |
| `prediction_outcome` | Confusion-matrix outcome: `TP`, `FP`, `TN`, or `FN` |
| `fraud_correctly_detected` | Whether a fraud transaction was correctly blocked |
| `fraud_missed` | Whether a fraud transaction was incorrectly allowed |
| `legit_correctly_allowed` | Whether a legitimate transaction was correctly allowed |
| `legit_incorrectly_blocked` | Whether a legitimate transaction was incorrectly blocked |
| `step` | Time step from the PaySim simulation |
| `type` | Transaction type from the source dataset |
| `amount` | Transaction amount |
| `oldbalanceOrg` | Sender/origin balance before transaction |
| `newbalanceOrig` | Sender/origin balance after transaction |
| `oldbalanceDest` | Receiver/destination balance before transaction |
| `newbalanceDest` | Receiver/destination balance after transaction |

### Notes about labels

The backend response includes `label` and `prediction_outcome` because the project is a local simulation with known test labels.

The frontend hides the true label and prediction outcome until the analyst clicks evaluation. This simulates delayed fraud confirmation while keeping the evaluation workflow simple and reproducible.

A production version could split this into separate endpoints, for example:

```text
GET /simulation/batch
POST /simulation/reveal
```

---

## Simulation metrics endpoint

```http
GET /simulation/metrics
```

Runs simulation on the processed test dataset and returns business-level metrics.

Required artifacts:

```text
data/processed/test/
models/fraud_model/
```

Query parameters:

| Parameter | Type  | Default | Limit | Description |
| --------- | ----- | ------- | ----- | ----------- |
| threshold | float | `0.8`   | `0-1` | Decision threshold used for system decisions |

Example request:

```text
GET /simulation/metrics?threshold=0.8
```

PowerShell example:

```powershell
Invoke-RestMethod "http://localhost:8000/simulation/metrics?threshold=0.8"
```

Example response from the current local model:

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

### Business cost logic

Business metrics are calculated from simulation output.

Current assumptions:

```text
estimated_fraud_loss = sum(amount for missed fraud transactions)
estimated_blocking_cost = blocked_legit_transactions * fixed_blocking_cost
estimated_total_cost = estimated_fraud_loss + estimated_blocking_cost
```

This means that missing a high-value fraudulent transaction has a larger business impact than missing a small fraudulent transaction.

The blocking cost is kept as a fixed operational/customer-friction cost for each incorrectly blocked legitimate transaction.

---

## Model evaluation endpoint

```http
GET /evaluation/model
```

Returns threshold-dependent model/system evaluation metrics on the processed test dataset.

Required artifacts:

```text
data/processed/test/
models/fraud_model/
```

Query parameters:

| Parameter | Type  | Default | Limit | Description |
| --------- | ----- | ------- | ----- | ----------- |
| threshold | float | `0.8`   | `0-1` | Decision threshold used for evaluation |

Example request:

```text
GET /evaluation/model?threshold=0.8
```

PowerShell example:

```powershell
Invoke-RestMethod "http://localhost:8000/evaluation/model?threshold=0.8"
```

Example response from the current local model:

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

This endpoint supports the frontend model quality section:

- precision,
- recall,
- F1 score,
- false positive rate,
- false negative rate,
- confusion matrix.

---

## Error responses

Expected application errors are returned as structured JSON.

### Missing model

```json
{
  "error": "Model not found",
  "detail": "Model not found at /app/models/fraud_model. Run scripts/train_model.py before using simulation endpoints."
}
```

### Missing processed test data

```json
{
  "error": "Test data not found",
  "detail": "Test data not found at /app/data/processed/test. Run scripts/prepare_data.py before using simulation endpoints."
}
```

### Invalid query parameters

FastAPI/Pydantic validation errors return HTTP `422`.

Example invalid threshold:

```text
GET /simulation/metrics?threshold=1.5
```

Example response shape:

```json
{
  "detail": [
    {
      "loc": ["query", "threshold"],
      "msg": "Input should be less than or equal to 1",
      "input": "1.5"
    }
  ]
}
```

---

## Testing API endpoints

Run the full backend test suite inside the Docker app container:

```bash
docker compose exec app python3 -m pytest tests
```

Run only lightweight API smoke tests:

```bash
docker compose exec app python3 -m pytest tests/test_api_system.py tests/test_api_decision.py tests/test_api_errors.py
```

Current expected full test result:

```text
42 passed
```

The lightweight smoke tests do not require Spark, processed data, or trained model artifacts.

Simulation and evaluation endpoints require generated artifacts.