import pytest

from src.simulation.feedback import build_feedback, classify_prediction_outcome


def test_classify_true_positive():
    assert classify_prediction_outcome(true_label=1, predicted_label=1) == "TP"


def test_classify_false_positive():
    assert classify_prediction_outcome(true_label=0, predicted_label=1) == "FP"


def test_classify_true_negative():
    assert classify_prediction_outcome(true_label=0, predicted_label=0) == "TN"


def test_classify_false_negative():
    assert classify_prediction_outcome(true_label=1, predicted_label=0) == "FN"


def test_build_feedback_for_detected_fraud():
    result = build_feedback(true_label=1, predicted_label=1, decision="block")

    assert result.prediction_outcome == "TP"
    assert result.fraud_correctly_detected is True
    assert result.fraud_missed is False


def test_build_feedback_for_missed_fraud():
    result = build_feedback(true_label=1, predicted_label=0, decision="allow")

    assert result.prediction_outcome == "FN"
    assert result.fraud_missed is True
    assert result.fraud_correctly_detected is False


def test_build_feedback_for_incorrectly_blocked_legit_transaction():
    result = build_feedback(true_label=0, predicted_label=1, decision="block")

    assert result.prediction_outcome == "FP"
    assert result.legit_incorrectly_blocked is True


def test_reject_invalid_true_label():
    with pytest.raises(ValueError):
        classify_prediction_outcome(true_label=2, predicted_label=0)


def test_reject_invalid_decision():
    with pytest.raises(ValueError):
        build_feedback(true_label=0, predicted_label=0, decision="review")