from src.tools.registry import get_service_health


def test_service_health_simulated_when_base_empty(monkeypatch):
    from src.config import settings as settings_mod

    monkeypatch.setattr(settings_mod.settings, "service_health_base_url", "")
    result = get_service_health({"service": "payments-api"})
    assert result["mode"] == "simulated"
    assert result["service"] == "payments-api"
    assert result["status"] == "healthy"
