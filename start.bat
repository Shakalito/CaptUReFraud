@echo off
setlocal

cd /d "%~dp0"

echo ==================================================
echo CaptUReFraud startup
echo ==================================================
echo.
echo This script will:
echo 1. Check Docker availability
echo 2. Download the dataset if it is missing
echo 3. Build and start Docker services
echo 4. Prepare data, train the model and run a sample prediction
echo 5. Open the frontend and API documentation
echo.

where docker >nul 2>nul
if errorlevel 1 (
    echo ERROR: Docker command was not found.
    echo Install Docker Desktop and make sure it is available in PATH.
    goto error
)

docker info >nul 2>nul
if errorlevel 1 (
    echo ERROR: Docker is not running.
    echo Start Docker Desktop and run this script again.
    goto error
)

echo Checking/downloading dataset...
python scripts\download_data.py
if errorlevel 1 (
    echo.
    echo ERROR: Dataset setup failed.
    echo Configure Kaggle API or download the dataset manually into data\raw.
    goto error
)

echo.
echo Building Docker images...
docker compose build
if errorlevel 1 goto error

echo.
echo Starting Docker services...
docker compose up -d
if errorlevel 1 goto error

echo.
echo Preparing processed data...
docker compose exec app python3 scripts/prepare_data.py
if errorlevel 1 goto error

echo.
echo Training model...
docker compose exec app python3 scripts/train_model.py
if errorlevel 1 goto error

echo.
echo Running sample prediction...
docker compose exec app python3 scripts/predict_sample.py
if errorlevel 1 goto error

echo.
echo Opening application...
start "" "http://localhost:5173"

echo.
echo ==================================================
echo CaptUReFraud is ready.
echo Frontend: http://localhost:5173
echo API docs: http://localhost:8000/docs
echo ==================================================
echo.
pause
exit /b 0

:error
echo.
echo ==================================================
echo Startup failed. Check the error message above.
echo ==================================================
echo.
pause
exit /b 1