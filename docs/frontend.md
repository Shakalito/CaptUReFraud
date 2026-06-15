# Frontend UI

CaptUReFraud includes a React + Vite frontend for interacting with the FastAPI backend.

The frontend provides a fraud monitoring interface where a user can load simulated incoming transaction batches, adjust the fraud decision threshold, review model recommendations, inspect risk alerts, make analyst decisions, and evaluate those decisions after revealing known labels.

## Purpose

The frontend is designed as an analyst-oriented simulation interface.

It allows the user to:

- load simulated incoming transaction records from the backend API
- review fraud probabilities, risk levels, and system recommendations
- inspect suspicious and fraud-level alerts
- filter transactions by type, risk level, probability, and amount
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
docker compose exec app python3 scripts/prepare_data.py
docker compose exec app python3 scripts/train_model.py
```

The frontend itself does not create or load these artifacts directly.

## Starting the frontend

The recommended way to start the full application stack is from the project root:

```bash
docker compose up -d
```

This starts both:

- FastAPI backend on `http://localhost:8000`
- React/Vite frontend on `http://localhost:5173`

The helper scripts can also be used:

```text
start.bat
start.sh
```

They build/start the Docker services and run the required dataset/model setup steps.

## Production build check

To verify that the frontend can be built:

```bash
docker compose exec frontend npm run build
```

The build output is created in:

```text
frontend/dist/
```

The `dist/` directory is generated and should not be committed.

## Lint check

To check frontend code quality:

```bash
docker compose exec frontend npm run lint
```

This runs ESLint and checks for basic JavaScript/React issues such as unused variables, invalid imports, or common code-quality problems.

## Main UI workflow

The frontend is organized around a simple analyst simulation workflow.

### 1. Load incoming transactions

The user selects a batch size and clicks the button for fetching incoming transactions.

This fetches a randomized simulated transaction batch from the backend.

The frontend calls:

```text
GET /simulation/batch
GET /simulation/metrics
GET /evaluation/model
```

The backend handles Spark/model logic and returns structured API responses.

Each transaction can include:

- `transaction_id`
- transaction type
- transaction amount
- sender balance before and after the transaction
- receiver balance before and after the transaction
- fraud probability
- system decision
- risk level

Balance fields come directly from the PaySim dataset. For some transaction types, especially `PAYMENT` and `CASH_IN`, destination balances may remain zero because of how the simulator represents merchants and cash agents.

### 2. Review risk levels and alerts

The frontend assigns a simple risk level based on the fraud probability and currently selected threshold:

```text
OK          -> low probability
Suspicious  -> medium probability below the blocking threshold
Fraud       -> probability greater than or equal to the blocking threshold
```

Suspicious and fraud-level transactions are also shown in a dedicated alerts section.

Clicking an alert selects the related transaction in the analyst review panel.

### 3. Filter transactions

The transaction stream can be filtered by:

- transaction type
- risk level
- minimum fraud probability
- minimum amount

Filtering is frontend-only and does not retrain the model or change backend simulation results.

### 4. Review decisions

After loading transactions, the user can select rows in the transaction table.

For each selected transaction, the analyst review panel shows:

- model prediction
- fraud probability
- risk level
- system decision
- transaction details
- hidden true label before evaluation
- hidden prediction outcome before evaluation

The user can choose:

```text
allow
block
```

Analyst decisions are stored only in frontend state.

No backend persistence is used at this stage.

### 5. Evaluate results

After reviewing one or more transactions, the user can click the evaluation button.

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

The user can adjust the threshold with the slider and apply it.

Changing the threshold refreshes:

- simulation batch
- business metrics
- evaluation metrics

The threshold affects operational decisions without retraining the model.

Lower threshold generally means:

- more frauds detected
- fewer missed frauds
- more legitimate transactions may be blocked

Higher threshold generally means:

- fewer legitimate transactions blocked
- more frauds may be missed

The frontend displays this trade-off through business metrics and evaluation indicators.

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
GET /evaluation/model
```

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
