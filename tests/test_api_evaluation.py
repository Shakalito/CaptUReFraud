from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routes import evaluation
from src.api.schemas import EvaluationMetricsResponse


client = TestClient(app)


def test_evaluation_model_endpoint_returns_metrics(monkeypatch):
    expected_response = EvaluationMetricsResponse(
        threshold=0.8,
        true_positives=8,
        false_positives=1,
        true_negatives=10,
        false_negatives=2,
        total=21,
        accuracy=18 / 21,
        precision=8 / 9,
        recall=8 / 10,
        f1_score=0.8421052631578948,
        false_positive_rate=1 / 11,
        false_negative_rate=2 / 10,
    )

    def fake_calculate_evaluation_response(threshold):
        assert threshold == 0.8
        return expected_response

    monkeypatch.setattr(
        evaluation,
        "calculate_evaluation_response",
        fake_calculate_evaluation_response,
    )

    response = client.get("/evaluation/model?threshold=0.8")

    assert response.status_code == 200
    assert response.json() == {
        "threshold": 0.8,
        "true_positives": 8,
        "false_positives": 1,
        "true_negatives": 10,
        "false_negatives": 2,
        "total": 21,
        "accuracy": 18 / 21,
        "precision": 8 / 9,
        "recall": 8 / 10,
        "f1_score": 0.8421052631578948,
        "false_positive_rate": 1 / 11,
        "false_negative_rate": 2 / 10,
    }


def test_evaluation_model_endpoint_uses_default_threshold(monkeypatch):
    expected_response = EvaluationMetricsResponse(
        threshold=0.8,
        true_positives=1,
        false_positives=0,
        true_negatives=1,
        false_negatives=0,
        total=2,
        accuracy=1.0,
        precision=1.0,
        recall=1.0,
        f1_score=1.0,
        false_positive_rate=0.0,
        false_negative_rate=0.0,
    )

    def fake_calculate_evaluation_response(threshold):
        assert threshold == 0.8
        return expected_response

    monkeypatch.setattr(
        evaluation,
        "calculate_evaluation_response",
        fake_calculate_evaluation_response,
    )

    response = client.get("/evaluation/model")

    assert response.status_code == 200
    assert response.json()["threshold"] == 0.8


def test_evaluation_model_endpoint_rejects_invalid_threshold():
    response = client.get("/evaluation/model?threshold=1.5")

    assert response.status_code == 422