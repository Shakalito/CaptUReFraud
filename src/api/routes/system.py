from fastapi import APIRouter

from src.api.schemas import HealthResponse, MetadataResponse


router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
    )


@router.get("/metadata", response_model=MetadataResponse)
def get_metadata() -> MetadataResponse:
    return MetadataResponse(
        project="CaptUReFraud",
        api_version="0.1.0",
        model_type="Spark MLlib Random Forest",
        runtime="Docker",
        requires_model=False,
    )