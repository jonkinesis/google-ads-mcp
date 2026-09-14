"""Asset write tools."""

from __future__ import annotations

from typing import Any

from app import mutations as mutation_api
from app.google_ads_client import get_client_holder


def _cid(customer_id: str | None) -> str:
    return get_client_holder().resolve_customer_id(customer_id)


def register(mcp) -> None:
    @mcp.tool()
    def create_asset(
        asset_payload: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_mutate(
            "AssetService", [{"create": asset_payload}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def update_asset(
        asset_id: int,
        updates: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        payload = {"resource_name": f"customers/{cid}/assets/{asset_id}", **updates}
        return mutation_api.google_ads_resource_mutate(
            "Asset", "update", payload, customer_id=cid, update_mask=list(updates.keys()), dry_run=dry_run
        )

    @mcp.tool()
    def remove_asset(
        asset_id: int, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_resource_mutate(
            "Asset",
            "remove",
            {"resource_name": f"customers/{cid}/assets/{asset_id}"},
            customer_id=cid,
            dry_run=dry_run,
        )

    @mcp.tool()
    def attach_asset_to_campaign(
        campaign_id: int,
        asset_resource_name: str,
        field_type: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {
            "campaign": f"customers/{cid}/campaigns/{campaign_id}",
            "asset": asset_resource_name,
            "field_type": field_type,
        }
        return mutation_api.google_ads_mutate(
            "CampaignAssetService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def detach_asset_from_campaign(
        campaign_id: int,
        asset_resource_name: str,
        field_type: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        rn = f"customers/{cid}/campaignAssets/{campaign_id}~{asset_resource_name.split('/')[-1]}~{field_type}"
        return mutation_api.google_ads_resource_mutate(
            "CampaignAsset", "remove", {"resource_name": rn}, customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def attach_asset_to_ad_group(
        ad_group_id: int,
        asset_resource_name: str,
        field_type: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {
            "ad_group": f"customers/{cid}/adGroups/{ad_group_id}",
            "asset": asset_resource_name,
            "field_type": field_type,
        }
        return mutation_api.google_ads_mutate(
            "AdGroupAssetService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def detach_asset_from_ad_group(
        ad_group_id: int,
        asset_id: int,
        field_type: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        rn = f"customers/{cid}/adGroupAssets/{ad_group_id}~{asset_id}~{field_type}"
        return mutation_api.google_ads_resource_mutate(
            "AdGroupAsset", "remove", {"resource_name": rn}, customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def attach_asset_to_customer(
        asset_resource_name: str,
        field_type: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {"asset": asset_resource_name, "field_type": field_type}
        return mutation_api.google_ads_mutate(
            "CustomerAssetService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def detach_asset_from_customer(
        asset_id: int, field_type: str, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        rn = f"customers/{cid}/customerAssets/{asset_id}~{field_type}"
        return mutation_api.google_ads_resource_mutate(
            "CustomerAsset", "remove", {"resource_name": rn}, customer_id=cid, dry_run=dry_run
        )
