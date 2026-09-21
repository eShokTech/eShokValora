from datetime import date, timedelta

from app.core.calculator import calculate_valuation
from app.core.engine import ValuationRequest, value_device
from app.core.models import Condition, MarketObservation, PriceSource, ValuationInput


def observations():
    today = date(2026, 9, 21)
    return tuple(
        MarketObservation(
            device_key="samsung|s22 ultra|256gb",
            condition=Condition.WORKING,
            price=float(price),
            observed_on=today - timedelta(days=i * 10),
            source=PriceSource.MARKETPLACE,
            confidence=1.0,
        )
        for i, price in enumerate((5000, 5100, 4900, 5200, 5050))
    )


def test_market_drives_maximum_purchase():
    result = value_device(
        ValuationRequest(
            observations=observations(),
            condition=Condition.WORKING,
            repair_cost=1000,
            desired_profit=1000,
        )
    )

    assert result.market.price > 4900
    assert result.valuation.maximum_purchase_price < result.market.price
    assert result.valuation.expected_profit_at_max == 1000.0


def test_margin_goal_is_respected():
    result = calculate_valuation(
        ValuationInput(
            market_price=5000,
            repair_cost=1000,
            desired_profit=200,
            desired_margin_percent=30,
        )
    )

    assert result.maximum_purchase_price == 2500
    assert result.expected_profit_at_max == 1500


def test_negative_purchase_is_not_viable():
    result = calculate_valuation(
        ValuationInput(
            market_price=2000,
            repair_cost=1500,
            risk_reserve=500,
            desired_profit=500,
        )
    )

    assert result.maximum_purchase_price == 0
    assert result.viable is False
