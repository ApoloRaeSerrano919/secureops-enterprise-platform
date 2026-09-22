from types import SimpleNamespace
from src.incidents.correlation import _risk

def event(severity, event_type):
    return SimpleNamespace(severity=severity, event_type=event_type)

def test_risk_increases_with_related_events():
    low = _risk([event("medium","failed_login")])
    high = _risk([
        event("high","failed_login"),
        event("high","successful_login_new_region"),
        event("critical","dangerous_tool_request"),
    ])
    assert high > low
