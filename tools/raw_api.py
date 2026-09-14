"""Raw / future-proof Google Ads MCP tools."""

from __future__ import annotations

from typing import Any

from app.google_ads_client import execute_gaql, search_google_ads_fields
from app import mutations as mutation_api
from app.services_registry import discover_services


def register(mcp) -> None:
    @mcp.tool()
    def google_ads_query(
        query: str,
        customer_id: str | None = None,
        page_size: int | None = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        """Execute an arbitrary GAQL query against Google Ads."""
        return execute_gaql(
            query, customer_id=customer_id, page_size=page_size, stream=stream
        )

    @mcp.tool()
    def google_ads_describe_fields(query: str) -> dict[str, Any]:
        """Search Google Ads API fields/resources via GoogleAdsFieldService."""
        return search_google_ads_fields(query)

    @mcp.tool()
    def google_ads_list_services() -> dict[str, Any]:
        """List installed Google Ads API services and callable methods (allowlist source)."""
        return {"success": True, "data": discover_services()}

    @mcp.tool()
    def google_ads_service_call(
        service_name: str,
        method_name: str,
        request: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
        validate_only: bool | None = None,
        partial_failure: bool | None = None,
        override_limits: bool = False,
    ) -> dict[str, Any]:
        """Invoke an allowlisted Google Ads service method with a structured request payload."""
        return mutation_api.google_ads_service_call(
            service_name,
            method_name,
            request,
            customer_id=customer_id,
            dry_run=dry_run,
            validate_only=validate_only,
            partial_failure=partial_failure,
            override_limits=override_limits,
        )

    @mcp.tool()
    def google_ads_mutate(
        service_name: str,
        operations: list[dict[str, Any]],
        customer_id: str | None = None,
        dry_run: bool = False,
        validate_only: bool | None = None,
        partial_failure: bool | None = None,
        override_limits: bool = False,
    ) -> dict[str, Any]:
        """Generic mutate wrapper for a Google Ads service."""
        return mutation_api.google_ads_mutate(
            service_name,
            operations,
            customer_id=customer_id,
            dry_run=dry_run,
            validate_only=validate_only,
            partial_failure=partial_failure,
            override_limits=override_limits,
        )

    @mcp.tool()
    def google_ads_batch_mutate(
        mutate_operations: list[dict[str, Any]],
        customer_id: str | None = None,
        dry_run: bool = False,
        validate_only: bool | None = None,
        partial_failure: bool | None = True,
        override_limits: bool = False,
    ) -> dict[str, Any]:
        """Wrap GoogleAdsService.Mutate for multi-resource atomic mutations."""
        return mutation_api.google_ads_multi_mutate(
            mutate_operations,
            customer_id=customer_id,
            dry_run=dry_run,
            validate_only=validate_only,
            partial_failure=partial_failure,
            override_limits=override_limits,
        )

    @mcp.tool()
    def google_ads_resource_mutate(
        resource_type: str,
        operation_type: str,
        payload: dict[str, Any],
        customer_id: str | None = None,
        update_mask: list[str] | None = None,
        dry_run: bool = False,
        validate_only: bool | None = None,
        partial_failure: bool | None = None,
        override_limits: bool = False,
    ) -> dict[str, Any]:
        """Generic resource mutate dispatcher (create/update/remove)."""
        return mutation_api.google_ads_resource_mutate(
            resource_type,
            operation_type,
            payload,
            customer_id=customer_id,
            update_mask=update_mask,
            dry_run=dry_run,
            validate_only=validate_only,
            partial_failure=partial_failure,
            override_limits=override_limits,
        )

    @mcp.tool()
    def google_ads_multi_mutate(
        mutate_operations: list[dict[str, Any]],
        customer_id: str | None = None,
        dry_run: bool = False,
        validate_only: bool | None = None,
        partial_failure: bool | None = True,
        override_limits: bool = False,
    ) -> dict[str, Any]:
        """Alias for GoogleAdsService.Mutate with temporary resource name support."""
        return mutation_api.google_ads_multi_mutate(
            mutate_operations,
            customer_id=customer_id,
            dry_run=dry_run,
            validate_only=validate_only,
            partial_failure=partial_failure,
            override_limits=override_limits,
        )
