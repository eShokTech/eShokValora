from __future__ import annotations

from dataclasses import dataclass

from .calculator import calculate_valuation
from .market import estimate_market
from .models import Condition, MarketEstimate, MarketObservation, ValuationInput, ValuationResult
from .risk import RiskAssessment, assess_risk


@dataclass(frozen=True)
class ValuationRequest:
    observations: tuple[MarketObservation, ...]
    condition: Condition
    repair_cost: float = 0.0
    selling_cost: float = 0.0
    other_cost: float = 0.0
    desired_profit: float = 0.0
    desired_margin_percent: float | None = None
    known_faults: int = 0
    unknown_faults: bool = False
    repair_complexity: float = 0.0
    recommendation_buffer: float = 0.0


@dataclass(frozen=True)
class ValuationEngineResult:
    market: MarketEstimate
    risk: RiskAssessment
    valuation: ValuationResult


def value_device(request: ValuationRequest) -> ValuationEngineResult:
    market = estimate_market(
        request.observations,
        condition=request.condition,
    )
    risk = assess_risk(
        repair_cost=request.repair_cost,
        market_price=market.price,
        known_faults=request.known_faults,
        unknown_faults=request.unknown_faults,
        repair_complexity=request.repair_complexity,
    )
    valuation = calculate_valuation(
        ValuationInput(
            market_price=market.price,
            repair_cost=request.repair_cost,
            risk_reserve=risk.reserve,
            selling_cost=request.selling_cost,
            other_cost=request.other_cost,
            desired_profit=request.desired_profit,
            desired_margin_percent=request.desired_margin_percent,
            recommendation_buffer=request.recommendation_buffer,
        )
    )
    return ValuationEngineResult(
        market=market,
        risk=risk,
        valuation=valuation,
    )
