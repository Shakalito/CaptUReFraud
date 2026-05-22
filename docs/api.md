# Backend API

This document describes the FastAPI backend used by CaptUReFraud.

The API exposes endpoints for project health checks, runtime metadata, prediction, decision logic, batch simulation, and business-level simulation metrics.

## Runtime

The backend API is implemented with FastAPI and is intended to run inside the Docker container.

The API is served by Uvicorn.

## Start the API

From the project root directory, start the Docker app container:

```bash
docker compose up -d app
docker compose exec app bash
```

Inside the container, run:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:

```text
http://localhost:8000
```

## Interactive API documentation

FastAPI provides interactive OpenAPI documentation.

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

OpenAPI JSON:

```text
http://localhost:8000/openapi.json
```

## Required local artifacts

Some endpoints do not require data or model artifacts:

- `GET /`
- `GET /health`
- `GET /metadata`
- `POST /decision`

Model-dependent and simulation-dependent endpoints require local generated artifacts:

- `data/processed/test/`
- `models/fraud_model/`

These artifacts are not tracked by Git.

To generate them from raw data, run inside the Docker container:

```bash
python3 scripts/prepare_data.py
python3 scripts/train_model.py
```

## Endpoints

### Root endpoint

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

### Health check

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

### Runtime metadata

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

### Decision endpoint

```http
POST /decision
```

Converts fraud probability into an operational decision using threshold-based logic.

This endpoint does not load Spark, data, or model artifacts.

Default threshold:

```text
0.8
```

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

Request without threshold uses the default threshold:

```json
{
  "fraud_probability": 0.95
}
```

---

### Sample prediction endpoint

```http
GET /prediction/sample
```

Runs model prediction for one sample transaction from:

```text
data/processed/test/
```

Required local artifacts:

- `data/processed/test/`
- `models/fraud_model/`

Example response:

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
Invoke-RestMethod "http://localhost:8000/prediction/sample"
```

With custom threshold:

```powershell
Invoke-RestMethod "http://localhost:8000/prediction/sample?threshold=0.5"
```

---

### Batch simulation endpoint

```http
GET /simulation/batch
```

Runs batch simulation on processed test data.

Required local artifacts:

- `data/processed/test/`
- `models/fraud_model/`

Query parameters:

- `limit` – number of records to return, default `10`, maximum `100`
- `threshold` – fraud decision threshold, default `0.8`

Example request:

```text
GET /simulation/batch?limit=5&threshold=0.8
```

Example response:

```json
{
  "threshold": 0.8,
  "count": 5,
  "records": [
    {
      "label": 0,
      "prediction": 0,
      "fraud_probability": 0.0753546140819208,
      "decision": "allow",
      "prediction_outcome": "TN",
      "fraud_correctly_detected": false,
      "fraud_missed": false,
      "legit_correctly_allowed": true,
      "legit_incorrectly_blocked": false
    }
  ]
}
```

PowerShell example:

```powershell
Invoke-RestMethod "http://localhost:8000/simulation/batch?limit=5&threshold=0.8"
```

---

### Simulation metrics endpoint

```http
GET /simulation/metrics
```

Runs simulation on the processed test dataset and returns business-level metrics.

Required local artifacts:

- `data/processed/test/`
- `models/fraud_model/`

Query parameters:

- `threshold` – fraud decision threshold, default `0.8`

Example request:

```text
GET /simulation/metrics?threshold=0.8
```

Example response:

```json
{
  "total_transactions": 1271628,
  "total_frauds": 1609,
  "detected_frauds": 1595,
  "missed_frauds": 14,
  "blocked_legit_transactions": 6,
  "fraud_recall": 0.9912989434431324,
  "estimated_fraud_loss": 14000.0,
  "estimated_blocking_cost": 300.0,
  "estimated_total_cost": 14300.0
}
```

PowerShell example:

```powershell
Invoke-RestMethod "http://localhost:8000/simulation/metrics?threshold=0.8"
```

## Error responses

Expected application errors are returned as structured JSON.

Example missing model response:

```json
{
  "error": "Model not found",
  "detail": "Model not found at /app/models/fraud_model. Run scripts/train_model.py before using prediction endpoints."
}
```

Example missing processed test data response:

```json
{
  "error": "Test data not found",
  "detail": "Test data not found at /app/data/processed/test. Run scripts/prepare_data.py before using simulation endpoints."
}
```

Validation errors, such as invalid threshold values, are returned by FastAPI/Pydantic as HTTP `422`.

Example invalid threshold:

```text
GET /simulation/metrics?threshold=1.5
```

Example response:

```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["query", "threshold"],
      "msg": "Input should be less than or equal to 1",
      "input": "1.5"
    }
  ]
}
```

## Testing API endpoints

Lightweight API smoke tests can be run with:

```bash
python3 -m pytest tests/test_api_system.py tests/test_api_decision.py tests/test_api_errors.py
```

Full test suite:

```bash
python3 -m pytest tests
```

API smoke tests do not require Spark, processed data, or trained model artifacts.
