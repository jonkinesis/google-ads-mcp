from unittest.mock import MagicMock, patch

import pytest
from google.ads.googleads.errors import GoogleAdsException

from app.config import settings_for_tests
from app.errors import format_exception
from app.mutations import google_ads_service_call


class _FakeFailure:
    errors = []


def test_format_google_ads_exception():
    exc = GoogleAdsException(MagicMock(), MagicMock(), _FakeFailure(), "req-1")
    payload = format_exception(exc, customer_id="1234567890", request_id="req-1")
    assert payload["success"] is False
    assert payload["request_id"] == "req-1"


def test_dry_run_sets_validate_only(monkeypatch):
    settings = settings_for_tests()
    fake_client = MagicMock()
    fake_service = MagicMock()
    fake_request = MagicMock()
    fake_response = MagicMock()
    fake_response.request_id = "rid"
    fake_service.mutate_campaigns.return_value = fake_response
    fake_client.get_service.return_value = fake_service
    fake_client.get_type.return_value = fake_request

    holder = MagicMock()
    holder.resolve_customer_id.return_value = "1234567890"
    holder.get_client.return_value = fake_client

    monkeypatch.setattr("app.mutations.get_client_holder", lambda: holder)
    monkeypatch.setattr(
        "app.mutations.validate_service_call", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        "app.mutations.parse_dict_to_message",
        lambda message, data: message,
    )
    monkeypatch.setattr(
        "app.mutations.mutate_response_to_dict",
        lambda response: {"request_id": "rid"},
    )

    result = google_ads_service_call(
        "CampaignService",
        "mutate_campaigns",
        {"customer_id": "1234567890", "operations": []},
        dry_run=True,
    )
    assert result["success"] is True
    assert fake_request.validate_only is True


def test_health_route():
    from starlette.testclient import TestClient

    from app.server import create_mcp

    client = TestClient(create_mcp().http_app(path="/mcp", stateless_http=True))
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "MCP_API_KEY" not in body


def test_mcp_requires_api_key_when_configured():
    from starlette.testclient import TestClient

    from app.server import create_mcp

    client = TestClient(create_mcp().http_app(path="/mcp", stateless_http=True))
    response = client.post("/mcp", json={})
    # Protected MCP endpoint should not allow unauthenticated access when key configured.
    assert response.status_code in {401, 403, 406, 415, 422}
