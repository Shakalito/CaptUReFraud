#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "=================================================="
echo "CaptUReFraud startup"
echo "=================================================="
echo
echo "This script will:"
echo "1. Check Docker availability"
echo "2. Download the dataset if it is missing"
echo "3. Build and start Docker services"
echo "4. Prepare data, train the model and run a sample prediction"
echo

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker command was not found."
  echo "Install Docker and make sure it is available in PATH."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is not running."
  echo "Start Docker and run this script again."
  exit 1
fi

echo "Checking/downloading dataset..."
python3 scripts/download_data.py

echo
echo "Building Docker images..."
docker compose build

echo
echo "Starting Docker services..."
docker compose up -d

echo
echo "Preparing processed data..."
docker compose exec app python3 scripts/prepare_data.py

echo
echo "Training model..."
docker compose exec app python3 scripts/train_model.py

echo
echo "Running sample prediction..."
docker compose exec app python3 scripts/predict_sample.py

echo
echo "=================================================="
echo "CaptUReFraud is ready."
echo "Frontend: http://localhost:5173"
echo "API docs: http://localhost:8000/docs"
echo "=================================================="

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://localhost:5173" >/dev/null 2>&1 || true
  xdg-open "http://localhost:8000/docs" >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
  open "http://localhost:5173" || true
  open "http://localhost:8000/docs" || true
fi