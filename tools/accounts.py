"""Account-level MCP tools."""

from __future__ import annotations

from typing import Any

from app.google_ads_client import list_accessible_customers as fetch_accessible_customers


def register(mcp) -> None:
    @mcp.tool()
    def list_accessible_customers() -> dict[str, Any]:
        """List Google Ads customer IDs accessible to the authenticated service account."""
        return fetch_accessible_customers()
