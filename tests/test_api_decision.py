from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_decision_endpoint_returns_block_when_probability_reaches_threshold():
    response = client.post(
        "/decision",
        json={
            "fraud_probability": 0.82,
            "threshold": 0.8,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "fraud_probability": 0.82,
        "threshold": 0.8,
        "decision": "block",
    }


def test_decision_endpoint_returns_allow_when_probability_is_below_threshold():
    response = client.post(
        "/decision",
        json={
            "fraud_probability": 0.12,
            "threshold": 0.8,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "fraud_probability": 0.12,
        "threshold": 0.8,
        "decision": "allow",
    }


def test_decision_endpoint_uses_default_threshold():
    response = client.post(
        "/decision",
        json={
            "fraud_probability": 0.95,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "fraud_probability": 0.95,
        "threshold": 0.8,
        "decision": "block",
    }


def test_decision_endpoint_rejects_invalid_probability():
    response = client.post(
        "/decision",
        json={
            "fraud_probability": 1.5,
            "threshold": 0.8,
        },
    )

    assert response.status_code == 422


def test_decision_endpoint_rejects_invalid_threshold():
    response = client.post(
        "/decision",
        json={
            "fraud_probability": 0.5,
            "threshold": 1.5,
        },
    )

    assert response.status_code == 422