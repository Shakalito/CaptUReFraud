from fastapi import APIRouter

from src.api.schemas import DecisionRequest, DecisionResponse
from src.simulation.decision import make_decision


router = APIRouter(
    tags=["decision"],
)


@router.post("/decision", response_model=DecisionResponse)
def create_decision(request: DecisionRequest) -> DecisionResponse:
    decision_result = make_decision(
        request.fraud_probability,
        request.threshold,
    )

    return DecisionResponse(
        fraud_probability=request.fraud_probability,
        threshold=request.threshold,
        decision=decision_result.decision,
    )