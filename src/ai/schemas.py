from pydantic import BaseModel, Field
from typing import Literal


class EvidenceBackedObservation(BaseModel):
    observation: str = Field(min_length=1, max_length=1200)
    evidence_event_ids: list[int] = Field(default_factory=list)


class Hypothesis(BaseModel):
    description: str = Field(min_length=1, max_length=1200)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_event_ids: list[int] = Field(default_factory=list)


