"""Environment configuration for the Google Ads MCP server."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

_CUSTOMER_ID_RE = re.compile(r"^\d{10}$")


def normalize_customer_id(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip().replace("-", "")
    if not _CUSTOMER_ID_RE.fullmatch(cleaned):
        raise ValueError(
            "Customer ID must be exactly 10 digits (hyphens are stripped automatically)."
        )
    return cleaned


def _normalize_mcp_tool_mode(raw: str | None) -> str:
    mode = (raw or "compact").strip().lower()
    if mode not in {"compact", "full"}:
        raise ValueError("MCP_TOOL_MODE must be 'compact' or 'full'.")
    return mode


def parse_optional_float(name: str, raw: str | None) -> float | None:
    if raw is None or raw.strip() == "":
        return None
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc


@dataclass(frozen=True)
class Settings:
    google_ads_customer_id: str | None
    google_ads_login_customer_id: str | None
    google_service_account_json: str | None
    mcp_api_key: str | None
    max_budget_change_percent: float | None
    max_bid_change_percent: float | None
    mcp_tool_mode: str
    port: int

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> Settings:
        env = environ if environ is not None else os.environ
        customer_raw = env.get("GOOGLE_ADS_CUSTOMER_ID")
        login_raw = env.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
        customer_id = normalize_customer_id(customer_raw) if customer_raw else None
        login_customer_id = normalize_customer_id(login_raw) if login_raw else None
        port_raw = env.get("PORT", "8000")
        try:
            port = int(port_raw)
        except ValueError as exc:
            raise ValueError("PORT must be an integer") from exc
        return cls(
            google_ads_customer_id=customer_id,
            google_ads_login_customer_id=login_customer_id,
            google_service_account_json=env.get("GOOGLE_SERVICE_ACCOUNT_JSON"),
            mcp_api_key=env.get("MCP_API_KEY"),
            max_budget_change_percent=parse_optional_float(
                "MAX_BUDGET_CHANGE_PERCENT", env.get("MAX_BUDGET_CHANGE_PERCENT")
            ),
            max_bid_change_percent=parse_optional_float(
                "MAX_BID_CHANGE_PERCENT", env.get("MAX_BID_CHANGE_PERCENT")
            ),
            mcp_tool_mode=_normalize_mcp_tool_mode(env.get("MCP_TOOL_MODE")),
            port=port,
        )

    def require_mcp_api_key(self) -> str:
        if not self.mcp_api_key:
            raise ValueError("MCP_API_KEY is required for remote MCP access.")
        return self.mcp_api_key

    def require_google_ads_config(self) -> None:
        if not self.google_service_account_json:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON is required.")
        if not self.google_ads_customer_id:
            raise ValueError("GOOGLE_ADS_CUSTOMER_ID is required.")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()


def settings_for_tests(overrides: dict[str, Any] | None = None) -> Settings:
    base = {
        "GOOGLE_ADS_CUSTOMER_ID": "1234567890",
        "GOOGLE_SERVICE_ACCOUNT_JSON": '{"type":"service_account","project_id":"p","private_key_id":"k","private_key":"-----BEGIN PRIVATE KEY-----\\nabc\\n-----END PRIVATE KEY-----\\n","client_email":"a@p.iam.gserviceaccount.com","client_id":"1","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/a","universe_domain":"googleapis.com"}',
        "MCP_API_KEY": "test-key",
        "PORT": "8000",
    }
    if overrides:
        base.update({k: str(v) for k, v in overrides.items()})
    return Settings.from_env(base)
