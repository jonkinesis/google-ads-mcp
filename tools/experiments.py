"""Experiment tools."""

from __future__ import annotations

from typing import Any

from app import mutations as mutation_api


def register(mcp) -> None:
    @mcp.tool()
    def create_experiment(
        payload: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return mutation_api.google_ads_mutate(
            "ExperimentService", [{"create": payload}], customer_id=customer_id, dry_run=dry_run
        )

    @mcp.tool()
    def update_experiment(
        resource_name: str,
        updates: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        payload = {"resource_name": resource_name, **updates}
        return mutation_api.google_ads_resource_mutate(
            "Experiment",
            "update",
            payload,
            customer_id=customer_id,
            update_mask=list(updates.keys()),
            dry_run=dry_run,
        )

    @mcp.tool()
    def schedule_experiment(
        resource_name: str, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        return mutation_api.google_ads_service_call(
            "ExperimentService",
            "schedule_experiment",
            {"resource_name": resource_name},
            customer_id=customer_id,
            dry_run=dry_run,
            tool_name="schedule_experiment",
        )

    @mcp.tool()
    def end_experiment(
        resource_name: str, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        return mutation_api.google_ads_service_call(
            "ExperimentService",
            "end_experiment",
            {"resource_name": resource_name},
            customer_id=customer_id,
            dry_run=dry_run,
            tool_name="end_experiment",
        )

    @mcp.tool()
    def promote_experiment_if_supported(
        resource_name: str, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        return mutation_api.google_ads_service_call(
            "ExperimentService",
            "promote_experiment",
            {"resource_name": resource_name},
            customer_id=customer_id,
            dry_run=dry_run,
            tool_name="promote_experiment_if_supported",
        )
