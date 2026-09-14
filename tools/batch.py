"""Batch job tools."""

from __future__ import annotations

from typing import Any

from app import mutations as mutation_api


def register(mcp) -> None:
    @mcp.tool()
    def google_ads_batch_job(
        action: str,
        payload: dict[str, Any] | None = None,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Manage batch jobs: create, add_operations, run, status, list_results."""
        payload = payload or {}
        action = action.lower()
        if action == "create":
            return mutation_api.google_ads_service_call(
                "BatchJobService",
                "mutate_batch_job",
                {"operation": {"create": payload.get("batch_job", {})}},
                customer_id=customer_id,
                dry_run=dry_run,
                tool_name="google_ads_batch_job",
            )
        if action == "add_operations":
            return mutation_api.google_ads_service_call(
                "BatchJobService",
                "add_batch_job_operations",
                payload,
                customer_id=customer_id,
                dry_run=dry_run,
                tool_name="google_ads_batch_job",
            )
        if action == "run":
            return mutation_api.google_ads_service_call(
                "BatchJobService",
                "run_batch_job",
                payload,
                customer_id=customer_id,
                dry_run=dry_run,
                tool_name="google_ads_batch_job",
            )
        if action == "status":
            return mutation_api.google_ads_service_call(
                "BatchJobService",
                "list_batch_job_results",
                payload,
                customer_id=customer_id,
                dry_run=dry_run,
                tool_name="google_ads_batch_job",
            )
        if action == "list_results":
            return mutation_api.google_ads_service_call(
                "BatchJobService",
                "list_batch_job_results",
                payload,
                customer_id=customer_id,
                dry_run=dry_run,
                tool_name="google_ads_batch_job",
            )
        return {
            "success": False,
            "message": "action must be one of: create, add_operations, run, status, list_results",
        }
