"""Protobuf helpers for Google Ads messages."""

from __future__ import annotations

import inspect
from typing import Any, Iterable

from google.protobuf import json_format
from google.protobuf.message import Message

_MESSAGE_TO_DICT_PARAMS = inspect.signature(json_format.MessageToDict).parameters


def _as_protobuf(message: Any) -> Message | None:
    if message is None:
        return None
    if isinstance(message, Message):
        return message
    pb = getattr(message, "_pb", None)
    if isinstance(pb, Message):
        return pb
    return None


def _message_to_dict_kwargs() -> dict[str, Any]:
    """Build MessageToDict kwargs for the installed protobuf version.

    protobuf 4.x used ``including_default_value_fields``. protobuf 5.26+
    renamed that option to ``always_print_fields_with_no_presence``; 6.x/7.x
    removed the old name. Passing the stale keyword raises TypeError after a
    successful Google Ads RPC (paged search and search_stream share this path).
    """
    kwargs: dict[str, Any] = {}
    if "preserving_proto_field_name" in _MESSAGE_TO_DICT_PARAMS:
        kwargs["preserving_proto_field_name"] = True
    if "use_integers_for_enums" in _MESSAGE_TO_DICT_PARAMS:
        kwargs["use_integers_for_enums"] = False
    if "always_print_fields_with_no_presence" in _MESSAGE_TO_DICT_PARAMS:
        kwargs["always_print_fields_with_no_presence"] = False
    elif "including_default_value_fields" in _MESSAGE_TO_DICT_PARAMS:
        kwargs["including_default_value_fields"] = False
    return kwargs


def message_to_dict(message: Any) -> dict[str, Any]:
    if message is None:
        return {}
    if isinstance(message, dict):
        return message
    pb = _as_protobuf(message)
    if pb is None:
        raise TypeError(
            f"Cannot convert {type(message)!r} to dict; expected a protobuf or proto-plus message."
        )
    converted = json_format.MessageToDict(pb, **_message_to_dict_kwargs())
    if converted is None:
        return {}
    if not isinstance(converted, dict):
        raise TypeError(
            f"Protobuf JSON conversion produced {type(converted)!r}, expected dict."
        )
    return converted


def parse_dict_to_message(message: Any, data: dict[str, Any]) -> Any:
    pb = _as_protobuf(message)
    if pb is None:
        raise TypeError(
            f"Cannot parse dict into {type(message)!r}; expected a protobuf or proto-plus message."
        )
    json_format.ParseDict(data, pb, ignore_unknown_fields=False)
    return message


def rows_to_dicts(rows: Iterable[Any] | None) -> list[dict[str, Any]]:
    if rows is None:
        return []
    return [message_to_dict(row) for row in rows]
