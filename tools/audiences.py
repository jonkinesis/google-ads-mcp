"""Audience and user list tools."""

from __future__ import annotations

from typing import Any

from app import mutations as mutation_api
from app.google_ads_client import get_client_holder


def _cid(customer_id: str | None) -> str:
    return get_client_holder().resolve_customer_id(customer_id)


def register(mcp) -> None:
    @mcp.tool()
    def create_user_list(
        payload: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        return mutation_api.google_ads_mutate(
            "UserListService", [{"create": payload}], customer_id=cid, dry_run=dry_run
        )

    @mcp.tool()
    def update_user_list(
        user_list_id: int,
        updates: dict[str, Any],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        payload = {
            "resource_name": f"customers/{cid}/userLists/{user_list_id}",
            **updates,
        }
        return mutation_api.google_ads_resource_mutate(
            "UserList",
            "update",
            payload,
            customer_id=cid,
            update_mask=list(updates.keys()),
            dry_run=dry_run,
        )

    @mcp.tool()
    def add_customer_match_members(
        user_list_id: int,
        members: list[dict[str, Any]],
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        cid = _cid(customer_id)
        request = {
            "resource_name": f"customers/{cid}/userLists/{user_list_id}",
            "operations": [{"create": m} for m in members],
        }
        return mutation_api.google_ads_service_call(
            "OfflineUserDataJobService",
            "create_offline_user_data_job",
            {"job": {"type": "CUSTOMER_MATCH_USER_LIST", "customer_match_user_list_metadata": {"user_list": f"customers/{cid}/userLists/{user_list_id}"}}},
            customer_id=cid,
            dry_run=dry_run,
            tool_name="add_customer_match_members",
        )

    @mcp.tool()
    def remove_customer_match_members(
        user_list_id: int,
        customer_id: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return {
            "success": False,
            "message": "Use OfflineUserDataJobService via google_ads_service_call to remove customer match members.",
            "suggested_action": "Create an offline user data job with REMOVE operations.",
        }
