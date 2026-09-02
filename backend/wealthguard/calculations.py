"""Deterministic financial calculations used by the research service.

All price series supplied by the offline demo are synthetic. These functions are
pure, validated and independently testable; no language model performs arithmetic.
"""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from collections.abc import Iterable
from decimal import ROUND_HALF_UP, Decimal


def _validate_prices(prices: Iterable[float]) -> list[float]:
    values = [float(value) for value in prices]
    if len(values) < 2:
        raise ValueError("at least two prices are required")
    if any(not math.isfinite(value) or value <= 0 for value in values):
        raise ValueError("prices must be finite and positive")
    return values


def period_return(prices: Iterable[float]) -> float:
    values = _validate_prices(prices)
    return values[-1] / values[0] - 1.0


def periodic_returns(prices: Iterable[float]) -> list[float]:
    values = _validate_prices(prices)
    return [current / previous - 1.0 for previous, current in zip(values[:-1], values[1:], strict=True)]


def annualized_return(prices: Iterable[float], periods_per_year: int = 12) -> float:
    values = _validate_prices(prices)
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive")
    periods = len(values) - 1
    return (values[-1] / values[0]) ** (periods_per_year / periods) - 1.0


def annualized_volatility(prices: Iterable[float], periods_per_year: int = 12) -> float:
    returns = periodic_returns(prices)
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive")
    if len(returns) < 2:
        return 0.0
    return statistics.stdev(returns) * math.sqrt(periods_per_year)


def maximum_drawdown(prices: Iterable[float]) -> float:
    values = _validate_prices(prices)
    peak = values[0]
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1.0)
    return worst


def fee_impact(
    principal: Decimal | str | float,
    gross_annual_return: Decimal | str | float,
    annual_fee: Decimal | str | float,
    years: int,
) -> dict[str, float]:
    if years < 0:
        raise ValueError("years must be non-negative")
    amount = Decimal(str(principal))
    gross = Decimal(str(gross_annual_return))
    fee = Decimal(str(annual_fee))
    if amount < 0 or fee < 0 or gross <= Decimal("-1") or gross - fee <= Decimal("-1"):
        raise ValueError("invalid principal, return or fee")
    without_fees = amount * ((Decimal("1") + gross) ** years)
    with_fees = amount * ((Decimal("1") + gross - fee) ** years)
    quant = Decimal("0.01")
    return {
        "without_fees": float(without_fees.quantize(quant, rounding=ROUND_HALF_UP)),
        "with_fees": float(with_fees.quantize(quant, rounding=ROUND_HALF_UP)),
        "fee_drag": float((without_fees - with_fees).quantize(quant, rounding=ROUND_HALF_UP)),
    }


def concentration_ratio(weights: Iterable[float]) -> dict[str, float]:
    values = [float(weight) for weight in weights]
    if not values or any(weight < 0 or not math.isfinite(weight) for weight in values):
        raise ValueError("weights must be finite, non-negative and non-empty")
    total = sum(values)
    if abs(total - 1.0) > 1e-6:
        raise ValueError("weights must sum to one")
    ordered = sorted(values, reverse=True)
    return {
        "largest_position": ordered[0],
        "top_three": sum(ordered[:3]),
        "herfindahl_index": sum(weight * weight for weight in values),
    }


def aggregate_exposure(
    holdings: Iterable[tuple[float, dict[str, float]]],
) -> dict[str, float]:
    result: defaultdict[str, float] = defaultdict(float)
    total_weight = 0.0
    for holding_weight, exposure in holdings:
        if holding_weight < 0:
            raise ValueError("holding weights must be non-negative")
        if abs(sum(exposure.values()) - 1.0) > 1e-6:
            raise ValueError("each exposure map must sum to one")
        total_weight += holding_weight
        for label, weight in exposure.items():
            result[label] += holding_weight * weight
    if abs(total_weight - 1.0) > 1e-6:
        raise ValueError("holding weights must sum to one")
    return dict(sorted(((label, round(weight, 10)) for label, weight in result.items())))


def scenario_loss(weights: Iterable[float], shocks: Iterable[float]) -> float:
    weight_values = [float(value) for value in weights]
    shock_values = [float(value) for value in shocks]
    if len(weight_values) != len(shock_values) or not weight_values:
        raise ValueError("weights and shocks must have the same non-zero length")
    if abs(sum(weight_values) - 1.0) > 1e-6:
        raise ValueError("weights must sum to one")
    if any(weight < 0 for weight in weight_values):
        raise ValueError("weights must be non-negative")
    if any(shock < -1.0 or not math.isfinite(shock) for shock in shock_values):
        raise ValueError("shocks must be finite and no lower than -100%")
    return sum(weight * shock for weight, shock in zip(weight_values, shock_values, strict=True))


def selected_financial_ratios(
    revenue_current: float,
    revenue_previous: float,
    component_revenue: float,
) -> dict[str, float]:
    if revenue_current <= 0 or revenue_previous <= 0 or component_revenue < 0:
        raise ValueError("revenues must be positive; component revenue cannot be negative")
    if component_revenue > revenue_current:
        raise ValueError("component revenue cannot exceed total revenue")
    return {
        "revenue_growth": revenue_current / revenue_previous - 1.0,
        "component_share": component_revenue / revenue_current,
    }


def normalize_comparison(
    rows: dict[str, dict[str, float]],
    lower_is_better: set[str] | None = None,
) -> dict[str, dict[str, float]]:
    """Min-max normalize metrics for visual comparison, not product ranking."""
    if not rows:
        return {}
    lower_is_better = lower_is_better or set()
    metrics = set.intersection(*(set(values) for values in rows.values()))
    output = {item_id: {} for item_id in rows}
    for metric in sorted(metrics):
        values = [rows[item_id][metric] for item_id in rows]
        minimum, maximum = min(values), max(values)
        for item_id, item_metrics in rows.items():
            if maximum == minimum:
                score = 0.5
            else:
                score = (item_metrics[metric] - minimum) / (maximum - minimum)
            if metric in lower_is_better:
                score = 1.0 - score
            output[item_id][metric] = round(score, 6)
    return output
