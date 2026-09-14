"""Recommendation tools."""

from __future__ import annotations

from typing import Any

from app import mutations as mutation_api


def register(mcp) -> None:
    @mcp.tool()
    def apply_recommendation(
        resource_name: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        request = {"operations": [{"resource_name": resource_name}]}
        return mutation_api.google_ads_service_call(
            "RecommendationService",
            "apply_recommendation",
            request,
            customer_id=customer_id,
            dry_run=dry_run,
            tool_name="apply_recommendation",
        )

    @mcp.tool()
    def dismiss_recommendation(
        resource_name: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        request = {"operations": [{"resource_name": resource_name}]}
        return mutation_api.google_ads_service_call(
            "RecommendationService",
            "dismiss_recommendation",
            request,
            customer_id=customer_id,
            dry_run=dry_run,
            tool_name="dismiss_recommendation",
        )
