from __future__ import annotations

from collections import defaultdict
from datetime import date
from statistics import median
from typing import Iterable

from .models import Condition, MarketEstimate, MarketObservation


def _recency_weight(observed_on: date, today: date) -> float:
    days = max(0, (today - observed_on).days)
    # Decaimiento suave: 50% aproximadamente cada 180 días.
    return 0.5 ** (days / 180.0)


def estimate_market(
    observations: Iterable[MarketObservation],
    *,
    condition: Condition,
    today: date | None = None,
) -> MarketEstimate:
    today = today or date.today()

    matching = [
        item for item in observations
        if item.condition == condition and item.price > 0
    ]

    if not matching:
        raise ValueError("No existen observaciones para esa condición.")

    # El precio central usa mediana para resistir anuncios atípicos.
    values = [item.price for item in matching]
    central = median(values)

    weighted_values: list[tuple[float, float]] = []
    for item in matching:
        weight = _recency_weight(item.observed_on, today) * item.confidence
        weighted_values.append((item.price, max(weight, 0.05)))

    weight_sum = sum(weight for _, weight in weighted_values)
    recent_price = sum(price * weight for price, weight in weighted_values) / weight_sum

    # 70% del centro robusto + 30% de la señal reciente.
    estimate = (central * 0.70) + (recent_price * 0.30)

    ordered = sorted(values)
    low_index = max(0, int(len(ordered) * 0.15))
    high_index = min(len(ordered) - 1, int(len(ordered) * 0.85))
    low = ordered[low_index]
    high = ordered[high_index]

    average_confidence = sum(item.confidence for item in matching) / len(matching)
    quantity_factor = min(1.0, len(matching) / 12.0)
    confidence = round(average_confidence * (0.35 + 0.65 * quantity_factor), 3)

    return MarketEstimate(
        price=round(estimate, 2),
        low=round(low, 2),
        high=round(high, 2),
        sample_count=len(matching),
        confidence=confidence,
        condition=condition,
    )


def group_by_condition(
    observations: Iterable[MarketObservation],
) -> dict[Condition, list[MarketObservation]]:
    grouped: dict[Condition, list[MarketObservation]] = defaultdict(list)
    for item in observations:
        grouped[item.condition].append(item)
    return dict(grouped)
