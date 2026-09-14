import asyncio

from app.config import get_settings
from app.server import create_mcp


def test_tool_discovery_lists_core_tools(monkeypatch):
    monkeypatch.setenv("MCP_TOOL_MODE", "full")
    get_settings.cache_clear()
    mcp = create_mcp()
    tools = asyncio.run(mcp._local_provider.list_tools())
    tool_names = sorted(t.name for t in tools)
    assert "google_ads_query" in tool_names
    assert "list_campaigns" in tool_names
    assert "create_campaign" in tool_names
    assert len(tool_names) > 100
