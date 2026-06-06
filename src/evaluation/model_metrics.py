"""Model evaluation metrics for fraud classification.

This module contains reusable metric logic for binary fraud classification.
It intentionally does not depend on Spark, FastAPI, or frontend code.

Expected labels:
- 0 = legitimate transaction
- 1 = fraud transaction

Expected predictions:
- 0 = predicted legitimate
- 1 = predicted fraud
"""

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple


@dataclass(frozen=True)
class ConfusionMatrix:
    """Confusion matrix values for binary fraud classification."""

    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int

    @property
    def total(self) -> int:
        """Return total number of evaluated records."""
        return (
            self.true_positives
            + self.false_positives
            + self.true_negatives
            + self.false_negatives
        )


@dataclass(frozen=True)
class ModelPerformanceMetrics:
    """Standard model performance metrics for binary classification."""

    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    total: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    false_negative_rate: float


def calculate_confusion_matrix(
    labels: Sequence[int],
    predictions: Sequence[int],
) -> ConfusionMatrix:
    """Calculate confusion matrix values from labels and predictions.

    Args:
        labels: True binary labels. 0 means legitimate, 1 means fraud.
        predictions: Predicted binary classes. 0 means legitimate, 1 means fraud.

    Returns:
        ConfusionMatrix with TP, FP, TN, FN counts.

    Raises:
        ValueError: If inputs have different lengths, are empty, or contain
            values other than 0 and 1.
    """
    if len(labels) != len(predictions):
        raise ValueError("Labels and predictions must have the same length.")

    if len(labels) == 0:
        raise ValueError("Labels and predictions must not be empty.")

    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0

    for label, prediction in zip(labels, predictions):
        normalized_label = _validate_binary_value(label, "label")
        normalized_prediction = _validate_binary_value(prediction, "prediction")

        if normalized_label == 1 and normalized_prediction == 1:
            true_positives += 1
        elif normalized_label == 0 and normalized_prediction == 1:
            false_positives += 1
        elif normalized_label == 0 and normalized_prediction == 0:
            true_negatives += 1
        elif normalized_label == 1 and normalized_prediction == 0:
            false_negatives += 1

    return ConfusionMatrix(
        true_positives=true_positives,
        false_positives=false_positives,
        true_negatives=true_negatives,
        false_negatives=false_negatives,
    )


def calculate_model_performance_metrics(
    labels: Sequence[int],
    predictions: Sequence[int],
) -> ModelPerformanceMetrics:
    """Calculate model performance metrics from labels and predictions.

    Metrics:
    - accuracy: all correct predictions divided by all records
    - precision: fraud predictions that were actually fraud
    - recall: fraud cases that were detected
    - F1 score: harmonic mean of precision and recall
    - false positive rate: legitimate cases incorrectly predicted as fraud
    - false negative rate: fraud cases incorrectly predicted as legitimate
    """
    confusion_matrix = calculate_confusion_matrix(labels, predictions)

    return calculate_metrics_from_confusion_matrix(confusion_matrix)


def calculate_metrics_from_confusion_matrix(
    confusion_matrix: ConfusionMatrix,
) -> ModelPerformanceMetrics:
    """Calculate performance metrics from a confusion matrix."""
    tp = confusion_matrix.true_positives
    fp = confusion_matrix.false_positives
    tn = confusion_matrix.true_negatives
    fn = confusion_matrix.false_negatives
    total = confusion_matrix.total

    accuracy = _safe_divide(tp + tn, total)
    precision = _safe_divide(tp, tp + fp)
    recall = _safe_divide(tp, tp + fn)
    f1_score = _safe_divide(2 * precision * recall, precision + recall)
    false_positive_rate = _safe_divide(fp, fp + tn)
    false_negative_rate = _safe_divide(fn, fn + tp)

    return ModelPerformanceMetrics(
        true_positives=tp,
        false_positives=fp,
        true_negatives=tn,
        false_negatives=fn,
        total=total,
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        false_positive_rate=false_positive_rate,
        false_negative_rate=false_negative_rate,
    )


def rows_to_labels_and_predictions(
    rows: Iterable[object],
    label_field: str = "label",
    prediction_field: str = "prediction",
) -> Tuple[List[int], List[int]]:
    """Extract labels and predictions from row-like objects.

    This helper is useful for converting Spark Row objects or simple Python
    objects into lists accepted by the metric functions.

    Args:
        rows: Iterable of row-like objects. Supported forms:
            - dict-like objects
            - objects with attributes
        label_field: Field containing true label.
        prediction_field: Field containing predicted class.

    Returns:
        Tuple of labels list and predictions list.
    """
    labels: List[int] = []
    predictions: List[int] = []

    for row in rows:
        labels.append(_read_row_value(row, label_field))
        predictions.append(_read_row_value(row, prediction_field))

    return labels, predictions


def _read_row_value(row: object, field_name: str) -> int:
    """Read a value from a dict-like or attribute-like row object."""
    if isinstance(row, dict):
        return int(row[field_name])

    return int(getattr(row, field_name))


def _validate_binary_value(value: int, value_name: str) -> int:
    """Validate that a value is binary and normalize it to int."""
    normalized_value = int(value)

    if normalized_value not in (0, 1):
        raise ValueError(f"{value_name} must be 0 or 1.")

    return normalized_value


def _safe_divide(numerator: float, denominator: float) -> float:
    """Divide two numbers and return 0.0 when denominator is zero."""
    if denominator == 0:
        return 0.0

    return numerator / denominator