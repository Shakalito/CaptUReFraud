from typing import Dict

from fastapi import FastAPI


app = FastAPI(
    title="CaptUReFraud API",
    description="Backend API for fraud detection prediction and simulation.",
    version="0.1.0",
)


@app.get("/")
def read_root() -> Dict[str, str]:
    return {
        "name": "CaptUReFraud API",
        "status": "running",
    }