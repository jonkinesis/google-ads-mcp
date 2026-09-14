"""Performance Max write tools."""

from __future__ import annotations

from typing import Any

from app import mutations as mutation_api
from app.google_ads_client import get_client_holder


def _cid(customer_id: str | None) -> str:
    return get_client_holder().resolve_customer_id(customer_id)


def register(mcp) -> None:
    @mcp.tool()
    def create_performance_max_campaign(
        name: str,
        budget_resource_name: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {
            "name": name,
            "campaign_budget": budget_resource_name,
            "advertising_channel_type": "PERFORMANCE_MAX",
            "status": "PAUSED",
        }
        return mutation_api.google_ads_mutate(
            "CampaignService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def create_asset_group(
        campaign_id: int,
        name: str,
        final_urls: list[str],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {
            "campaign": f"customers/{cid}/campaigns/{campaign_id}",
            "name": name,
            "final_urls": final_urls,
            "status": "ENABLED",
        }
        return mutation_api.google_ads_mutate(
            "AssetGroupService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def update_asset_group(
        asset_group_id: int,
        updates: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        payload = {
            "resource_name": f"customers/{cid}/assetGroups/{asset_group_id}",
            **updates,
        }
        return mutation_api.google_ads_resource_mutate(
            "AssetGroup",
            "update",
            payload,
            customer_id=cid,
            update_mask=list(updates.keys()),
            dry_run=dry_run,
        )

    @mcp.tool()
    def attach_assets_to_asset_group(
        asset_group_id: int,
        asset_resource_name: str,
        field_type: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {
            "asset_group": f"customers/{cid}/assetGroups/{asset_group_id}",
            "asset": asset_resource_name,
            "field_type": field_type,
        }
        return mutation_api.google_ads_mutate(
            "AssetGroupAssetService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def add_asset_group_signal(
        asset_group_id: int,
        signal: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {"asset_group": f"customers/{cid}/assetGroups/{asset_group_id}", **signal}
        return mutation_api.google_ads_mutate(
            "AssetGroupSignalService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )
