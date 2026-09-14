"""MCP tool exposure modes (compact vs full)."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

logger = logging.getLogger("google_ads_mcp")

LAST_IMPLEMENTED_TOOL_COUNT: int = 0
LAST_EXPOSED_TOOL_COUNT: int = 0

# All tools remain registered; compact mode limits MCP discovery/calls to this set.
COMPACT_TOOL_NAMES: frozenset[str] = frozenset(
    {
        # Generic / future-proof
        "google_ads_query",
        "google_ads_describe_fields",
        "google_ads_list_services",
        "google_ads_service_call",
        "google_ads_mutate",
        "google_ads_batch_mutate",
        "google_ads_resource_mutate",
        "google_ads_multi_mutate",
        "google_ads_batch_job",
        # Account access
        "list_accessible_customers",
        # Reporting
        "get_account_summary",
        "list_campaigns",
        "get_campaign_performance",
        "get_campaign_statuses",
        "list_campaign_budgets",
        "get_budget_performance",
        "list_ad_groups",
        "get_ad_group_performance",
        "list_ads",
        "get_ad_performance",
        "list_keywords",
        "get_keyword_performance",
        "get_search_terms",
        "get_search_term_performance",
        "get_device_performance",
        "get_geographic_performance",
        "get_conversions",
        "get_conversion_performance",
        "get_recommendations",
        "get_policy_issues",
        "get_disapproved_ads",
        "get_change_history",
        # Campaign / budget changes
        "pause_campaign",
        "enable_campaign",
        "update_campaign",
        "set_campaign_daily_budget",
        "set_campaign_bid_strategy",
        # Ad groups
        "pause_ad_group",
        "enable_ad_group",
        "set_ad_group_bid",
        # Keywords
        "add_keyword",
        "pause_keyword",
        "enable_keyword",
        "add_negative_keyword",
        "remove_negative_keyword",
        # Ads
        "pause_ad",
        "enable_ad",
        # Recommendations
        "apply_recommendation",
        "dismiss_recommendation",
        # Explicit removals / detach (compact cleanup)
        "remove_campaign",
        "remove_ad_group",
        "remove_ad",
        "remove_keyword",
        "remove_location_target",
        "remove_location_exclusion",
        "remove_ad_schedule",
        "detach_asset_from_campaign",
        "detach_asset_from_ad_group",
        "detach_asset_from_customer",
        "remove_label",
        "remove_data_exclusion",
        "remove_seasonality_adjustment",
        "remove_customer_match_members",
        "remove_shared_criterion",
        "remove_shared_set",
    }
)


def normalize_tool_mode(raw: str | None) -> str:
    mode = (raw or "compact").strip().lower()
    if mode not in {"compact", "full"}:
        raise ValueError("MCP_TOOL_MODE must be 'compact' or 'full'.")
    return mode


async def count_exposed_tools(mcp: FastMCP) -> int:
    tools = await mcp.list_tools()
    return len(tools)


async def list_exposed_tool_names(mcp: FastMCP) -> list[str]:
    tools = await mcp.list_tools()
    return sorted(t.name for t in tools)


async def list_implemented_tool_names(mcp: FastMCP) -> list[str]:
    tools = await mcp._local_provider.list_tools()
    return sorted(t.name for t in tools)


def apply_tool_exposure(mcp: FastMCP, mode: str) -> None:
    global LAST_IMPLEMENTED_TOOL_COUNT, LAST_EXPOSED_TOOL_COUNT

    mode = normalize_tool_mode(mode)
    implemented_names = set(asyncio.run(list_implemented_tool_names(mcp)))
    LAST_IMPLEMENTED_TOOL_COUNT = len(implemented_names)

    if mode == "full":
        LAST_EXPOSED_TOOL_COUNT = LAST_IMPLEMENTED_TOOL_COUNT
        logger.info(
            "MCP tool exposure: full (%s tools exposed)",
            LAST_EXPOSED_TOOL_COUNT,
        )
        return

    missing = sorted(COMPACT_TOOL_NAMES - implemented_names)
    if missing:
        raise ValueError(
            "Compact mode references tools that are not registered: "
            + ", ".join(missing)
        )

    mcp.enable(names=set(COMPACT_TOOL_NAMES), only=True)
    LAST_EXPOSED_TOOL_COUNT = asyncio.run(count_exposed_tools(mcp))
    logger.info(
        "MCP tool exposure: compact (%s tools exposed, %s implemented)",
        LAST_EXPOSED_TOOL_COUNT,
        LAST_IMPLEMENTED_TOOL_COUNT,
    )
