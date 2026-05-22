from fastapi import FastAPI

from src.api.routes.decision import router as decision_router
from src.api.routes.prediction import router as prediction_router
from src.api.routes.system import router as system_router
from src.api.schemas import RootResponse


app = FastAPI(
    title="CaptUReFraud API",
    description="Backend API for fraud detection prediction and simulation.",
    version="0.1.0",
)

app.include_router(system_router)
app.include_router(prediction_router)
app.include_router(decision_router)


@app.get("/", response_model=RootResponse)
def read_root() -> RootResponse:
    return RootResponse(
        name="CaptUReFraud API",
        status="running",
    )