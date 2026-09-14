"""Google Ads client factory and query execution."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from google.ads.googleads.client import GoogleAdsClient, _DEFAULT_VERSION
from google.ads.googleads.errors import GoogleAdsException

from app.auth import build_google_ads_credentials
from app.config import Settings, get_settings
from app.errors import format_exception, success_payload
from app.gaql import validate_gaql
from app.proto_utils import message_to_dict, rows_to_dicts


class GoogleAdsClientHolder:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client: GoogleAdsClient | None = None

    @property
    def api_version(self) -> str:
        client = self.get_client()
        return client.version or _DEFAULT_VERSION

    def get_client(self) -> GoogleAdsClient:
        if self._client is None:
            self._settings.require_google_ads_config()
            credentials = build_google_ads_credentials(self._settings)
            self._client = GoogleAdsClient(
                credentials=credentials,
                developer_token=None,
                login_customer_id=self._settings.google_ads_login_customer_id,
                use_proto_plus=True,
            )
        return self._client

    def resolve_customer_id(self, customer_id: str | None) -> str:
        cid = customer_id or self._settings.google_ads_customer_id
        if not cid:
            raise ValueError(
                "customer_id is required (set GOOGLE_ADS_CUSTOMER_ID or pass customer_id)."
            )
        return cid.replace("-", "")


@lru_cache(maxsize=1)
def get_client_holder() -> GoogleAdsClientHolder:
    return GoogleAdsClientHolder()


def execute_gaql(
    query: str,
    *,
    customer_id: str | None = None,
    page_size: int | None = None,
    stream: bool = False,
) -> dict[str, Any]:
    holder = get_client_holder()
    validate_gaql(query)
    cid = holder.resolve_customer_id(customer_id)
    client = holder.get_client()
    service = client.get_service("GoogleAdsService")
    try:
        if stream:
            stream_iter = service.search_stream(
                customer_id=cid, query=query, timeout=300
            )
            rows: list[dict[str, Any]] = []
            for batch in stream_iter:
                rows.extend(rows_to_dicts(batch.results))
            return success_payload(rows, customer_id=cid, row_count=len(rows), streamed=True)
        request = client.get_type("SearchGoogleAdsRequest")
        request.customer_id = cid
        request.query = query
        if page_size:
            request.page_size = page_size
        response = service.search(request=request)
        page_rows = getattr(response, "results", response)
        rows = rows_to_dicts(page_rows)
        next_page_token = getattr(response, "next_page_token", None) or None
        return success_payload(
            rows,
            customer_id=cid,
            row_count=len(rows),
            next_page_token=next_page_token,
        )
    except GoogleAdsException as exc:
        return format_exception(exc, customer_id=cid, request_id=exc.request_id)
    except Exception as exc:  # noqa: BLE001
        return format_exception(exc, customer_id=cid)


def search_google_ads_fields(query: str) -> dict[str, Any]:
    holder = get_client_holder()
    client = holder.get_client()
    service = client.get_service("GoogleAdsFieldService")
    request = client.get_type("SearchGoogleAdsFieldsRequest")
    request.query = query
    try:
        response = service.search_google_ads_fields(request=request)
        return success_payload(rows_to_dicts(response.results))
    except GoogleAdsException as exc:
        return format_exception(exc, request_id=exc.request_id)
    except Exception as exc:  # noqa: BLE001
        return format_exception(exc)


def list_accessible_customers() -> dict[str, Any]:
    holder = get_client_holder()
    client = holder.get_client()
    service = client.get_service("CustomerService")
    try:
        response = service.list_accessible_customers()
        return success_payload(list(response.resource_names))
    except GoogleAdsException as exc:
        return format_exception(exc, request_id=exc.request_id)
    except Exception as exc:  # noqa: BLE001
        return format_exception(exc)


def mutate_response_to_dict(response: Any) -> dict[str, Any]:
    return message_to_dict(response)
