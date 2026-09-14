"""Protobuf helpers for Google Ads messages."""

from __future__ import annotations

from typing import Any

from google.protobuf import json_format
from google.protobuf.message import Message


def message_to_dict(message: Any) -> dict[str, Any]:
    if message is None:
        return {}
    pb = message._pb if hasattr(message, "_pb") else message
    return json_format.MessageToDict(
        pb, preserving_proto_field_name=False, including_default_value_fields=False
    )


def parse_dict_to_message(message: Any, data: dict[str, Any]) -> Any:
    pb = message._pb if hasattr(message, "_pb") else message
    json_format.ParseDict(data, pb, ignore_unknown_fields=False)
    return message


def rows_to_dicts(rows: list[Any]) -> list[dict[str, Any]]:
    return [message_to_dict(row) for row in rows]
