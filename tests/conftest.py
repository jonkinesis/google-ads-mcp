import os

import pytest

from app.config import get_settings


@pytest.fixture(autouse=True)
def _test_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_ADS_CUSTOMER_ID", "1234567890")
    monkeypatch.setenv("MCP_API_KEY", "test-key")
    monkeypatch.setenv("MAX_BUDGET_CHANGE_PERCENT", "15")
    monkeypatch.setenv("MAX_BID_CHANGE_PERCENT", "15")
    monkeypatch.setenv(
        "GOOGLE_SERVICE_ACCOUNT_JSON",
        '{"type":"service_account","project_id":"p","private_key_id":"k","private_key":"-----BEGIN PRIVATE KEY-----\\nabc\\n-----END PRIVATE KEY-----\\n","client_email":"a@p.iam.gserviceaccount.com","client_id":"1","token_uri":"https://oauth2.googleapis.com/token"}',
    )
    get_settings.cache_clear()
