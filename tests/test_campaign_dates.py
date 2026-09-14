from datetime import datetime
from zoneinfo import ZoneInfo

from app.campaign_dates import (
    campaign_age_days,
    normalize_campaign_date_time,
    parse_campaign_date_time,
)


def test_normalize_date_only_to_v25_start_and_end():
    assert normalize_campaign_date_time("2024-03-01", end=False) == "2024-03-01 00:00:00"
    assert normalize_campaign_date_time("2024-03-01", end=True) == "2024-03-01 23:59:59"


def test_normalize_preserves_full_datetime():
    assert (
        normalize_campaign_date_time("2024-03-01 09:30:00") == "2024-03-01 09:30:00"
    )


def test_parse_in_customer_timezone():
    parsed = parse_campaign_date_time("2024-03-01 00:00:00", "America/New_York")
    assert parsed is not None
    assert parsed.tzinfo == ZoneInfo("America/New_York")


def test_campaign_age_days_in_customer_timezone():
    age = campaign_age_days(
        "2024-03-01 00:00:00",
        time_zone="America/New_York",
        as_of=datetime(2024, 3, 11, 12, 0, tzinfo=ZoneInfo("America/New_York")),
    )
    assert age == 10
