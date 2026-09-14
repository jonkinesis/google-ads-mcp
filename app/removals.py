"""Removal operation metadata and audit helpers."""

from __future__ import annotations

from typing import Any


def extract_remove_resource_names(operations: list[Any]) -> list[str]:
    names: list[str] = []
    for operation in operations:
        if not isinstance(operation, dict):
            continue
        if "remove" in operation and operation["remove"]:
            names.append(str(operation["remove"]))
        for value in operation.values():
            if isinstance(value, dict) and value.get("remove"):
                names.append(str(value["remove"]))
    return names


def removal_records(customer_id: str, resource_names: list[str]) -> list[dict[str, str]]:
    return [
        {"customer_id": customer_id, "resource_name": resource_name}
        for resource_name in resource_names
    ]


def enrich_removal_result(
    result: dict[str, Any],
    *,
    customer_id: str,
    resource_names: list[str],
    dry_run: bool,
) -> dict[str, Any]:
    if not resource_names:
        return result
    records = removal_records(customer_id, resource_names)
    result["before_execution"] = {
        "removals": records,
        "dry_run": dry_run,
        "message": (
            "Dry-run validation only; no resources removed."
            if dry_run
            else "The following resource(s) are targeted for removal."
        ),
    }
    if result.get("success"):
        result["after_execution"] = {
            "removals": records,
            "executed": not dry_run and not result.get("dry_run", False),
            "message": (
                "Removal validated (dry_run=true)."
                if dry_run or result.get("dry_run")
                else "Removal request completed for the resource(s) below."
            ),
        }
    return result
