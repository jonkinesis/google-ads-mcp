"""Campaign write tools."""
from __future__ import annotations
from typing import Any
from app import mutations as mutation_api
from app.campaign_dates import normalize_campaign_date_time
from app.google_ads_client import get_client_holder

def _cid(customer_id: str | None) -> str:
    return get_client_holder().resolve_customer_id(customer_id)

def _campaign_rn(customer_id: str, campaign_id: int) -> str:
    return f"customers/{customer_id}/campaigns/{campaign_id}"

def register(mcp) -> None:
    @mcp.tool()
    def create_campaign(name: str, budget_resource_name: str, advertising_channel_type: str = "SEARCH", status: str = "PAUSED", customer_id: str | None = None, dry_run: bool = False, override_limits: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        op = {"create": {"name": name, "campaign_budget": budget_resource_name, "advertising_channel_type": advertising_channel_type, "status": status}}
        return mutation_api.google_ads_mutate("CampaignService", [op], customer_id=cid, dry_run=dry_run, override_limits=override_limits)

    @mcp.tool()
    def update_campaign(campaign_id: int, updates: dict[str, Any], customer_id: str | None = None, dry_run: bool = False, override_limits: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        payload = {"resource_name": _campaign_rn(cid, campaign_id), **updates}
        mask = list(updates.keys())
        return mutation_api.google_ads_resource_mutate("Campaign", "update", payload, customer_id=cid, update_mask=mask, dry_run=dry_run, override_limits=override_limits)

    @mcp.tool()
    def pause_campaign(campaign_id: int, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        return update_campaign(campaign_id, {"status": "PAUSED"}, customer_id=customer_id, dry_run=dry_run)

    @mcp.tool()
    def enable_campaign(campaign_id: int, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        return update_campaign(campaign_id, {"status": "ENABLED"}, customer_id=customer_id, dry_run=dry_run)

    @mcp.tool()
    def remove_campaign(campaign_id: int, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        rn = _campaign_rn(cid, campaign_id)
        return mutation_api.google_ads_resource_mutate("Campaign", "remove", {"resource_name": rn}, customer_id=cid, dry_run=dry_run)

    @mcp.tool()
    def set_campaign_dates(campaign_id: int, start_date: str | None = None, end_date: str | None = None, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        updates = {}
        if start_date:
            updates["start_date_time"] = normalize_campaign_date_time(start_date, end=False)
        if end_date:
            updates["end_date_time"] = normalize_campaign_date_time(end_date, end=True)
        return update_campaign(campaign_id, updates, customer_id=customer_id, dry_run=dry_run)

    @mcp.tool()
    def update_campaign_name(campaign_id: int, name: str, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        return update_campaign(campaign_id, {"name": name}, customer_id=customer_id, dry_run=dry_run)

    @mcp.tool()
    def update_campaign_network_settings(campaign_id: int, network_settings: dict[str, Any], customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        return update_campaign(campaign_id, {"network_settings": network_settings}, customer_id=customer_id, dry_run=dry_run)
