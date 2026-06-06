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

## Dataset

This project uses a dataset from Kaggle: [Online Payments Fraud Detection Dataset](https://www.kaggle.com/datasets/rupakroy/online-payments-fraud-detection-dataset)

Raw data is not tracked by Git.

For dataset setup instructions, see: [`docs/data_setup.md`](docs/data_setup.md).

## Running the project

The project is intended to run inside Docker.

For Docker setup and runtime commands, see: [`docs/docker.md`](docs/docker.md).

For simulation scripts, see: [`docs/simulation.md`](docs/simulation.md).

## Documentation

- [Dataset setup](docs/data_setup.md) – Kaggle dataset download and raw data setup
- [Docker setup](docs/docker.md) – Docker runtime, app container, Jupyter profile, and basic commands
- [EDA notes](docs/eda.md) – exploratory data analysis observations and fraud distribution notes
- [Data pipeline](docs/data_pipeline.md) – preprocessing, feature engineering, and train/test dataset preparation
- [ML dataset](docs/ml_dataset.md) – structure of the final Spark ML dataset with `features` and `label`
- [Model overview](docs/model.md) – Random Forest model, class weighting, training, prediction output, and persistence
- [Simulation engine](docs/simulation.md) – prediction interface, decision logic, feedback tracking, metrics, and batch simulation
- [Backend API](docs/api.md) – FastAPI backend endpoints for prediction, simulation, and metrics
- [Frontend UI](docs/frontend.md) – React dashboard for fraud monitoring, threshold experimentation, and analyst decision simulation
- [Evaluation](docs/evaluation.md) – model performance metrics, confusion matrix, business impact, and analyst decision quality
- [Development workflow](docs/development.md) – Git workflow, commit convention, tests, and local artifacts
