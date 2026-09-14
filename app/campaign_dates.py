"""v25 campaign schedule field helpers (start_date_time / end_date_time)."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_DATE_ONLY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATE_TIME = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")


def normalize_campaign_date_time(value: str | None, *, end: bool = False) -> str | None:
    """Map YYYY-MM-DD (or full datetime) to campaign.start_date_time / end_date_time.

    Google Ads v25 stores campaign schedule as customer-timezone timestamps in
    ``yyyy-MM-dd HH:mm:ss``. Date-only values get 00:00:00 (start) or 23:59:59 (end).
    """
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if _DATE_ONLY.fullmatch(text):
        suffix = "23:59:59" if end else "00:00:00"
        return f"{text} {suffix}"
    if _DATE_TIME.fullmatch(text):
        return text
    raise ValueError(
        "Campaign dates must be 'yyyy-MM-dd' or 'yyyy-MM-dd HH:mm:ss' "
        "(customer timezone, Google Ads API v25 start_date_time / end_date_time)."
    )


def parse_campaign_date_time(value: str | None, time_zone: str | None = None) -> datetime | None:
    """Parse a v25 campaign date-time string, attaching customer timezone when known."""
    if not value or not str(value).strip():
        return None
    text = str(value).strip()
    naive = datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
    if not time_zone:
        return naive
    try:
        return naive.replace(tzinfo=ZoneInfo(time_zone))
    except ZoneInfoNotFoundError:
        return naive


def campaign_age_days(
    start_date_time: str | None,
    *,
    time_zone: str | None = None,
    as_of: datetime | None = None,
) -> int | None:
    """Whole days since campaign.start_date_time in the customer timezone."""
    start = parse_campaign_date_time(start_date_time, time_zone)
    if start is None:
        return None
    now = as_of
    if now is None:
        tz = start.tzinfo
        now = datetime.now(tz) if tz is not None else datetime.now()
    elif start.tzinfo is not None and now.tzinfo is None:
        now = now.replace(tzinfo=start.tzinfo)
    elif start.tzinfo is None and now.tzinfo is not None:
        now = now.replace(tzinfo=None)
    delta: timedelta = now - start
    return max(delta.days, 0)
