# Frontend UI

CaptUReFraud includes a React + Vite frontend for interacting with the FastAPI backend.

The frontend provides a fraud monitoring interface where a user can load simulated transaction batches, adjust the fraud decision threshold, review model recommendations, make analyst decisions, and evaluate those decisions after revealing known labels.

## Purpose

The frontend is designed as an analyst-oriented simulation interface.

It allows the user to:

- load simulated transaction records from the backend API
- review fraud probabilities and system recommendations
- adjust the decision threshold
- observe business-level metrics
- make allow/block analyst decisions
- reveal known labels after review
- evaluate analyst decision quality

The UI does not run machine learning logic directly. Prediction, simulation, and metrics are handled by the backend API.

## Technology

The frontend is built with:

- React
- Vite
- JavaScript
- CSS

TypeScript is not used in this project stage to keep the frontend simpler and easier to maintain.

## Location

Frontend source code is located in:

```text
frontend/
```

Main frontend files:

```text
frontend/src/App.jsx
frontend/src/App.css
frontend/src/api/client.js
frontend/.env.example
frontend/package.json
```

## Backend dependency

The frontend depends on the FastAPI backend.

Default backend URL:

```text
http://localhost:8000
```

Default frontend URL:

```text
http://localhost:5173
```

The frontend calls the backend through API functions defined in:

```text
frontend/src/api/client.js
```

The backend API base URL is configured through:

```env
VITE_API_BASE_URL=http://localhost:8000
```

An example environment file is provided in:

```text
frontend/.env.example
```

If no custom value is provided, the frontend uses:

```text
http://localhost:8000
```

## Required backend artifacts

Some frontend features depend on model and processed data artifacts.

Before using model-dependent frontend functionality, the backend should have:

```text
data/processed/test/
models/fraud_model/
```

These are created by running the data preparation and model training workflow:

```bash
python3 scripts/prepare_data.py
python3 scripts/train_model.py
```

The frontend itself does not create or load these artifacts directly.

## Starting the backend

From the project root, start the Docker app container:

```bash
docker compose up -d app
docker compose exec app bash
```

Inside the container, start the FastAPI backend:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend should be available at:

```text
http://localhost:8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## Starting the frontend

From the project root:

```bash
cd frontend
npm install
npm run dev
```

The frontend should be available at:

```text
http://localhost:5173
```

## Production build check

To verify that the frontend can be built:

```bash
cd frontend
npm run build
```

The build output is created in:

```text
frontend/dist/
```

The `dist/` directory is generated and should not be committed.

## Lint check

To check frontend code quality:

```bash
cd frontend
npm run lint
```

This runs ESLint and checks for basic JavaScript/React issues such as unused variables, invalid imports, or common code-quality problems.

## Main UI workflow

The frontend is organized around a simple analyst simulation workflow.

### 1. Load transactions

The user selects a batch size and clicks:

```text
Load / refresh batch
```

This fetches a simulated transaction batch from the backend.

The frontend calls:

```text
GET /simulation/batch
GET /simulation/metrics
```

The backend handles Spark/model logic and returns structured API responses.

### 2. Review decisions

After loading transactions, the user can select rows in the transaction table.

For each selected transaction, the analyst review panel shows:

- model prediction
- fraud probability
- system decision
- hidden true label before evaluation
- hidden prediction outcome before evaluation

The user can choose:

```text
Mark allow
Mark block
```

Analyst decisions are stored only in frontend state.

No backend persistence is used at this stage.

### 3. Evaluate results

After reviewing one or more transactions, the user can click:

```text
Evaluate decisions
```

Only then does the UI reveal:

- true label
- prediction outcome
- whether the analyst decision was correct or incorrect

This better simulates a real analyst workflow, where the final truth is usually not known at the moment of making a decision.

## Threshold interaction

The frontend includes a decision threshold control.

Default threshold:

```text
0.8
```

The user can adjust the threshold with the slider and apply it with:

```text
Apply threshold
```

Changing the threshold refreshes:

- simulation batch
- business metrics

The threshold affects operational decisions without retraining the model.

Lower threshold generally means:

- more frauds detected
- fewer missed frauds
- more legitimate transactions may be blocked

Higher threshold generally means:

- fewer legitimate transactions blocked
- more frauds may be missed

The frontend displays this trade-off through business metrics and simple visual indicators.

## Business metrics shown

The dashboard displays backend-calculated business metrics:

- fraud recall
- missed frauds
- blocked legitimate transactions
- estimated fraud loss
- estimated blocking cost
- estimated total cost

These values come from the backend simulation and metrics logic.

The frontend only displays them.

## Analyst evaluation metrics

After evaluating analyst decisions, the frontend displays:

- reviewed transactions
- correct analyst decisions
- incorrect analyst decisions
- analyst accuracy
- frauds missed by analyst
- legitimate transactions blocked by analyst

These metrics are calculated in frontend state from the currently loaded simulation batch.

They are not persisted.

## Technical details panel

Technical information is intentionally kept secondary in the UI.

The technical details panel can show:

- API base URL
- API version
- model type
- runtime information

These details are useful for development and verification but are not the main focus of the analyst workflow.

## Frontend API endpoints used

The frontend uses these backend endpoints:

```text
GET /health
GET /metadata
GET /simulation/batch
GET /simulation/metrics
```

Earlier development versions also used:

```text
GET /prediction/sample
```

The final analyst workflow primarily relies on batch simulation and metrics endpoints.

## CORS

The backend must allow requests from the frontend development server.

The frontend runs on:

```text
http://localhost:5173
```

The backend runs on:

```text
http://localhost:8000
```

Because these use different ports, the browser treats them as different origins.

The backend uses CORS configuration to allow the frontend to call the API during development.

## What the frontend does not do

The frontend does not:

- load raw dataset files
- read Parquet files directly
- run Spark
- load the trained model
- calculate model predictions
- calculate backend business metrics
- persist analyst decisions
- replace backend validation or simulation logic

The frontend consumes backend API responses and renders an interactive analyst-facing interface.

## Known limitations

Current limitations:

- analyst decisions are stored only in frontend state
- decisions are reset when a new batch is loaded
- true labels are available because this is a simulation dataset
- real banking workflows would usually receive fraud confirmation later
- transaction details are limited by the current backend response
- no authentication or user accounts are implemented
- no persistent decision history is implemented
- no production deployment configuration is included yet

Possible future improvements:

- persist analyst decisions through a backend endpoint
- add transaction-level domain fields such as amount, type, origin balance, and destination balance
- add historical analyst performance
- add exportable reports
- add richer evaluation charts
- add frontend tests
- improve final production styling