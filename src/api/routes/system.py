from typing import Dict, Union

from fastapi import APIRouter


router = APIRouter(tags=["system"])


@router.get("/health")
def health_check() -> Dict[str, str]:
    return {
        "status": "ok",
    }


@router.get("/metadata")
def get_metadata() -> Dict[str, Union[str, bool]]:
    return {
        "project": "CaptUReFraud",
        "api_version": "0.1.0",
        "model_type": "Spark MLlib Random Forest",
        "runtime": "Docker",
        "requires_model": False,
    }