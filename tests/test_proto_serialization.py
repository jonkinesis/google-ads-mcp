"""Regression tests: proto-plus GoogleAdsRow serialization for paged and stream search."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

from google.ads.googleads.v25.enums.types.advertising_channel_type import (
    AdvertisingChannelTypeEnum,
)
from google.ads.googleads.v25.enums.types.campaign_status import CampaignStatusEnum
from google.ads.googleads.v25.enums.types.device import DeviceEnum
from google.ads.googleads.v25.services.types.google_ads_service import (
    GoogleAdsRow,
    SearchGoogleAdsStreamResponse,
)
from google.protobuf import json_format

from app.google_ads_client import execute_gaql
from app.proto_utils import _message_to_dict_kwargs, message_to_dict, rows_to_dicts


def _sample_row() -> GoogleAdsRow:
    row = GoogleAdsRow()
    row.campaign.id = 111
    row.campaign.name = "Myth Search"
    row.campaign.status = CampaignStatusEnum.CampaignStatus.ENABLED
    row.campaign.advertising_channel_type = (
        AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH
    )
    row.campaign.start_date_time = "2024-01-15 00:00:00"
    row.campaign.resource_name = "customers/1234567890/campaigns/111"
    row.metrics.impressions = 1000
    row.metrics.clicks = 40
    row.metrics.cost_micros = 2500000
    row.metrics.conversions = 2.5
    row.segments.device = DeviceEnum.Device.MOBILE
    row.ad_group_ad.ad.id = 99
    row.ad_group_ad.ad.final_urls.append("https://example.com/a")
    row.ad_group_ad.ad.final_urls.append("https://example.com/b")
    row.customer.time_zone = "America/New_York"
    return row


def test_legacy_messagetodict_kwargs_are_incompatible_with_installed_protobuf():
    row = _sample_row()
    params = json_format.MessageToDict.__code__.co_varnames
    if "including_default_value_fields" not in params:
        try:
            json_format.MessageToDict(
                row._pb,
                preserving_proto_field_name=False,
                including_default_value_fields=False,
            )
            raise AssertionError("expected TypeError for including_default_value_fields")
        except TypeError as exc:
            assert "including_default_value_fields" in str(exc)
    json_format.MessageToDict(row._pb, **_message_to_dict_kwargs())


def test_message_to_dict_preserves_nested_enums_metrics_and_repeated_fields():
    converted = message_to_dict(_sample_row())
    json.dumps(converted)
    assert converted["campaign"]["id"] == "111"
    assert converted["campaign"]["name"] == "Myth Search"
    assert converted["campaign"]["status"] == "ENABLED"
    assert converted["campaign"]["advertising_channel_type"] == "SEARCH"
    assert converted["campaign"]["start_date_time"] == "2024-01-15 00:00:00"
    assert converted["campaign"]["resource_name"].endswith("/campaigns/111")
    assert "end_date_time" not in converted["campaign"]
    assert converted["metrics"]["impressions"] == "1000"
    assert converted["metrics"]["clicks"] == "40"
    assert converted["metrics"]["cost_micros"] == "2500000"
    assert converted["segments"]["device"] == "MOBILE"
    assert converted["ad_group_ad"]["ad"]["final_urls"] == [
        "https://example.com/a",
        "https://example.com/b",
    ]
    assert converted["customer"]["time_zone"] == "America/New_York"


def test_rows_to_dicts_matches_message_to_dict():
    row = _sample_row()
    assert rows_to_dicts([row]) == [message_to_dict(row)]


def _patch_ads_service(monkeypatch, *, paged_rows, stream_batches):
    fake_service = MagicMock()
    fake_response = SimpleNamespace(results=paged_rows, next_page_token="")
    fake_service.search.return_value = fake_response
    fake_service.search_stream.return_value = stream_batches
    fake_client = MagicMock()
    fake_client.get_service.return_value = fake_service
    fake_client.get_type.return_value = MagicMock()
    holder = MagicMock()
    holder.resolve_customer_id.return_value = "1234567890"
    holder.get_client.return_value = fake_client
    monkeypatch.setattr("app.google_ads_client.get_client_holder", lambda: holder)
    return fake_service


def test_google_ads_query_paged_serializes_proto_rows(monkeypatch):
    row = _sample_row()
    _patch_ads_service(monkeypatch, paged_rows=[row], stream_batches=[])
    result = execute_gaql(
        "SELECT campaign.id, campaign.name, campaign.status, metrics.impressions FROM campaign",
        stream=False,
    )
    assert result["success"] is True
    assert result["row_count"] == 1
    assert result["data"][0]["campaign"]["status"] == "ENABLED"
    assert result["data"][0]["metrics"]["impressions"] == "1000"
    json.dumps(result)


def test_google_ads_query_stream_serializes_proto_rows(monkeypatch):
    row = _sample_row()
    batch = SearchGoogleAdsStreamResponse()
    batch.results.append(row)
    _patch_ads_service(monkeypatch, paged_rows=[], stream_batches=[batch])
    result = execute_gaql(
        "SELECT campaign.id, campaign.name, campaign.status, metrics.impressions FROM campaign",
        stream=True,
    )
    assert result["success"] is True
    assert result["streamed"] is True
    assert result["row_count"] == 1
    assert result["data"][0]["campaign"]["name"] == "Myth Search"
    assert result["data"][0]["segments"]["device"] == "MOBILE"
    json.dumps(result)


def test_paged_and_stream_share_json_schema(monkeypatch):
    row = _sample_row()
    batch = SearchGoogleAdsStreamResponse()
    batch.results.append(row)
    _patch_ads_service(monkeypatch, paged_rows=[row], stream_batches=[batch])
    query = "SELECT campaign.id, metrics.clicks FROM campaign"
    paged = execute_gaql(query, stream=False)
    streamed = execute_gaql(query, stream=True)
    assert paged["data"] == streamed["data"]


def test_convenience_reporting_tools_serialize_proto_rows(monkeypatch):
    row = _sample_row()
    batch = SearchGoogleAdsStreamResponse()
    batch.results.append(row)
    _patch_ads_service(monkeypatch, paged_rows=[row], stream_batches=[batch])
    from tools._helpers import gaql_tool

    queries = {
        "get_account_summary": (
            "SELECT customer.id, customer.descriptive_name, customer.currency_code, "
            "customer.time_zone, metrics.impressions, metrics.clicks, metrics.cost_micros, "
            "metrics.conversions FROM customer"
        ),
        "list_campaigns": (
            "SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type, "
            "campaign.start_date_time, campaign.end_date_time, customer.time_zone FROM campaign "
            "ORDER BY campaign.id"
        ),
        "get_campaign_performance": (
            "SELECT campaign.id, campaign.name, campaign.status, campaign.start_date_time, "
            "campaign.end_date_time, customer.time_zone, metrics.impressions, metrics.clicks, "
            "metrics.cost_micros, metrics.conversions, metrics.conversions_value FROM campaign"
        ),
    }
    for name, query in queries.items():
        paged = gaql_tool(query, date_range="LAST_30_DAYS" if "metrics" in query else None, stream=False)
        streamed = gaql_tool(query, date_range="LAST_30_DAYS" if "metrics" in query else None, stream=True)
        assert paged["success"] is True, name
        assert streamed["success"] is True, name
        assert paged["data"][0]["campaign"]["id"] == "111"
        assert not isinstance(paged["data"][0], str)
        json.dumps(paged)
        json.dumps(streamed)
