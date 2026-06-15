echo "Starting training process..."
docker compose exec app python3 scripts/prepare_data.py
docker compose exec app python3 scripts/train_model.py
docker compose exec app python3 scripts/predict_sample.py