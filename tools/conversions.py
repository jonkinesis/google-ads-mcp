"""Conversion write/upload tools."""

from __future__ import annotations

from typing import Any

from app import mutations as mutation_api
from app.google_ads_client import get_client_holder


def _cid(customer_id: str | None) -> str:
    return get_client_holder().resolve_customer_id(customer_id)


def register(mcp) -> None:
    @mcp.tool()
    def create_conversion_action(
        payload: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_mutate(
            "ConversionActionService", [{"create": payload}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def update_conversion_action(
        conversion_action_id: int,
        updates: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        payload = {
            "resource_name": f"customers/{cid}/conversionActions/{conversion_action_id}",
            **updates,
        }
        return mutation_api.google_ads_resource_mutate(
            "ConversionAction",
            "update",
            payload,
            customer_id=cid,
            update_mask=list(updates.keys()),
            dry_run=dry_run,
        )

    @mcp.tool()
    def set_conversion_action_status(
        conversion_action_id: int,
        status: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return update_conversion_action(
            conversion_action_id, {"status": status}, customer_id, dry_run
        )

    @mcp.tool()
    def upload_click_conversions(
        conversions: list[dict[str, Any]],
        customer_id: str | None = None,
        dry_run: bool = False,
        partial_failure: bool = True,
    ) -> dict[str, Any]:
        request = {"conversions": conversions, "partial_failure": partial_failure}
        return mutation_api.google_ads_service_call(
            "ConversionUploadService",
            "upload_click_conversions",
            request,
            customer_id=customer_id,
            dry_run=dry_run,
            partial_failure=partial_failure,
            tool_name="upload_click_conversions",
        )

    @mcp.tool()
    def upload_call_conversions(
        conversions: list[dict[str, Any]],
        customer_id: str | None = None,
        dry_run: bool = False,
        partial_failure: bool = True,
    ) -> dict[str, Any]:
        request = {"conversions": conversions, "partial_failure": partial_failure}
        return mutation_api.google_ads_service_call(
            "ConversionUploadService",
            "upload_call_conversions",
            request,
            customer_id=customer_id,
            dry_run=dry_run,
            partial_failure=partial_failure,
            tool_name="upload_call_conversions",
        )

    @mcp.tool()
    def upload_enhanced_conversions_if_supported(
        conversions: list[dict[str, Any]],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        request = {"conversions": conversions}
        return mutation_api.google_ads_service_call(
            "ConversionUploadService",
            "upload_click_conversions",
            request,
            customer_id=customer_id,
            dry_run=dry_run,
            tool_name="upload_enhanced_conversions_if_supported",
        )

    @mcp.tool()
    def upload_conversion_adjustments(
        adjustment: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return mutation_api.google_ads_service_call(
            "ConversionAdjustmentUploadService",
            "upload_conversion_adjustments",
            adjustment,
            customer_id=customer_id,
            dry_run=dry_run,
            tool_name="upload_conversion_adjustments",
        )
