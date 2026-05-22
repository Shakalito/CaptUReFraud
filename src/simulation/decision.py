from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Decision = Literal["allow", "block"]


@dataclass(frozen=True)
class DecisionResult:
    decision: Decision
    probability: float
    threshold: float


def make_decision(probability: float, threshold: float = 0.5) -> DecisionResult:
    if not 0.0 <= probability <= 1.0:
        raise ValueError("Probability must be between 0.0 and 1.0.")

    if not 0.0 <= threshold <= 1.0:
        raise ValueError("Threshold must be between 0.0 and 1.0.")

    decision: Decision = "block" if probability >= threshold else "allow"

    return DecisionResult(
        decision=decision,
        probability=probability,
        threshold=threshold,
    )