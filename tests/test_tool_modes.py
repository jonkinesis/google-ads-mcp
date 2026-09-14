import asyncio
import importlib

import pytest

from app.config import Settings, get_settings
from tools.tool_modes import COMPACT_TOOL_NAMES, apply_tool_exposure


def _fresh_mcp(monkeypatch, mode: str):
    monkeypatch.setenv("MCP_TOOL_MODE", mode)
    get_settings.cache_clear()
    import app.server as server_module

    importlib.reload(server_module)
    return server_module.create_mcp()


def test_default_tool_mode_is_compact():
    settings = Settings.from_env({})
    assert settings.mcp_tool_mode == "compact"


def test_compact_exposes_subset(monkeypatch):
    mcp = _fresh_mcp(monkeypatch, "compact")
    exposed = asyncio.run(mcp.list_tools())
    exposed_names = {t.name for t in exposed}
    assert "google_ads_query" in exposed_names
    assert "remove_campaign" in exposed_names
    assert "create_campaign" not in exposed_names
    assert len(exposed_names) == len(COMPACT_TOOL_NAMES)
    assert len(exposed_names) <= 70


def test_full_exposes_all_implemented(monkeypatch):
    mcp = _fresh_mcp(monkeypatch, "full")
    exposed = {t.name for t in asyncio.run(mcp.list_tools())}
    assert "create_campaign" in exposed
    assert len(exposed) > len(COMPACT_TOOL_NAMES)


def test_invalid_tool_mode():
    with pytest.raises(ValueError):
        Settings.from_env({"MCP_TOOL_MODE": "invalid"})
