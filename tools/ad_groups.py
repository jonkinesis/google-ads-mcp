"""Ad group write tools."""
from __future__ import annotations
from typing import Any
from app import mutations as mutation_api
from app.google_ads_client import get_client_holder
from app.safety import check_bid_change

def _cid(customer_id: str | None) -> str:
    return get_client_holder().resolve_customer_id(customer_id)

def _rn(cid: str, ad_group_id: int) -> str:
    return f"customers/{cid}/adGroups/{ad_group_id}"

def register(mcp) -> None:
    @mcp.tool()
    def create_ad_group(campaign_id: int, name: str, cpc_bid_micros: int | None = None, status: str = "ENABLED", customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {"name": name, "campaign": f"customers/{cid}/campaigns/{campaign_id}", "status": status, "type": "SEARCH_STANDARD"}
        if cpc_bid_micros is not None:
            create["cpc_bid_micros"] = cpc_bid_micros
        return mutation_api.google_ads_mutate("AdGroupService", [{"create": create}], customer_id=cid, dry_run=dry_run)

    @mcp.tool()
    def update_ad_group(ad_group_id: int, updates: dict[str, Any], customer_id: str | None = None, dry_run: bool = False, override_limits: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        if "cpc_bid_micros" in updates:
            check = check_bid_change(None, updates["cpc_bid_micros"], override_limits)
            if not check.allowed:
                return {"success": False, "message": check.message}
        payload = {"resource_name": _rn(cid, ad_group_id), **updates}
        return mutation_api.google_ads_resource_mutate("AdGroup", "update", payload, customer_id=cid, update_mask=list(updates.keys()), dry_run=dry_run, override_limits=override_limits)

    @mcp.tool()
    def pause_ad_group(ad_group_id: int, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        return update_ad_group(ad_group_id, {"status": "PAUSED"}, customer_id=customer_id, dry_run=dry_run)

    @mcp.tool()
    def enable_ad_group(ad_group_id: int, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        return update_ad_group(ad_group_id, {"status": "ENABLED"}, customer_id=customer_id, dry_run=dry_run)

    @mcp.tool()
    def remove_ad_group(ad_group_id: int, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_resource_mutate("AdGroup", "remove", {"resource_name": _rn(cid, ad_group_id)}, customer_id=cid, dry_run=dry_run)

    @mcp.tool()
    def set_ad_group_bid(ad_group_id: int, cpc_bid_micros: int, customer_id: str | None = None, dry_run: bool = False, override_limits: bool = False) -> dict[str, Any]:
        return update_ad_group(ad_group_id, {"cpc_bid_micros": cpc_bid_micros}, customer_id=customer_id, dry_run=dry_run, override_limits=override_limits)
