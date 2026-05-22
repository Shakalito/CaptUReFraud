from typing import Dict

from fastapi import FastAPI

from src.api.routes.system import router as system_router


app = FastAPI(
    title="CaptUReFraud API",
    description="Backend API for fraud detection prediction and simulation.",
    version="0.1.0",
)

app.include_router(system_router)


@app.get("/")
def read_root() -> Dict[str, str]:
    return {
        "name": "CaptUReFraud API",
        "status": "running",
    }