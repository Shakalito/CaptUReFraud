# Model Overview

## Model Type

Random Forest classifier (Spark MLlib)

## Problem

Binary classification:
- 0 → legitimate transaction
- 1 → fraud

## Input

Model expects:
- `features` column (Vector)
- generated using VectorAssembler

## Training

Model is trained on:
- `/data/processed/train`

Tested on:
- `/data/processed/test`

## Imbalance Handling

Severe class imbalance (~0.13% fraud)

Handled using:
- class weighting (`weightCol`)

## Performance Focus

Primary metric:
- Fraud Recall (minimize missed fraud cases)

Secondary:
- Precision
- F1-score

## Output

Model produces:
- `prediction` (0 or 1)
- `probability` (confidence score)

## Persistence

Saved to:
`/models/fraud_model`


Can be loaded using:
`PipelineModel.load(...)` 

### Notes
- Model is part of full pipeline (no manual preprocessing needed)
- Features must match training pipeline
- Do not modify processed datasets manually