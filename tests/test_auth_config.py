import json

import pytest

from app.auth import parse_service_account_json, build_google_ads_credentials
from app.config import Settings, normalize_customer_id, settings_for_tests


def test_parse_service_account_json_unescapes_private_key():
    raw = json.dumps(
        {
            "type": "service_account",
            "project_id": "demo",
            "private_key_id": "1",
            "private_key": "-----BEGIN PRIVATE KEY-----\\nLINE\\n-----END PRIVATE KEY-----\\n",
            "client_email": "svc@demo.iam.gserviceaccount.com",
            "client_id": "123",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    )
    data = parse_service_account_json(raw)
    assert "\n" in data["private_key"]
    assert "\\n" not in data["private_key"]


def test_normalize_customer_id_strips_hyphens():
    assert normalize_customer_id("123-456-7890") == "1234567890"


def test_settings_from_env():
    settings = settings_for_tests({"MAX_BUDGET_CHANGE_PERCENT": "15"})
    assert settings.google_ads_customer_id == "1234567890"
    assert settings.max_budget_change_percent == 15.0


def test_build_credentials_from_settings(monkeypatch):
    settings = settings_for_tests()
    monkeypatch.setattr(
        "google.oauth2.service_account.Credentials.from_service_account_info",
        lambda info, scopes: object(),
    )
    creds = build_google_ads_credentials(settings)
    assert creds is not None
