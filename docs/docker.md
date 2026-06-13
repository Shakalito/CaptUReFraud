# Docker setup

---

## Docker development environment

This project uses Docker as the main runtime environment for Spark-based scripts, backend API, frontend UI, and application code.

The recommended workflow is:

- use the local system only for editing files,
- run Spark, model, simulation, and backend commands inside Docker,
- start the default application stack with Docker Compose,
- start Jupyter Lab only when notebook-based exploration is needed.

A separate Python virtual environment is not required inside the Docker container.

---

## Build containers

Run from the project root directory:

```bash
docker compose build
```

For a clean rebuild:

```bash
docker compose build --no-cache
```

---

## Start the default application stack

```bash
docker compose up -d
```

This starts the default application stack:

- FastAPI backend
- React/Vite frontend

Jupyter Lab is not started by default.

Available URLs:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

---

## Start only the backend/app service

```bash
docker compose up -d app
```

This starts only the backend/app container.

Use this mode when you only need the backend container for API development, tests, Spark scripts, or backend commands.

Open a shell inside the container:

```bash
docker compose exec app bash
```

Inside the container, the project is mounted at:
`/app`


---

## Verify runtime versions

Run inside the app container:

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

---

## Run backend tests

Run inside the app container:

```bash
python3 -m pytest tests
```

---

## Run sample prediction

The sample prediction script verifies that the trained model can be loaded and used on processed test data.

Required local artifacts:

- `data/processed/test/`
- `models/fraud_model/`

These artifacts are not tracked by Git and must be generated locally.

Run inside the app container:

```bash
python3 scripts/predict_sample.py
```

The script loads a small batch from `data/processed/test`, applies the trained Spark MLlib model from `models/fraud_model`, and prints prediction results.

---

## Start optional Jupyter Lab

Jupyter Lab is optional and does not start with the default application stack.

To start Jupyter Lab:

```bash
docker compose --profile jupyter up -d jupyter
```

Then open: 
`http://localhost:8888`

Token: 
`fraud123`

---

## Start backend, frontend and Jupyter

```bash
docker compose --profile jupyter up -d
```

This starts:

- FastAPI backend
- React/Vite frontend
- Jupyter Lab

---

## Stop containers

```bash
docker compose down
```

Use `docker compose stop` only if you want to stop containers without removing them.