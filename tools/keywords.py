"""Keyword/criterion write tools."""
from __future__ import annotations
from typing import Any
from app import mutations as mutation_api
from app.google_ads_client import get_client_holder
from app.safety import check_bid_change

def _cid(customer_id: str | None) -> str:
    return get_client_holder().resolve_customer_id(customer_id)

def register(mcp) -> None:
    @mcp.tool()
    def add_keyword(ad_group_id: int, text: str, match_type: str = "EXACT", cpc_bid_micros: int | None = None, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {"ad_group": f"customers/{cid}/adGroups/{ad_group_id}", "status": "ENABLED", "keyword": {"text": text, "match_type": match_type}}
        if cpc_bid_micros is not None:
            create["cpc_bid_micros"] = cpc_bid_micros
        return mutation_api.google_ads_mutate("AdGroupCriterionService", [{"create": create}], customer_id=cid, dry_run=dry_run)

    @mcp.tool()
    def update_keyword_bid(ad_group_id: int, criterion_id: int, cpc_bid_micros: int, customer_id: str | None = None, dry_run: bool = False, override_limits: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        check = check_bid_change(None, cpc_bid_micros, override_limits)
        if not check.allowed:
            return {"success": False, "message": check.message}
        payload = {"resource_name": f"customers/{cid}/adGroupCriteria/{ad_group_id}~{criterion_id}", "cpc_bid_micros": cpc_bid_micros}
        return mutation_api.google_ads_resource_mutate("AdGroupCriterion", "update", payload, customer_id=cid, update_mask=["cpc_bid_micros"], dry_run=dry_run, override_limits=override_limits)

    @mcp.tool()
    def pause_keyword(ad_group_id: int, criterion_id: int, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        payload = {"resource_name": f"customers/{cid}/adGroupCriteria/{ad_group_id}~{criterion_id}", "status": "PAUSED"}
        return mutation_api.google_ads_resource_mutate("AdGroupCriterion", "update", payload, customer_id=cid, update_mask=["status"], dry_run=dry_run)

    @mcp.tool()
    def enable_keyword(ad_group_id: int, criterion_id: int, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        payload = {"resource_name": f"customers/{cid}/adGroupCriteria/{ad_group_id}~{criterion_id}", "status": "ENABLED"}
        return mutation_api.google_ads_resource_mutate("AdGroupCriterion", "update", payload, customer_id=cid, update_mask=["status"], dry_run=dry_run)

    @mcp.tool()
    def remove_keyword(ad_group_id: int, criterion_id: int, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_resource_mutate("AdGroupCriterion", "remove", {"resource_name": f"customers/{cid}/adGroupCriteria/{ad_group_id}~{criterion_id}"}, customer_id=cid, dry_run=dry_run)

    @mcp.tool()
    def add_negative_keyword(campaign_id: int, text: str, match_type: str = "EXACT", customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        return add_campaign_negative_keyword(campaign_id, text, match_type, customer_id, dry_run)

    @mcp.tool()
    def remove_negative_keyword(campaign_id: int, criterion_id: int, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_resource_mutate("CampaignCriterion", "remove", {"resource_name": f"customers/{cid}/campaignCriteria/{campaign_id}~{criterion_id}"}, customer_id=cid, dry_run=dry_run)

    @mcp.tool()
    def add_campaign_negative_keyword(campaign_id: int, text: str, match_type: str = "EXACT", customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {"campaign": f"customers/{cid}/campaigns/{campaign_id}", "negative": True, "keyword": {"text": text, "match_type": match_type}}
        return mutation_api.google_ads_mutate("CampaignCriterionService", [{"create": create}], customer_id=cid, dry_run=dry_run)

    @mcp.tool()
    def add_ad_group_negative_keyword(ad_group_id: int, text: str, match_type: str = "EXACT", customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {"ad_group": f"customers/{cid}/adGroups/{ad_group_id}", "negative": True, "keyword": {"text": text, "match_type": match_type}}
        return mutation_api.google_ads_mutate("AdGroupCriterionService", [{"create": create}], customer_id=cid, dry_run=dry_run)

    @mcp.tool()
    def create_negative_keyword_list(name: str, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        op = {"create": {"name": name, "type": "NEGATIVE_KEYWORDS"}}
        return mutation_api.google_ads_mutate("SharedSetService", [op], customer_id=cid, dry_run=dry_run)

    @mcp.tool()
    def add_keyword_to_negative_list(shared_set_id: int, text: str, match_type: str = "EXACT", customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {"shared_set": f"customers/{cid}/sharedSets/{shared_set_id}", "keyword": {"text": text, "match_type": match_type}}
        return mutation_api.google_ads_mutate("SharedCriterionService", [{"create": create}], customer_id=cid, dry_run=dry_run)

    @mcp.tool()
    def remove_keyword_from_negative_list(shared_set_id: int, criterion_id: int, customer_id: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_resource_mutate("SharedCriterion", "remove", {"resource_name": f"customers/{cid}/sharedCriteria/{shared_set_id}~{criterion_id}"}, customer_id=cid, dry_run=dry_run)

    @mcp.tool()
    def remove_shared_criterion(
        shared_set_id: int,
        criterion_id: int,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Remove a criterion from a shared set (negative keyword list)."""
        return remove_keyword_from_negative_list(
            shared_set_id, criterion_id, customer_id=customer_id, dry_run=dry_run
        )

    @mcp.tool()
    def remove_shared_set(
        shared_set_id: int,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Remove a shared set. Google Ads may require linked campaigns to be detached first."""
        cid = _cid(customer_id)
        return mutation_api.google_ads_resource_mutate(
            "SharedSet",
            "remove",
            {"resource_name": f"customers/{cid}/sharedSets/{shared_set_id}"},
            customer_id=cid,
            dry_run=dry_run,
        )
