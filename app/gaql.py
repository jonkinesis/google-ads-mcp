"""GAQL validation helpers."""

from __future__ import annotations

import re

_FORBIDDEN = re.compile(r"(;|--|/\*|\*/)", re.MULTILINE)
_SELECT_REQUIRED = re.compile(r"^\s*SELECT\s+", re.IGNORECASE | re.DOTALL)
_FROM_REQUIRED = re.compile(r"\bFROM\s+\w+", re.IGNORECASE)


def validate_gaql(query: str) -> None:
    if not query or not query.strip():
        raise ValueError("GAQL query cannot be empty.")
    if _FORBIDDEN.search(query):
        raise ValueError("GAQL query must not contain SQL-style comment or statement separators.")
    if not _SELECT_REQUIRED.search(query):
        raise ValueError("GAQL query must begin with SELECT.")
    if not _FROM_REQUIRED.search(query):
        raise ValueError("GAQL query must include a FROM clause.")


def apply_date_range(base_query: str, date_range: str | None) -> str:
    if not date_range:
        return base_query
    clause = f"segments.date DURING {date_range}"
    if " WHERE " in base_query.upper():
        return f"{base_query} AND {clause}"
    return f"{base_query} WHERE {clause}"
