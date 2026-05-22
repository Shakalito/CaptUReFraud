from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    name: str
    status: str


class HealthResponse(BaseModel):
    status: str


class MetadataResponse(BaseModel):
    project: str
    api_version: str
    model_type: str
    runtime: str
    requires_model: bool


class DecisionRequest(BaseModel):
    fraud_probability: float = Field(ge=0.0, le=1.0)
    threshold: float = Field(default=0.8, ge=0.0, le=1.0)


class DecisionResponse(BaseModel):
    fraud_probability: float
    threshold: float
    decision: Literal["allow", "block"]


class PredictionResponse(BaseModel):
    prediction: int
    fraud_probability: float
    threshold: float = 0.8
    probability: Optional[List[float]] = None


class SimulationRecordResponse(BaseModel):
    label: int
    prediction: int
    fraud_probability: float
    decision: Literal["allow", "block"]
    prediction_outcome: Literal["TP", "FP", "TN", "FN"]
    fraud_correctly_detected: bool
    fraud_missed: bool
    legit_correctly_allowed: bool
    legit_incorrectly_blocked: bool


class BatchSimulationResponse(BaseModel):
    threshold: float
    count: int
    records: List[SimulationRecordResponse]


class BusinessMetricsResponse(BaseModel):
    total_transactions: int
    total_frauds: int
    detected_frauds: int
    missed_frauds: int
    blocked_legit_transactions: int
    fraud_recall: float
    estimated_fraud_loss: float
    estimated_blocking_cost: float
    estimated_total_cost: float


class ErrorResponse(BaseModel):
    error: str
    detail: str