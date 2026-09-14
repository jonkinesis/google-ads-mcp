"""Parse service-account credentials from environment variables."""

from __future__ import annotations

import json
import re
from typing import Any

from google.oauth2.service_account import Credentials

from app.config import Settings

_ADWORDS_SCOPE = ["https://www.googleapis.com/auth/adwords"]


def parse_service_account_json(raw: str) -> dict[str, Any]:
    """Parse GOOGLE_SERVICE_ACCOUNT_JSON, fixing escaped newlines in private_key."""
    if not raw or not raw.strip():
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON is empty.")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON.") from exc
    if not isinstance(data, dict):
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON must be a JSON object.")
    private_key = data.get("private_key")
    if isinstance(private_key, str):
        data["private_key"] = _normalize_private_key(private_key)
    return data


def _normalize_private_key(private_key: str) -> str:
    key = private_key.strip()
    if "\\n" in key:
        key = key.replace("\\n", "\n")
    if not key.startswith("-----BEGIN"):
        raise ValueError("Service account private_key is missing PEM headers.")
    return key


def build_google_ads_credentials(settings: Settings) -> Credentials:
    if not settings.google_service_account_json:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON is required.")
    info = parse_service_account_json(settings.google_service_account_json)
    required = {"type", "client_email", "private_key", "client_id", "token_uri"}
    missing = required - set(info.keys())
    if missing:
        raise ValueError(
            f"Service account JSON is missing required fields: {', '.join(sorted(missing))}"
        )
    if info.get("type") != "service_account":
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON must be a service account key.")
    return Credentials.from_service_account_info(info, scopes=_ADWORDS_SCOPE)


def redact_service_account_info(info: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(info)
    if "private_key" in redacted:
        redacted["private_key"] = "[REDACTED]"
    return redacted


def looks_like_secret(value: str) -> bool:
    if not value:
        return False
    if "BEGIN PRIVATE KEY" in value:
        return True
    if re.search(r'"private_key"\s*:', value):
        return True
    return False
