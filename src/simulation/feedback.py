from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


PredictionOutcome = Literal["TP", "FP", "TN", "FN"]


@dataclass(frozen=True)
class FeedbackResult:
    prediction_outcome: PredictionOutcome
    fraud_correctly_detected: bool
    fraud_missed: bool
    legit_correctly_allowed: bool
    legit_incorrectly_blocked: bool


def classify_prediction_outcome(true_label: int, predicted_label: int) -> PredictionOutcome:
    if true_label not in (0, 1):
        raise ValueError("True label must be 0 or 1.")

    if predicted_label not in (0, 1):
        raise ValueError("Predicted label must be 0 or 1.")

    if true_label == 1 and predicted_label == 1:
        return "TP"

    if true_label == 0 and predicted_label == 1:
        return "FP"

    if true_label == 0 and predicted_label == 0:
        return "TN"

    return "FN"


def build_feedback(true_label: int, predicted_label: int, decision: str) -> FeedbackResult:
    if decision not in ("allow", "block"):
        raise ValueError("Decision must be 'allow' or 'block'.")

    outcome = classify_prediction_outcome(
        true_label=true_label,
        predicted_label=predicted_label,
    )

    return FeedbackResult(
        prediction_outcome=outcome,
        fraud_correctly_detected=true_label == 1 and decision == "block",
        fraud_missed=true_label == 1 and decision == "allow",
        legit_correctly_allowed=true_label == 0 and decision == "allow",
        legit_incorrectly_blocked=true_label == 0 and decision == "block",
    )