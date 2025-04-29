from pydantic import BaseModel, Field
from typing import Literal


class EvidenceBackedObservation(BaseModel):
    observation: str = Field(min_length=1, max_length=1200)
    evidence_event_ids: list[int] = Field(default_factory=list)


