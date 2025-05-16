from pydantic import BaseModel, Field
from typing import Literal


class EvidenceBackedObservation(BaseModel):
    observation: str = Field(min_length=1, max_length=1200)
    evidence_event_ids: list[int] = Field(default_factory=list)


class Hypothesis(BaseModel):
    description: str = Field(min_length=1, max_length=1200)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_event_ids: list[int] = Field(default_factory=list)


class RecommendedAction(BaseModel):
    action: str = Field(min_length=1, max_length=200)
    reason: str = Field(min_length=1, max_length=1200)
    requires_approval: bool = True


class InvestigationResult(BaseModel):
    summary: str = Field(min_length=1, max_length=4000)
    severity_assessment: Literal["low", "medium", "high", "critical"]
    confidence: float = Field(ge=0.0, le=1.0)
    observations: list[EvidenceBackedObservation] = Field(default_factory=list, max_length=20)
    hypotheses: list[Hypothesis] = Field(default_factory=list, max_length=10)
    recommended_actions: list[RecommendedAction] = Field(default_factory=list, max_length=10)
