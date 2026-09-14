"""Safety limits for budget and bid changes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config import Settings, get_settings


@dataclass
class LimitCheckResult:
    allowed: bool
    message: str | None = None
    warning: str | None = None


def check_percent_change(
    *,
    current: float | None,
    new: float | None,
    max_percent: float | None,
    override_limits: bool,
    resource_label: str,
) -> LimitCheckResult:
    if max_percent is None or override_limits:
        return LimitCheckResult(allowed=True)
    if current is None or new is None:
        return LimitCheckResult(
            allowed=True,
            warning=(
                f"Could not verify {resource_label} change limits because current or new value is unknown."
            ),
        )
    if current <= 0:
        return LimitCheckResult(allowed=True)
    change_pct = abs((new - current) / current) * 100.0
    if change_pct > max_percent:
        return LimitCheckResult(
            allowed=False,
            message=(
                f"{resource_label} change of {change_pct:.2f}% exceeds MAX limit of {max_percent:.2f}%. "
                "Set override_limits=true to proceed."
            ),
        )
    return LimitCheckResult(allowed=True)


def check_budget_change(
    current_micros: int | None,
    new_micros: int | None,
    override_limits: bool,
    settings: Settings | None = None,
) -> LimitCheckResult:
    settings = settings or get_settings()
    current = current_micros / 1_000_000 if current_micros is not None else None
    new = new_micros / 1_000_000 if new_micros is not None else None
    return check_percent_change(
        current=current,
        new=new,
        max_percent=settings.max_budget_change_percent,
        override_limits=override_limits,
        resource_label="Budget",
    )


def check_bid_change(
    current_micros: int | None,
    new_micros: int | None,
    override_limits: bool,
    settings: Settings | None = None,
) -> LimitCheckResult:
    settings = settings or get_settings()
    current = current_micros / 1_000_000 if current_micros is not None else None
    new = new_micros / 1_000_000 if new_micros is not None else None
    return check_percent_change(
        current=current,
        new=new,
        max_percent=settings.max_bid_change_percent,
        override_limits=override_limits,
        resource_label="Bid",
    )


def raw_mutation_limit_warning(override_limits: bool) -> str | None:
    settings = get_settings()
    if settings.max_budget_change_percent or settings.max_bid_change_percent:
        if not override_limits:
            return (
                "Generic mutation tools do not enforce MAX_BUDGET_CHANGE_PERCENT / "
                "MAX_BID_CHANGE_PERCENT. Use convenience budget/bid tools or set override_limits=true knowingly."
            )
    return None


def remove_operation_summary(
    resource_name: str, customer_id: str, resource_type: str
) -> dict[str, Any]:
    return {
        "will_remove": True,
        "resource_type": resource_type,
        "resource_name": resource_name,
        "customer_id": customer_id,
        "message": f"This operation will REMOVE {resource_type} {resource_name} for customer {customer_id}.",
    }
