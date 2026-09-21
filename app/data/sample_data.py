from __future__ import annotations

from datetime import date, timedelta

from app.core.models import Condition, Device, MarketObservation, PriceSource


def sample_s22_ultra_observations() -> tuple[Device, tuple[MarketObservation, ...]]:
    device = Device("Samsung", "S22 Ultra", storage_gb=256, year=2022)
    today = date.today()
    prices = (5200, 5000, 5100, 4800, 5500, 4950, 5300, 5050)

    observations = tuple(
        MarketObservation(
            device_key=device.key,
            condition=Condition.WORKING,
            price=float(price),
            observed_on=today - timedelta(days=index * 9),
            source=PriceSource.MARKETPLACE,
            sample_note="Dato de demostración",
            city="Reynosa",
            sold=False,
            confidence=0.9,
        )
        for index, price in enumerate(prices)
    )
    return device, observations
