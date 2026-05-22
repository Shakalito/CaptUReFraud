from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_root_endpoint_returns_api_status():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "CaptUReFraud API",
        "status": "running",
    }


def test_health_endpoint_returns_ok_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


def test_metadata_endpoint_returns_runtime_information():
    response = client.get("/metadata")

    assert response.status_code == 200

    payload = response.json()

    assert payload["project"] == "CaptUReFraud"
    assert payload["api_version"] == "0.1.0"
    assert payload["model_type"] == "Spark MLlib Random Forest"
    assert payload["runtime"] == "Docker"
    assert payload["requires_model"] is False