"""Structured audit logging for MCP write operations."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("google_ads_mcp.audit")


def audit_log(
    *,
    tool_name: str,
    customer_id: str | None,
    action: str,
    resource_names: list[str] | None = None,
    dry_run: bool = False,
    success: bool = True,
    request_id: str | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "tool_name": tool_name,
        "customer_id": customer_id,
        "action": action,
        "resource_names": resource_names or [],
        "dry_run": dry_run,
        "success": success,
        "request_id": request_id,
    }
    if detail:
        entry["detail"] = detail
    logger.info(json.dumps(entry, default=str))
