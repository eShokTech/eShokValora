from __future__ import annotations
from dataclasses import dataclass
from .calculator import calculate_valuation
from .identification import DeviceIdentity
from .market import MarketType,estimate_market
from .models import Condition,MarketEstimate,MarketObservation,ValuationInput,ValuationResult
from .risk import RiskAssessment,assess_risk
from .uncertainty import UncertaintyAssessment,assess_uncertainty
@dataclass(frozen=True)
class ValuationRequest:
    observations:tuple[MarketObservation,...]
    condition:Condition
    market_type:MarketType=MarketType.SECOND_LIFE
    repair_cost:float=0.0
    selling_cost:float=0.0
    other_cost:float=0.0
    desired_profit:float=0.0
    desired_margin_percent:float|None=None
    known_faults:int=0
    unknown_faults:bool=False
    repair_complexity:float=0.0
    recommendation_buffer:float=0.0
    identity:DeviceIdentity|None=None
@dataclass(frozen=True)
class ValuationEngineResult:
    market:MarketEstimate
    risk:RiskAssessment
    uncertainty:UncertaintyAssessment
    valuation:ValuationResult

def value_device(request:ValuationRequest)->ValuationEngineResult:
    market=estimate_market(request.observations,condition=request.condition,market_type=request.market_type)
    risk=assess_risk(repair_cost=request.repair_cost,market_price=market.price,known_faults=request.known_faults,unknown_faults=request.unknown_faults,repair_complexity=request.repair_complexity)
    identity=request.identity
    uncertainty=assess_uncertainty(
        market_price=market.price,
        model_confirmed=identity is None or identity.model.confirmed,
        exact_variant_confirmed=identity is None or identity.variant.confirmed,
        ram_confirmed=identity is None or identity.ram_gb.confirmed,
        storage_confirmed=identity is None or identity.storage_gb.confirmed,
        imei_verified=identity is None or identity.imei.verified,
        carrier_confirmed=identity is None or identity.carrier.confirmed,
        functional_test_completed=identity is None or identity.functional_test.confirmed,
    )
    valuation=calculate_valuation(ValuationInput(market_price=market.price,repair_cost=request.repair_cost,risk_reserve=risk.reserve+uncertainty.reserve,selling_cost=request.selling_cost,other_cost=request.other_cost,desired_profit=request.desired_profit,desired_margin_percent=request.desired_margin_percent,recommendation_buffer=request.recommendation_buffer))
    return ValuationEngineResult(market,risk,uncertainty,valuation)
