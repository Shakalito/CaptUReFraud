# Model overview

---

## Model type

Random Forest classifier using Spark MLlib.

## Problem

Binary classification:

- `0` – legitimate transaction
- `1` – fraud

## Input

The model expects processed input data with:

- `features` column: Spark ML vector used for prediction,
- `label` column: target variable used during training and evaluation.

The processed dataset also keeps selected transaction fields, such as `step`, `type`, `amount`, and balance columns, so the API and frontend can display transaction details. These fields are not a replacement for the assembled `features` vector used by the model.

Raw transactions must be transformed by the preprocessing pipeline before prediction.

## Training data

Model is trained on: `data/processed/train/`

Tested on: `data/processed/test/`

The test dataset is also used by the simulation API as the source of simulated incoming transaction batches after the model has already been trained.

## Reproducible model training

The model can be regenerated without running notebooks by using the training script.

From the project root, start the Docker services:

```bash
docker compose up -d
```

Before training, make sure processed datasets exist.

If needed, generate them from raw data:

```bash
docker compose exec app python3 scripts/prepare_data.py
```

Then train the model:

```bash
docker compose exec app python3 scripts/train_model.py
```

The script:

- loads processed training data from `data/processed/train/`,
- adds class weights for imbalanced fraud detection,
- trains a Spark MLlib Random Forest pipeline,
- saves the trained model to `models/fraud_model/`.

After training, verify the model with:

```bash
docker compose exec app python3 scripts/predict_sample.py
```

The startup scripts can also run the setup workflow automatically:

```bash
start.bat
```

or:

```bash
./start.sh
```

## Imbalance handling

The dataset has severe class imbalance.

Fraud transactions represent only a small percentage of all transactions.

Class imbalance is handled using class weighting through Spark MLlib `weightCol`.

This helps the model pay more attention to the minority fraud class.

## Performance focus

Primary metric:

- fraud recall: minimize missed fraud cases.

Secondary metrics:

- precision,
- F1-score,
- confusion matrix.

## Output

The model produces:

- `prediction`: predicted class, `0` or `1`,
- `probability`: vector with class probabilities.

For fraud detection, the important value is the probability of class `1`.

The API converts this fraud probability into an operational decision using the selected threshold:

```text
fraud_probability >= threshold -> block
fraud_probability < threshold  -> allow
```

The default threshold is `0.8`.

## Persistence

The trained model is saved to: `models/fraud_model/`

The directory is not tracked by Git and should be regenerated locally.

The model is saved as a Spark PipelineModel and can be loaded using:

```bash
PipelineModel.load("models/fraud_model")
```

## Notes

- The persisted model is saved as a Spark `PipelineModel`.
- The current prediction interface expects processed input data with a `features` column.
- Raw transactions must be transformed by the preprocessing pipeline before prediction.
- Feature order and vector structure must match the training pipeline.
- Do not modify processed datasets manually.
