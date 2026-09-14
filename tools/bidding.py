"""Bidding strategy write tools."""

from __future__ import annotations

from typing import Any

from app import mutations as mutation_api
from app.google_ads_client import get_client_holder


def _cid(customer_id: str | None) -> str:
    return get_client_holder().resolve_customer_id(customer_id)


def _update_campaign_bidding(
    campaign_id: int,
    bidding: dict[str, Any],
    customer_id: str | None,
    dry_run: bool,
) -> dict[str, Any]:
    cid = _cid(customer_id)
    payload = {"resource_name": f"customers/{cid}/campaigns/{campaign_id}", **bidding}
    return mutation_api.google_ads_resource_mutate(
        "Campaign",
        "update",
        payload,
        customer_id=cid,
        update_mask=list(bidding.keys()),
        dry_run=dry_run,
    )


def register(mcp) -> None:
    @mcp.tool()
    def set_manual_cpc(
        campaign_id: int, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        return _update_campaign_bidding(
            campaign_id, {"manual_cpc": {}}, customer_id, dry_run
        )

    @mcp.tool()
    def set_maximize_clicks(
        campaign_id: int, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        return _update_campaign_bidding(
            campaign_id, {"maximize_clicks": {}}, customer_id, dry_run
        )

    @mcp.tool()
    def set_maximize_conversions(
        campaign_id: int, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        return _update_campaign_bidding(
            campaign_id, {"maximize_conversions": {}}, customer_id, dry_run
        )

    @mcp.tool()
    def set_maximize_conversion_value(
        campaign_id: int, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        return _update_campaign_bidding(
            campaign_id, {"maximize_conversion_value": {}}, customer_id, dry_run
        )

    @mcp.tool()
    def set_target_cpa(
        campaign_id: int,
        target_cpa_micros: int,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return _update_campaign_bidding(
            campaign_id,
            {"target_cpa": {"target_cpa_micros": target_cpa_micros}},
            customer_id,
            dry_run,
        )

    @mcp.tool()
    def set_target_roas(
        campaign_id: int,
        target_roas: float,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return _update_campaign_bidding(
            campaign_id, {"target_roas": {"target_roas": target_roas}}, customer_id, dry_run
        )

    @mcp.tool()
    def update_target_cpa(
        campaign_id: int,
        target_cpa_micros: int,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return set_target_cpa(campaign_id, target_cpa_micros, customer_id, dry_run)

    @mcp.tool()
    def update_target_roas(
        campaign_id: int,
        target_roas: float,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return set_target_roas(campaign_id, target_roas, customer_id, dry_run)

    @mcp.tool()
    def set_campaign_bid_strategy(
        campaign_id: int,
        bidding: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return _update_campaign_bidding(campaign_id, bidding, customer_id, dry_run)

    @mcp.tool()
    def create_portfolio_bidding_strategy(
        name: str,
        strategy: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {"name": name, **strategy}
        return mutation_api.google_ads_mutate(
            "BiddingStrategyService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def update_portfolio_bidding_strategy(
        bidding_strategy_id: int,
        updates: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        payload = {
            "resource_name": f"customers/{cid}/biddingStrategies/{bidding_strategy_id}",
            **updates,
        }
        return mutation_api.google_ads_resource_mutate(
            "BiddingStrategy",
            "update",
            payload,
            customer_id=cid,
            update_mask=list(updates.keys()),
            dry_run=dry_run,
        )

    @mcp.tool()
    def create_data_exclusion(
        payload: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_mutate(
            "BiddingDataExclusionService",
            [{"create": payload}],
            customer_id=cid,
            dry_run=dry_run,
        )

    @mcp.tool()
    def remove_data_exclusion(
        resource_name: str, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_resource_mutate(
            "BiddingDataExclusion",
            "remove",
            {"resource_name": resource_name},
            customer_id=cid,
            dry_run=dry_run,
        )

    @mcp.tool()
    def create_seasonality_adjustment(
        payload: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_mutate(
            "BiddingSeasonalityAdjustmentService",
            [{"create": payload}],
            customer_id=cid,
            dry_run=dry_run,
        )

    @mcp.tool()
    def remove_seasonality_adjustment(
        resource_name: str, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_resource_mutate(
            "BiddingSeasonalityAdjustment",
            "remove",
            {"resource_name": resource_name},
            customer_id=cid,
            dry_run=dry_run,
        )
