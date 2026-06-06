# Docker setup

--- 

## Docker development environment

This project uses Docker as the main runtime environment for Spark-based scripts and application code.

The recommended workflow is:

- use the local system only for editing files,
- run Spark, model, and simulation scripts inside Docker,
- start Jupyter Lab only when notebook-based exploration is needed.

A separate Python virtual environment is not required inside the Docker container.

### Build the Docker image

Run from the project root directory:

```bash
docker compose build --no-cache
```

### Start the application container

```bash
docker compose up -d
```

This starts the main development container without Jupyter Lab.

### Open a shell inside the container

```bash
docker compose exec app bash
```

Inside the container, the project is mounted at: `/app`

### Verify runtime versions

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

### Run sample prediction

The sample prediction script verifies that the trained model can be loaded and used on processed test data.

Required local artifacts: `data/processed/test/`, `models/fraud_model/`

These artifacts are not tracked by Git and must be generated locally.

Run inside the container:

```bash
python3 scripts/predict_sample.py
```

The script loads a small batch from `data/processed/test`, applies the trained Spark MLlib model from `models/fraud_model`, and prints prediction results.

### Start Jupyter Lab only when needed

To start Jupyter Lab:

```bash
docker compose --profile jupyter up -d jupyter
```

Then open: `http://localhost:8888`

Token: `fraud123`

### Stop containers

```bash
docker compose down
```
