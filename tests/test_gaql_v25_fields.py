"""Validate predefined convenience GAQL against installed Google Ads v25 protos."""

from __future__ import annotations

import ast
import re
from pathlib import Path

from google.ads.googleads.v25.services.types.google_ads_service import GoogleAdsRow

ROOT = Path(__file__).resolve().parents[1]
REPORTING = ROOT / "tools" / "reporting.py"
BILLING = ROOT / "tools" / "billing.py"

_IDENT = re.compile(r"\b([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]+)+)\b", re.I)
_FROM = re.compile(r"\bFROM\s+(\w+)", re.I)
_PYTHON_RESERVED_FIELD = {"type": "type_"}


def _literal_queries(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    queries: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == "q" for t in node.targets):
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    queries.append(node.value.value)
    return queries


def _resolve_field(path: str) -> str | None:
    cur = GoogleAdsRow.pb().DESCRIPTOR
    parts = path.split(".")
    for i, raw in enumerate(parts):
        name = _PYTHON_RESERVED_FIELD.get(raw, raw)
        field = cur.fields_by_name.get(name) or cur.fields_by_name.get(raw)
        if field is None:
            return f"missing {raw} at {'.'.join(parts[:i]) or 'GoogleAdsRow'}"
        if i < len(parts) - 1:
            if field.message_type is None:
                return f"{raw} is not a nested message"
            cur = field.message_type
    return None


def test_convenience_gaql_uses_v25_campaign_datetime_fields():
    text = REPORTING.read_text()
    assert "campaign.start_date," not in text
    assert "campaign.end_date," not in text
    assert "campaign.start_date " not in text
    assert "campaign.end_date " not in text
    assert "campaign.start_date_time" in text
    assert "campaign.end_date_time" in text


def test_removed_v25_resources_are_not_queried():
    text = REPORTING.read_text()
    assert "FROM conversion_goal" not in text
    assert "FROM campaign_experiment" not in text
    assert "FROM invoice" not in text
    assert "FROM custom_conversion_goal" in text
    assert "FROM experiment_arm" in text


def test_all_predefined_gaql_fields_exist_on_v25_google_ads_row():
    queries = _literal_queries(REPORTING) + _literal_queries(BILLING)
    assert len(queries) >= 80
    problems: list[str] = []
    for query in queries:
        from_match = _FROM.search(query)
        if from_match:
            resource = from_match.group(1)
            err = _resolve_field(resource)
            if err:
                problems.append(f"FROM {resource}: {err} :: {query[:120]}")
        for field in _IDENT.findall(query):
            if field.upper().startswith("ORDER"):
                continue
            err = _resolve_field(field)
            if err:
                problems.append(f"{field}: {err} :: {query[:120]}")
    assert problems == []


def test_convenience_query_count_is_documented_for_parent_report():
    queries = _literal_queries(REPORTING) + _literal_queries(BILLING)
    # Keep a stable lower bound so accidental query deletions fail the suite.
    assert len(queries) == len(_literal_queries(REPORTING)) + len(_literal_queries(BILLING))
