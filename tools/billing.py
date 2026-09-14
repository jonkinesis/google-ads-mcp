"""Billing read/write helpers."""

from __future__ import annotations

from typing import Any

from app import mutations as mutation_api
from tools._helpers import gaql_tool


def register(mcp) -> None:
    @mcp.tool()
    def get_billing_setups_tool(
        customer_id: str | None = None,
    ) -> dict[str, Any]:
        """Read billing setups (alias for reporting convenience)."""
        q = "SELECT billing_setup.id, billing_setup.status, billing_setup.payments_account_info.payments_account_name FROM billing_setup"
        return gaql_tool(q, customer_id=customer_id)

    @mcp.tool()
    def create_billing_setup(
        payload: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return mutation_api.google_ads_mutate(
            "BillingSetupService", [{"create": payload}], customer_id=customer_id, dry_run=dry_run
        )
