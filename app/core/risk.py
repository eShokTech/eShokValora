from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskAssessment:
    reserve: float
    level: str
    score: float
    reasons: tuple[str, ...]


def assess_risk(
    *,
    repair_cost: float,
    market_price: float,
    known_faults: int = 0,
    unknown_faults: bool = False,
    repair_complexity: float = 0.0,
) -> RiskAssessment:
    if market_price <= 0:
        raise ValueError("El precio de mercado debe ser mayor que cero.")

    repair_ratio = max(0.0, repair_cost) / market_price
    score = min(100.0, repair_ratio * 55.0 + known_faults * 7.0 + repair_complexity * 20.0)
    if unknown_faults:
        score += 18.0
    score = min(100.0, score)

    if score < 25:
        level = "low"
    elif score < 55:
        level = "medium"
    else:
        level = "high"

    # Reserva base para absorber desviaciones de reparación.
    reserve_rate = {"low": 0.03, "medium": 0.07, "high": 0.12}[level]
    reserve = max(0.0, market_price * reserve_rate)

    reasons: list[str] = []
    if repair_ratio >= 0.35:
        reasons.append("La reparación representa una parte importante del valor de reventa.")
    if known_faults >= 2:
        reasons.append("Hay múltiples fallas conocidas.")
    if unknown_faults:
        reasons.append("Existen fallas no confirmadas.")
    if repair_complexity >= 0.6:
        reasons.append("La reparación tiene complejidad elevada.")

    return RiskAssessment(
        reserve=round(reserve, 2),
        level=level,
        score=round(score, 2),
        reasons=tuple(reasons),
    )
