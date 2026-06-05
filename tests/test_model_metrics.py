import pytest

from src.evaluation.model_metrics import (
    ConfusionMatrix,
    calculate_confusion_matrix,
    calculate_metrics_from_confusion_matrix,
    calculate_model_performance_metrics,
    rows_to_labels_and_predictions,
)


def test_calculate_confusion_matrix_counts_binary_classification_outcomes():
    labels = [1, 1, 0, 0, 1, 0]
    predictions = [1, 0, 1, 0, 1, 0]

    result = calculate_confusion_matrix(labels, predictions)

    assert result.true_positives == 2
    assert result.false_positives == 1
    assert result.true_negatives == 2
    assert result.false_negatives == 1
    assert result.total == 6


def test_calculate_model_performance_metrics_from_labels_and_predictions():
    labels = [1, 1, 0, 0, 1, 0]
    predictions = [1, 0, 1, 0, 1, 0]

    result = calculate_model_performance_metrics(labels, predictions)

    assert result.true_positives == 2
    assert result.false_positives == 1
    assert result.true_negatives == 2
    assert result.false_negatives == 1
    assert result.total == 6
    assert result.accuracy == pytest.approx(4 / 6)
    assert result.precision == pytest.approx(2 / 3)
    assert result.recall == pytest.approx(2 / 3)
    assert result.f1_score == pytest.approx(2 / 3)
    assert result.false_positive_rate == pytest.approx(1 / 3)
    assert result.false_negative_rate == pytest.approx(1 / 3)


def test_calculate_metrics_from_confusion_matrix_handles_zero_division():
    confusion_matrix = ConfusionMatrix(
        true_positives=0,
        false_positives=0,
        true_negatives=10,
        false_negatives=0,
    )

    result = calculate_metrics_from_confusion_matrix(confusion_matrix)

    assert result.total == 10
    assert result.accuracy == 1.0
    assert result.precision == 0.0
    assert result.recall == 0.0
    assert result.f1_score == 0.0
    assert result.false_positive_rate == 0.0
    assert result.false_negative_rate == 0.0


def test_calculate_confusion_matrix_rejects_empty_input():
    with pytest.raises(ValueError, match="must not be empty"):
        calculate_confusion_matrix([], [])


def test_calculate_confusion_matrix_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="same length"):
        calculate_confusion_matrix([1, 0], [1])


def test_calculate_confusion_matrix_rejects_non_binary_labels():
    with pytest.raises(ValueError, match="label must be 0 or 1"):
        calculate_confusion_matrix([1, 2], [1, 0])


def test_calculate_confusion_matrix_rejects_non_binary_predictions():
    with pytest.raises(ValueError, match="prediction must be 0 or 1"):
        calculate_confusion_matrix([1, 0], [1, 2])


def test_rows_to_labels_and_predictions_extracts_values_from_dicts():
    rows = [
        {"label": 1, "prediction": 1},
        {"label": 0, "prediction": 1},
    ]

    labels, predictions = rows_to_labels_and_predictions(rows)

    assert labels == [1, 0]
    assert predictions == [1, 1]


def test_rows_to_labels_and_predictions_extracts_values_from_objects():
    class RowLike:
        def __init__(self, label, prediction):
            self.label = label
            self.prediction = prediction

    rows = [
        RowLike(label=1, prediction=0),
        RowLike(label=0, prediction=0),
    ]

    labels, predictions = rows_to_labels_and_predictions(rows)

    assert labels == [1, 0]
    assert predictions == [0, 0]