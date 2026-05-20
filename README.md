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

This project uses a dataset from Kaggle: [link](https://www.kaggle.com/datasets/rupakroy/online-payments-fraud-detection-dataset)

To download the dataset automatically, inside the docker container, run:

```bash
python3 scripts/download_data.py
```

Alternatively, download the dataset manually from Kaggle and place it in: `data/raw/`

For detailed setup instructions, see: `scripts/README.md`

## Running the project

### Docker development environment

This project uses Docker as the main runtime environment for Spark-based scripts and application code.

The recommended workflow is:

- use the local system only for editing files,
- run Spark, model, and simulation scripts inside Docker,
- start Jupyter Lab only when notebook-based exploration is needed.

#### Build the Docker image

Run from the project root directory:

```bash
docker compose build --no-cache
```

#### Start the application container

```bash
docker compose up -d app
```

This starts the main development container without Jupyter Lab.

#### Open a shell inside the container

```bash
docker compose exec app bash
```

Inside the container, the project is mounted at: `/app`

#### Verify runtime versions

Run inside the container:

```bash
python3 --version
python3 -c "import pyspark; print(pyspark.__version__)"
python3 -c "import pandas; print(pandas.__version__)"
```

Expected core versions:

```text
PySpark: 3.5.0
pandas: 2.0.3
```

#### Run sample prediction

The sample prediction script verifies that the trained model can be loaded and used on processed test data.

Required local artifacts: `data/processed/test/`, `models/fraud_model/`

These artifacts are not tracked by Git and must be generated locally.

Run inside the container:

```bash
python3 scripts/predict_sample.py
```

The script loads a small batch from `data/processed/test`, applies the trained Spark MLlib model from `models/fraud_model`, and prints prediction results.

#### Start Jupyter Lab only when needed

To start Jupyter Lab:

```bash
docker compose --profile jupyter up -d jupyter
```

Then open: `http://localhost:8888`

Token: `fraud123`

#### Stop containers

```bash
docker compose down
```

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


## Data Preprocessing

Data preprocessing is implemented in PySpark and available in: `notebooks/02_preprocessing.ipynb`

The pipeline includes:
- feature engineering (balance deltas, error flags)
- log transformation of transaction amount
- categorical encoding
- cleaned dataset export to `data/processed/`

## Data Pipeline

- `notebooks/01_eda.ipynb` – exploratory data analysis
- `notebooks/02_preprocessing.ipynb` – data cleaning and feature engineering
- `notebooks/03_dataset_preparation.ipynb` – final dataset preparation for ML

Additional details about dataset and ML setup are available in:
- `docs/eda.md`
- `docs/ml_dataset.md`

## Model Training
Model training was initially developed and validated in notebooks:

- `notebooks/04_model_setup.ipynb` – loading prepared datasets and verifying ML-ready structure
- `notebooks/05_baseline_model.ipynb` – baseline Random Forest model training
- `notebooks/06_model_evaluation.ipynb` – model evaluation and metrics calculation
- `notebooks/07_handle_imbalance.ipynb` – handling class imbalance using class weighting
- `notebooks/08_model_persistence.ipynb` – saving and loading trained model for reuse in API and simulation

The current trained model is expected at: `models/fraud_model/`

### Reproducible model training

The model can be regenerated without running notebooks by using the training script.

The script expects processed training data at:

`data/processed/train/`

Run inside the Docker container:

```bash
python3 scripts/train_model.py
```
The script:

- loads processed training data,
- adds class weights for imbalanced fraud detection,
- trains a Spark MLlib Random Forest pipeline,
- saves the trained model to models/fraud_model/.

After training, verify the model with:

```bash
python3 scripts/predict_sample.py
```