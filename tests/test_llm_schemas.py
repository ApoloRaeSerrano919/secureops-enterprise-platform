import pytest
from pydantic import ValidationError
from src.ai.schemas import InvestigationResult


def test_investigation_result_accepts_grounded_output():
    result = InvestigationResult.model_validate({
        "summary": "Suspicious authentication sequence observed.",
        "severity_assessment": "high",
        "confidence": 0.9,
        "observations": [{"observation": "Failed logins occurred.", "evidence_event_ids": [1, 2]}],
        "hypotheses": [{"description": "Possible account compromise.", "confidence": 0.7, "evidence_event_ids": [1, 2]}],
        "recommended_actions": [{"action": "review_auth_activity", "reason": "Validate user activity.", "requires_approval": False}],
    })
    assert result.confidence == 0.9
    assert result.observations[0].evidence_event_ids == [1, 2]


