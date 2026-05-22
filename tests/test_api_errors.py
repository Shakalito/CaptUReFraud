from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.errors import ApiError, api_error_handler


def test_api_error_handler_returns_structured_json():
    app = FastAPI()
    app.add_exception_handler(ApiError, api_error_handler)

    @app.get("/raise-api-error")
    def raise_api_error():
        raise ApiError(
            status_code=503,
            error="Model not found",
            detail="Run scripts/train_model.py before using prediction endpoints.",
        )

    client = TestClient(app)

    response = client.get("/raise-api-error")

    assert response.status_code == 503
    assert response.json() == {
        "error": "Model not found",
        "detail": "Run scripts/train_model.py before using prediction endpoints.",
    }