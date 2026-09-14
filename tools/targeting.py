"""Targeting write tools."""

from __future__ import annotations

from typing import Any

from app import mutations as mutation_api
from app.google_ads_client import get_client_holder


def _cid(customer_id: str | None) -> str:
    return get_client_holder().resolve_customer_id(customer_id)


def register(mcp) -> None:
    @mcp.tool()
    def add_location_target(
        campaign_id: int,
        geo_target_constant: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {
            "campaign": f"customers/{cid}/campaigns/{campaign_id}",
            "location": {"geo_target_constant": geo_target_constant},
        }
        return mutation_api.google_ads_mutate(
            "CampaignCriterionService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def remove_location_target(
        campaign_id: int, criterion_id: int, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_resource_mutate(
            "CampaignCriterion",
            "remove",
            {"resource_name": f"customers/{cid}/campaignCriteria/{campaign_id}~{criterion_id}"},
            customer_id=cid,
            dry_run=dry_run,
        )

    @mcp.tool()
    def add_location_exclusion(
        campaign_id: int,
        geo_target_constant: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {
            "campaign": f"customers/{cid}/campaigns/{campaign_id}",
            "negative": True,
            "location": {"geo_target_constant": geo_target_constant},
        }
        return mutation_api.google_ads_mutate(
            "CampaignCriterionService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def set_language_targeting(
        campaign_id: int,
        language_constant: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {
            "campaign": f"customers/{cid}/campaigns/{campaign_id}",
            "language": {"language_constant": language_constant},
        }
        return mutation_api.google_ads_mutate(
            "CampaignCriterionService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def add_device_bid_modifier(
        campaign_id: int,
        device_type: str,
        bid_modifier: float,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return set_device_bid_modifier(
            campaign_id, device_type, bid_modifier, customer_id, dry_run
        )

    @mcp.tool()
    def set_device_bid_modifier(
        campaign_id: int,
        device_type: str,
        bid_modifier: float,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {
            "campaign": f"customers/{cid}/campaigns/{campaign_id}",
            "device": {"type": device_type},
            "bid_modifier": bid_modifier,
        }
        return mutation_api.google_ads_mutate(
            "CampaignCriterionService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def add_audience_target(
        campaign_id: int,
        audience: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {
            "campaign": f"customers/{cid}/campaigns/{campaign_id}",
            "audience": {"audience": audience},
        }
        return mutation_api.google_ads_mutate(
            "CampaignCriterionService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def remove_audience_target(
        campaign_id: int, criterion_id: int, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_resource_mutate(
            "CampaignCriterion",
            "remove",
            {"resource_name": f"customers/{cid}/campaignCriteria/{campaign_id}~{criterion_id}"},
            customer_id=cid,
            dry_run=dry_run,
        )

    @mcp.tool()
    def add_demographic_target(
        campaign_id: int,
        demographic: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {"campaign": f"customers/{cid}/campaigns/{campaign_id}", **demographic}
        return mutation_api.google_ads_mutate(
            "CampaignCriterionService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def update_schedule_targeting(
        campaign_id: int,
        ad_schedule: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return add_ad_schedule(campaign_id, ad_schedule, customer_id, dry_run)

    @mcp.tool()
    def add_ad_schedule(
        campaign_id: int,
        ad_schedule: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {
            "campaign": f"customers/{cid}/campaigns/{campaign_id}",
            "ad_schedule": ad_schedule,
        }
        return mutation_api.google_ads_mutate(
            "CampaignCriterionService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def remove_ad_schedule(
        campaign_id: int, criterion_id: int, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_resource_mutate(
            "CampaignCriterion",
            "remove",
            {"resource_name": f"customers/{cid}/campaignCriteria/{campaign_id}~{criterion_id}"},
            customer_id=cid,
            dry_run=dry_run,
        )

    @mcp.tool()
    def remove_location_exclusion(
        campaign_id: int, criterion_id: int, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        """Remove a location exclusion criterion from a campaign."""
        return remove_location_target(
            campaign_id, criterion_id, customer_id=customer_id, dry_run=dry_run
        )
