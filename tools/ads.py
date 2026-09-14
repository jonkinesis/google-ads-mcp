"""Ad write tools."""

from __future__ import annotations

from typing import Any

from app import mutations as mutation_api
from app.google_ads_client import get_client_holder


def _cid(customer_id: str | None) -> str:
    return get_client_holder().resolve_customer_id(customer_id)


def register(mcp) -> None:
    @mcp.tool()
    def create_responsive_search_ad(
        ad_group_id: int,
        headlines: list[str],
        descriptions: list[str],
        final_urls: list[str],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        create = {
            "ad_group": f"customers/{cid}/adGroups/{ad_group_id}",
            "status": "ENABLED",
            "ad": {
                "final_urls": final_urls,
                "responsive_search_ad": {
                    "headlines": [{"text": h} for h in headlines],
                    "descriptions": [{"text": d} for d in descriptions],
                },
            },
        }
        return mutation_api.google_ads_mutate(
            "AdGroupAdService", [{"create": create}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def update_responsive_search_ad(
        ad_group_id: int,
        ad_id: int,
        updates: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        payload = {
            "resource_name": f"customers/{cid}/adGroupAds/{ad_group_id}~{ad_id}",
            **updates,
        }
        return mutation_api.google_ads_resource_mutate(
            "AdGroupAd",
            "update",
            payload,
            customer_id=cid,
            update_mask=list(updates.keys()),
            dry_run=dry_run,
        )

    @mcp.tool()
    def pause_ad(
        ad_group_id: int, ad_id: int, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        payload = {
            "resource_name": f"customers/{cid}/adGroupAds/{ad_group_id}~{ad_id}",
            "status": "PAUSED",
        }
        return mutation_api.google_ads_resource_mutate(
            "AdGroupAd", "update", payload, customer_id=cid, update_mask=["status"], dry_run=dry_run
        )

    @mcp.tool()
    def enable_ad(
        ad_group_id: int, ad_id: int, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        payload = {
            "resource_name": f"customers/{cid}/adGroupAds/{ad_group_id}~{ad_id}",
            "status": "ENABLED",
        }
        return mutation_api.google_ads_resource_mutate(
            "AdGroupAd", "update", payload, customer_id=cid, update_mask=["status"], dry_run=dry_run
        )

    @mcp.tool()
    def remove_ad(
        ad_group_id: int, ad_id: int, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_resource_mutate(
            "AdGroupAd",
            "remove",
            {"resource_name": f"customers/{cid}/adGroupAds/{ad_group_id}~{ad_id}"},
            customer_id=cid,
            dry_run=dry_run,
        )
