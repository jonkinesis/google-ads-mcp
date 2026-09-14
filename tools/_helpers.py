"""Shared helpers for MCP tools."""

from __future__ import annotations

from typing import Any

from app.gaql import apply_date_range
from app.google_ads_client import execute_gaql


def gaql_tool(
    query: str,
    *,
    customer_id: str | None = None,
    date_range: str | None = None,
    page_size: int | None = None,
    stream: bool = False,
) -> dict[str, Any]:
    final_query = apply_date_range(query, date_range)
    return execute_gaql(
        final_query,
        customer_id=customer_id,
        page_size=page_size,
        stream=stream,
    )
