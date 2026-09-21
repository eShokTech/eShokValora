from datetime import date
from app.core.catalog import demo_catalog
from app.core.engine import ValuationRequest,value_device
from app.core.identification import identity_from_variant
from app.core.models import Condition,MarketObservation,PriceSource
def test_reported_imei_blocks_purchase_value():
    observations=tuple(MarketObservation("x",Condition.WORKING,p,date(2026,9,21),PriceSource.MARKETPLACE) for p in (5000,5100,4900))
    model=demo_catalog().get("apple-iphone-11");assert model
    identity=identity_from_variant(model,imei="123456789012345",imei_reported=True)
    result=value_device(ValuationRequest(observations,Condition.WORKING,repair_cost=500,desired_profit=500,identity=identity))
    assert result.uncertainty.blocked
    assert result.valuation.maximum_purchase_price==0
