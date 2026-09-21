from __future__ import annotations

from collections import defaultdict
from datetime import date
from enum import Enum
from statistics import median
from typing import Iterable

from .models import Condition, MarketEstimate, MarketObservation


class MarketType(str, Enum):
    SECOND_LIFE = "second_life"
    QUICK_SALE = "quick_sale"
    REFURBISHED_SALE = "refurbished_sale"
    NEW = "new"


def _recency_weight(observed_on: date, today: date) -> float:
    days = max(0, (today - observed_on).days)
    return 0.5 ** (days / 180.0)


def estimate_market(observations: Iterable[MarketObservation], *, condition: Condition, market_type: MarketType = MarketType.SECOND_LIFE, today: date | None = None) -> MarketEstimate:
    today = today or date.today()
    matching = [item for item in observations if item.condition == condition and item.market_type == market_type.value and item.price > 0]
    if not matching:
        raise ValueError("No existen observaciones para esa condición y tipo de mercado.")
    values = [item.price for item in matching]
    central = median(values)
    weighted_values = []
    for item in matching:
        weight = _recency_weight(item.observed_on, today) * item.confidence
        weighted_values.append((item.price, max(weight, 0.05)))
    weight_sum = sum(weight for _, weight in weighted_values)
    recent_price = sum(price * weight for price, weight in weighted_values) / weight_sum
    estimate = (central * 0.70) + (recent_price * 0.30)
    ordered = sorted(values)
    low = ordered[max(0, int(len(ordered) * 0.15))]
    high = ordered[min(len(ordered) - 1, int(len(ordered) * 0.85))]
    average_confidence = sum(item.confidence for item in matching) / len(matching)
    quantity_factor = min(1.0, len(matching) / 12.0)
    confidence = round(average_confidence * (0.35 + 0.65 * quantity_factor), 3)
    return MarketEstimate(round(estimate, 2), round(low, 2), round(high, 2), len(matching), confidence, condition, market_type.value)


def group_by_condition(observations: Iterable[MarketObservation]) -> dict[Condition, list[MarketObservation]]:
    grouped: dict[Condition, list[MarketObservation]] = defaultdict(list)
    for item in observations:
        grouped[item.condition].append(item)
    return dict(grouped)
