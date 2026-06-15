echo "Pobierz dane zgodnie z instrukcją w dokumentacji projektu."
docker compose build
docker compose up -d
docker compose exec app python3 scripts/prepare_data.py
docker compose exec app python3 scripts/train_model.py
docker compose exec app python3 scripts/predict_sample.py
start http://localhost:5173
start http://localhost:8000/docs