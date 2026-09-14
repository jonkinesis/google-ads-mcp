"""Budget write tools."""
from __future__ import annotations
from typing import Any
from app import mutations as mutation_api
from app.google_ads_client import get_client_holder
from app.safety import check_budget_change

def _cid(customer_id: str | None) -> str:
    return get_client_holder().resolve_customer_id(customer_id)

def register(mcp) -> None:
    @mcp.tool()
    def create_campaign_budget(name: str, amount_micros: int, delivery_method: str = "STANDARD", customer_id: str | None = None, dry_run: bool = False, override_limits: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        op = {"create": {"name": name, "amount_micros": amount_micros, "delivery_method": delivery_method}}
        return mutation_api.google_ads_mutate("CampaignBudgetService", [op], customer_id=cid, dry_run=dry_run, override_limits=override_limits)

    @mcp.tool()
    def update_campaign_budget(budget_id: int, updates: dict[str, Any], customer_id: str | None = None, dry_run: bool = False, override_limits: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        payload = {"resource_name": f"customers/{cid}/campaignBudgets/{budget_id}", **updates}
        if "amount_micros" in updates:
            check = check_budget_change(None, updates["amount_micros"], override_limits)
            if not check.allowed:
                return {"success": False, "message": check.message}
        return mutation_api.google_ads_resource_mutate("CampaignBudget", "update", payload, customer_id=cid, update_mask=list(updates.keys()), dry_run=dry_run, override_limits=override_limits)

    @mcp.tool()
    def set_campaign_daily_budget(budget_id: int, amount_micros: int, customer_id: str | None = None, dry_run: bool = False, override_limits: bool = False) -> dict[str, Any]:
        return update_campaign_budget(budget_id, {"amount_micros": amount_micros}, customer_id=customer_id, dry_run=dry_run, override_limits=override_limits)

    @mcp.tool()
    def set_campaign_shared_budget(campaign_id: int, budget_resource_name: str, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        payload = {"resource_name": f"customers/{cid}/campaigns/{campaign_id}", "campaign_budget": budget_resource_name}
        return mutation_api.google_ads_resource_mutate(
            "Campaign",
            "update",
            payload,
            customer_id=cid,
            update_mask=["campaign_budget"],
            dry_run=dry_run,
        )
