"""Generic Google Ads mutation helpers."""

from __future__ import annotations

from typing import Any

from google.ads.googleads.errors import GoogleAdsException

from app.audit import audit_log
from app.errors import format_exception, success_payload
from app.google_ads_client import get_client_holder, mutate_response_to_dict
from app.proto_utils import message_to_dict, parse_dict_to_message
from app.removals import enrich_removal_result, extract_remove_resource_names
from app.safety import raw_mutation_limit_warning, remove_operation_summary
from app.services_registry import (
    build_operation_message_name,
    discover_mutate_methods,
    resource_type_to_service,
    validate_service_call,
)


def _apply_validate_only(request: Any, dry_run: bool, validate_only: bool | None) -> None:
    flag = validate_only if validate_only is not None else dry_run
    if hasattr(request, "validate_only"):
        request.validate_only = flag


def _apply_partial_failure(request: Any, partial_failure: bool | None) -> None:
    if partial_failure is None:
        return
    if hasattr(request, "partial_failure"):
        request.partial_failure = partial_failure


def google_ads_service_call(
    service_name: str,
    method_name: str,
    request: dict[str, Any],
    *,
    customer_id: str | None = None,
    dry_run: bool = False,
    validate_only: bool | None = None,
    partial_failure: bool | None = None,
    tool_name: str = "google_ads_service_call",
    override_limits: bool = False,
) -> dict[str, Any]:
    holder = get_client_holder()
    cid = holder.resolve_customer_id(customer_id)
    validate_service_call(service_name, method_name)
    client = holder.get_client()
    service = client.get_service(service_name)
    method = getattr(service, method_name)
    message = _build_request_message(client, service_name, method_name)
    payload = dict(request)
    payload.setdefault("customer_id", cid)
    parse_dict_to_message(message, payload)
    _apply_validate_only(message, dry_run, validate_only)
    _apply_partial_failure(message, partial_failure)
    warning = raw_mutation_limit_warning(override_limits)
    removal_targets = extract_remove_resource_names(payload.get("operations", []))
    if not removal_targets:
        removal_targets = extract_remove_resource_names(
            payload.get("mutate_operations", [])
        )
    try:
        response = method(request=message)
        result = success_payload(
            mutate_response_to_dict(response),
            customer_id=cid,
            service=service_name,
            method=method_name,
            dry_run=dry_run or bool(getattr(message, "validate_only", False)),
            request_id=getattr(response, "request_id", None),
        )
        if warning:
            result["limit_warning"] = warning
        result = enrich_removal_result(
            result,
            customer_id=cid,
            resource_names=removal_targets,
            dry_run=dry_run,
        )
        audit_log(
            tool_name=tool_name,
            customer_id=cid,
            action=f"{service_name}.{method_name}",
            resource_names=removal_targets or None,
            dry_run=result["dry_run"],
            success=True,
            request_id=result.get("request_id"),
        )
        return result
    except GoogleAdsException as exc:
        audit_log(
            tool_name=tool_name,
            customer_id=cid,
            action=f"{service_name}.{method_name}",
            resource_names=removal_targets or None,
            dry_run=dry_run,
            success=False,
            request_id=exc.request_id,
        )
        out = format_exception(exc, customer_id=cid, request_id=exc.request_id)
        if warning:
            out["limit_warning"] = warning
        out = enrich_removal_result(
            out,
            customer_id=cid,
            resource_names=removal_targets,
            dry_run=dry_run,
        )
        return out
    except Exception as exc:  # noqa: BLE001
        audit_log(
            tool_name=tool_name,
            customer_id=cid,
            action=f"{service_name}.{method_name}",
            resource_names=removal_targets or None,
            dry_run=dry_run,
            success=False,
        )
        return format_exception(exc, customer_id=cid)


def _build_request_message(client: Any, service_name: str, method_name: str) -> Any:
    last_error: Exception | None = None
    for request_type_name in _request_type_candidates(service_name, method_name):
        try:
            return client.get_type(request_type_name)
        except (ValueError, AttributeError) as exc:
            last_error = exc
    raise ValueError(
        f"Could not resolve request type for {service_name}.{method_name}: {last_error}"
    )


def _request_type_candidates(service_name: str, method_name: str) -> list[str]:
    primary = _infer_request_type(service_name, method_name)
    candidates = [primary]
    if not primary.endswith("Request"):
        candidates.append(f"{primary}Request")
    return candidates


def _infer_request_type(service_name: str, method_name: str) -> str:
    # mutate_campaigns -> MutateCampaignsRequest ; search -> SearchXRequest patterns
    parts = method_name.split("_")
    if parts[0] == "mutate":
        suffix = "".join(p.capitalize() for p in parts[1:])
        return f"Mutate{suffix}Request"
    if parts[0] in {"search", "list", "get", "apply", "promote", "end", "schedule"}:
        suffix = "".join(p.capitalize() for p in parts)
        return f"{suffix[0].upper()}{suffix[1:]}Request"
    suffix = "".join(p.capitalize() for p in parts)
    return f"{suffix}Request"


def google_ads_resource_mutate(
    resource_type: str,
    operation_type: str,
    payload: dict[str, Any],
    *,
    customer_id: str | None = None,
    update_mask: list[str] | None = None,
    dry_run: bool = False,
    validate_only: bool | None = None,
    partial_failure: bool | None = None,
    override_limits: bool = False,
) -> dict[str, Any]:
    holder = get_client_holder()
    cid = holder.resolve_customer_id(customer_id)
    service_name = resource_type_to_service(resource_type)
    mutate_methods = discover_mutate_methods()
    if service_name not in mutate_methods:
        return format_exception(
            ValueError(f"No mutate method discovered for {service_name}."),
            customer_id=cid,
        )
    method_name = mutate_methods[service_name]
    op_type = operation_type.lower()
    op_payload: dict[str, Any] = {}
    if op_type == "create":
        op_payload["create"] = payload
    elif op_type == "update":
        if update_mask:
            op_payload["update_mask"] = ",".join(update_mask)
        op_payload["update"] = payload
    elif op_type == "remove":
        resource_name = payload.get("resource_name") or payload.get("resourceName")
        if not resource_name:
            return format_exception(
                ValueError("remove operations require resource_name in payload."),
                customer_id=cid,
            )
        op_payload["remove"] = resource_name
    else:
        return format_exception(
            ValueError("operation_type must be create, update, or remove."),
            customer_id=cid,
        )
    request_key = _operations_field_name(method_name)
    request = {
        "customer_id": cid,
        request_key: [op_payload],
    }
    remove_summary = None
    if op_type == "remove":
        remove_summary = remove_operation_summary(
            op_payload["remove"], cid, resource_type
        )
    result = google_ads_service_call(
        service_name,
        method_name,
        request,
        customer_id=cid,
        dry_run=dry_run,
        validate_only=validate_only,
        partial_failure=partial_failure,
        tool_name="google_ads_resource_mutate",
        override_limits=override_limits,
    )
    if remove_summary:
        result["remove_summary"] = remove_summary
    return result


def _operations_field_name(mutate_method: str) -> str:
    # mutate_campaigns -> operations ; mutate_ad_group_ads -> operations
    return "operations"


def google_ads_mutate(
    service_name: str,
    operations: list[dict[str, Any]],
    *,
    customer_id: str | None = None,
    dry_run: bool = False,
    validate_only: bool | None = None,
    partial_failure: bool | None = None,
    override_limits: bool = False,
) -> dict[str, Any]:
    mutate_methods = discover_mutate_methods()
    if service_name not in mutate_methods:
        return format_exception(ValueError(f"Service {service_name} does not support mutate."))
    method_name = mutate_methods[service_name]
    request_key = _operations_field_name(method_name)
    holder = get_client_holder()
    cid = holder.resolve_customer_id(customer_id)
    request = {"customer_id": cid, request_key: operations}
    return google_ads_service_call(
        service_name,
        method_name,
        request,
        customer_id=cid,
        dry_run=dry_run,
        validate_only=validate_only,
        partial_failure=partial_failure,
        tool_name="google_ads_mutate",
        override_limits=override_limits,
    )


def google_ads_multi_mutate(
    mutate_operations: list[dict[str, Any]],
    *,
    customer_id: str | None = None,
    dry_run: bool = False,
    validate_only: bool | None = None,
    partial_failure: bool | None = True,
    override_limits: bool = False,
) -> dict[str, Any]:
    request = {
        "mutate_operations": mutate_operations,
    }
    return google_ads_service_call(
        "GoogleAdsService",
        "mutate",
        request,
        customer_id=customer_id,
        dry_run=dry_run,
        validate_only=validate_only,
        partial_failure=partial_failure,
        tool_name="google_ads_multi_mutate",
        override_limits=override_limits,
    )
