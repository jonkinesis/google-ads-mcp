"""Remote Google Ads MCP server (FastMCP + ASGI)."""

from __future__ import annotations

import logging
import os
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import get_settings
from app.observations import register_observations
from tools import register_all_tools
from tools.tool_modes import apply_tool_exposure

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("google_ads_mcp")


def create_mcp() -> FastMCP:
    settings = get_settings()
    auth = None
    if settings.mcp_api_key:
        auth = StaticTokenVerifier(
            tokens={
                settings.mcp_api_key: {
                    "client_id": "google-ads-mcp",
                    "scopes": [],
                }
            }
        )
    mcp = FastMCP(
        "google-ads-mcp",
        instructions=(
            "Broad Google Ads MCP for Myth Nightclub account monitoring, reporting, "
            "and controlled optimizations. Use dry_run=true to validate mutations."
        ),
        auth=auth,
    )

    @mcp.custom_route("/health", methods=["GET"])
    async def health(_: Request) -> JSONResponse:
        tools_exposed = len(await mcp.list_tools())
        tools_implemented = len(await mcp._local_provider.list_tools())
        payload: dict[str, Any] = {
            "status": "ok",
            "service": "google-ads-mcp",
            "mcp_tool_mode": settings.mcp_tool_mode,
            "tools_exposed": tools_exposed,
            "tools_implemented": tools_implemented,
            "google_ads_configured": bool(settings.google_service_account_json),
            "default_customer_configured": bool(settings.google_ads_customer_id),
        }
        return JSONResponse(payload)

    register_observations(mcp)
    register_all_tools(mcp)
    apply_tool_exposure(mcp, settings.mcp_tool_mode)
    return mcp


mcp = create_mcp()
app = mcp.http_app(
    path="/mcp",
    transport="http",
    stateless_http=True,
)


def main() -> None:
    settings = get_settings()
    host = os.environ.get("HOST", "0.0.0.0")
    port = settings.port
    logger.info("Starting google-ads-mcp on %s:%s", host, port)
    mcp.run_http_async(host=host, port=port, path="/mcp", stateless_http=True)


if __name__ == "__main__":
    main()
