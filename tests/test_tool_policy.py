from src.tools.policy import evaluate_tool_policy

def test_analyst_cannot_revoke_session():
    result = evaluate_tool_policy("analyst", "revoke_session")
    assert result["allowed"] is False

def test_responder_can_request_revoke():
    result = evaluate_tool_policy("responder", "revoke_session")
    assert result["allowed"] is True
    assert result["requires_approval"] is True

def test_only_admin_can_isolate_service():
    assert evaluate_tool_policy("responder", "isolate_service")["allowed"] is False
    assert evaluate_tool_policy("admin", "isolate_service")["allowed"] is True
