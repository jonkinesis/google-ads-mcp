import pytest

from app.gaql import validate_gaql
from app.safety import check_budget_change, check_bid_change


def test_validate_gaql_rejects_empty():
    with pytest.raises(ValueError):
        validate_gaql("")


def test_validate_gaql_requires_select_from():
    with pytest.raises(ValueError):
        validate_gaql("UPDATE campaign SET name = 'x'")


def test_budget_limit_blocks_large_change():
    result = check_budget_change(1_000_000, 2_000_000, override_limits=False)
    assert result.allowed is False


def test_budget_limit_allows_with_override():
    result = check_budget_change(1_000_000, 2_000_000, override_limits=True)
    assert result.allowed is True


def test_bid_limit_blocks_large_change():
    result = check_bid_change(1_000_000, 2_000_000, override_limits=False)
    assert result.allowed is False
