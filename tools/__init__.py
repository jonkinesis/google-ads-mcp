"""MCP tool registration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_all_tools(mcp: FastMCP) -> None:
    from tools import (
        accounts,
        ad_groups,
        ads,
        assets,
        audiences,
        batch,
        bidding,
        billing,
        budgets,
        campaigns,
        conversions,
        experiments,
        keywords,
        labels,
        performance_max,
        raw_api,
        recommendations,
        reporting,
        targeting,
    )

    modules = [
        raw_api,
        accounts,
        reporting,
        campaigns,
        budgets,
        ad_groups,
        ads,
        keywords,
        targeting,
        assets,
        bidding,
        conversions,
        recommendations,
        audiences,
        performance_max,
        experiments,
        billing,
        batch,
        labels,
    ]
    for module in modules:
        module.register(mcp)
