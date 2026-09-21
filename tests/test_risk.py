from app.core.risk import assess_risk


def test_high_risk_reserve_is_higher():
    low = assess_risk(repair_cost=200, market_price=5000)
    high = assess_risk(
        repair_cost=2500,
        market_price=5000,
        known_faults=3,
        unknown_faults=True,
        repair_complexity=1.0,
    )

    assert high.reserve > low.reserve
    assert high.level == "high"
