"""Label tools."""

from __future__ import annotations

from typing import Any

from app import mutations as mutation_api
from app.google_ads_client import get_client_holder


def _cid(customer_id: str | None) -> str:
    return get_client_holder().resolve_customer_id(customer_id)


def register(mcp) -> None:
    @mcp.tool()
    def create_label(
        name: str, customer_id: str | None = None, dry_run: bool = False
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_mutate(
            "LabelService", [{"create": {"name": name}}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def apply_label(
        service_name: str,
        operation: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Apply a label using the appropriate *LabelService (campaign/ad_group/ad/keyword)."""
        return mutation_api.google_ads_mutate(
            service_name, [{"create": operation}], customer_id=customer_id, dry_run=dry_run
        )

    @mcp.tool()
    def remove_label(
        service_name: str,
        resource_name: str,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        resource_type = service_name.replace("Service", "")
        return mutation_api.google_ads_resource_mutate(
            resource_type,
            "remove",
            {"resource_name": resource_name},
            customer_id=customer_id,
            dry_run=dry_run,
        )
