# CaptUReFraud

CaptUReFraud is a Spark-based fraud detection project focused on financial transaction analysis, model-based fraud prediction, and simulation of analyst decisions.

## Project structure

- `data/raw/` – raw downloaded dataset (not tracked)
- `data/processed/` – cleaned datasets and intermediate artifacts (not tracked)
- `notebooks/` – exploratory analysis and experiments
- `src/` – source code for data processing, modeling, simulation, and application logic
- `scripts/` – utility scripts for dataset handling, training, prediction, and development tasks
- `models/` – trained models (not tracked)
- `docs/` – additional project documentation

## Requirements

The recommended way to run this project is Docker-based.

Required:

- Docker Desktop / Docker Engine
- Docker Compose v2 (`docker compose` command)
- Kaggle dataset downloaded into `data/raw/`

Optional:

- Kaggle API token, if you want to download the dataset with `scripts/download_data.py`
- Python with Kaggle CLI installed, if running the dataset download script locally

## Dataset

This project uses a dataset from Kaggle: [Online Payments Fraud Detection Dataset](https://www.kaggle.com/datasets/rupakroy/online-payments-fraud-detection-dataset)

Raw data is not tracked by Git.

The dataset must be available in:

```text
 data/raw/
```

You can either:

- download it automatically with `scripts/download_data.py`, or
- download it manually from Kaggle and place the CSV file in `data/raw/`.

For detailed dataset setup instructions, see: [`docs/data_setup.md`](docs/data_setup.md).

## Quick start

The easiest way to start the project is to use the startup scripts from the project root.

### Windows

```powershell
.\start.bat
```

### Linux / macOS

```bash
chmod +x start.sh
./start.sh
```

The startup script checks Docker, downloads the dataset if needed, builds containers, starts the application stack, prepares processed data, trains the model, runs a sample prediction, and opens the frontend.

After startup, open:

```text
Frontend: http://localhost:5173
API docs: http://localhost:8000/docs
```

## Manual run

Use these commands if you prefer to run the setup step by step.

### 1. Download or prepare the dataset

From the project root:

```bash
python scripts/download_data.py
```

If you do not use the Kaggle API, download the dataset manually and place the CSV file in:

```text
data/raw/
```

### 2. Build Docker containers

```bash
docker compose build
```

### 3. Start the default application stack

```bash
docker compose up -d
```

This starts:

- FastAPI backend
- React/Vite frontend

Jupyter is not started by default.

### 4. Prepare data and train the model

```bash
docker compose exec app python3 scripts/prepare_data.py
docker compose exec app python3 scripts/train_model.py
docker compose exec app python3 scripts/predict_sample.py
```

### 5. Open the application

```text
Frontend: http://localhost:5173
Backend API: http://localhost:8000
API docs: http://localhost:8000/docs
```

## Optional Jupyter service

Jupyter is optional and is not required to run the application.

To start Jupyter:

```bash
docker compose --profile jupyter up -d jupyter
```

Then open:

```text
http://localhost:8888
```

## Stop the project

```bash
docker compose down
```

Or use the helper scripts:

### Windows

```powershell
.\stop.bat
```

### Linux / macOS

```bash
chmod +x stop.sh
./stop.sh
```

## Documentation

- [Dataset setup](docs/data_setup.md) – Kaggle dataset download and raw data setup
- [Docker setup](docs/docker.md) – Docker runtime, app container, Jupyter profile, and basic commands
- [EDA notes](docs/eda.md) – exploratory data analysis observations and fraud distribution notes
- [Data pipeline](docs/data_pipeline.md) – preprocessing, feature engineering, and train/test dataset preparation
- [ML dataset](docs/ml_dataset.md) – structure of the final Spark ML dataset with model features and business fields
- [Model overview](docs/model.md) – Random Forest model, class weighting, training, prediction output, and persistence
- [Simulation engine](docs/simulation.md) – prediction interface, decision logic, feedback tracking, metrics, and incoming transaction simulation
- [Backend API](docs/api.md) – FastAPI backend endpoints for prediction, simulation, evaluation, and metrics
- [Frontend UI](docs/frontend.md) – React dashboard for fraud monitoring, threshold experimentation, alerts, filtering, and analyst decision simulation
- [Evaluation](docs/evaluation.md) – model performance metrics, confusion matrix, business impact, and analyst decision quality
- [Development workflow](docs/development.md) – Git workflow, commit convention, tests, and local artifacts
