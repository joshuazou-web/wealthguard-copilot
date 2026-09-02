from __future__ import annotations

from decimal import Decimal

import pytest
from wealthguard import calculations


def test_period_and_annualized_return() -> None:
    prices = [100, 105, 110]
    assert calculations.period_return(prices) == pytest.approx(0.10)
    assert calculations.annualized_return(prices, periods_per_year=2) == pytest.approx(0.10)


def test_volatility_is_zero_for_constant_returns() -> None:
    assert calculations.annualized_volatility([100, 110, 121], 2) == pytest.approx(0.0)


def test_maximum_drawdown() -> None:
    assert calculations.maximum_drawdown([100, 120, 90, 95]) == pytest.approx(-0.25)


def test_invalid_prices_rejected() -> None:
    with pytest.raises(ValueError):
        calculations.period_return([100])
    with pytest.raises(ValueError):
        calculations.period_return([100, 0])


def test_fee_impact_uses_decimal_money_rounding() -> None:
    result = calculations.fee_impact(Decimal("10000"), Decimal("0.05"), Decimal("0.01"), 10)
    assert result["without_fees"] == 16288.95
    assert result["with_fees"] == 14802.44
    assert result["fee_drag"] == 1486.50


def test_concentration_and_exposure() -> None:
    concentration = calculations.concentration_ratio([0.5, 0.3, 0.2])
    assert concentration["largest_position"] == 0.5
    assert concentration["herfindahl_index"] == pytest.approx(0.38)
    exposure = calculations.aggregate_exposure([(0.5, {"Tech": 1.0}), (0.5, {"Tech": 0.2, "Bond": 0.8})])
    assert exposure == {"Bond": 0.4, "Tech": 0.6}


def test_scenario_and_ratios() -> None:
    assert calculations.scenario_loss([0.6, 0.4], [-0.1, -0.02]) == pytest.approx(-0.068)
    ratios = calculations.selected_financial_ratios(120, 100, 30)
    assert ratios == pytest.approx({"revenue_growth": 0.2, "component_share": 0.25})


def test_comparison_normalization_does_not_rank_products() -> None:
    result = calculations.normalize_comparison(
        {"A": {"risk": 5, "return": 8}, "B": {"risk": 2, "return": 4}},
        lower_is_better={"risk"},
    )
    assert result["A"] == {"return": 1.0, "risk": 0.0}
    assert result["B"] == {"return": 0.0, "risk": 1.0}
