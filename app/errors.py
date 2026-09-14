"""Google Ads API error formatting."""

from __future__ import annotations

from typing import Any

from google.ads.googleads.errors import GoogleAdsException
from google.api_core.exceptions import GoogleAPICallError


def _extract_google_ads_failure(exc: GoogleAdsException) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    failure = exc.failure
    if failure is None:
        return details
    for error in failure.errors:
        entry: dict[str, Any] = {
            "error_code": str(error.error_code),
            "message": error.message,
        }
        if error.location and error.location.field_path_elements:
            field_path = ".".join(
                element.field_name for element in error.location.field_path_elements
            )
            entry["field_path"] = field_path
        if error.trigger:
            entry["trigger"] = str(error.trigger)
        details.append(entry)
    return details


def _suggest_action(message: str, code: str) -> str | None:
    text = f"{message} {code}".lower()
    if "authentication" in text or "unauthorized" in text:
        return "Verify GOOGLE_SERVICE_ACCOUNT_JSON and that the service account has Standard access in Google Ads."
    if "customer not found" in text or "not enabled" in text:
        return "Confirm GOOGLE_ADS_CUSTOMER_ID and optional GOOGLE_ADS_LOGIN_CUSTOMER_ID (MCC) are correct."
    if "permission" in text or "authorization" in text:
        return "The service account may lack permission for this operation or customer."
    if "query" in text and "error" in text:
        return "Check GAQL syntax and field compatibility with the API version."
    if "quota" in text or "rate" in text:
        return "Reduce request frequency or wait before retrying."
    if "explorer" in text or "access level" in text:
        return "This operation may require higher Google Cloud API access than Explorer."
    if "policy" in text:
        return "Review Google Ads policy requirements for the affected resource."
    if "remove" in text and (
        "cannot" in text
        or "in use" in text
        or "depend" in text
        or "must" in text
        or "linked" in text
    ):
        return (
            "Google Ads blocked this removal — detach or remove dependent links first "
            "(for example campaign/shared-set links or asset links), then retry."
        )
    return None


def format_exception(
    exc: BaseException,
    *,
    customer_id: str | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "success": False,
        "error_type": type(exc).__name__,
        "message": str(exc),
        "customer_id": customer_id,
        "request_id": request_id,
        "errors": [],
        "suggested_action": None,
    }
    if isinstance(exc, GoogleAdsException):
        payload["request_id"] = exc.request_id or request_id
        payload["errors"] = _extract_google_ads_failure(exc)
        if payload["errors"]:
            first = payload["errors"][0]
            payload["suggested_action"] = _suggest_action(
                first.get("message", ""), first.get("error_code", "")
            )
        else:
            payload["suggested_action"] = _suggest_action(str(exc), "")
    elif isinstance(exc, GoogleAPICallError):
        payload["message"] = exc.message if hasattr(exc, "message") else str(exc)
        payload["suggested_action"] = _suggest_action(payload["message"], "")
    else:
        payload["suggested_action"] = _suggest_action(payload["message"], "")
    return payload


def success_payload(data: Any, **extra: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"success": True, "data": data}
    out.update(extra)
    return out
