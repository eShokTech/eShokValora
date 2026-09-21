from datetime import date
from app.core.engine import ValuationRequest,value_device
from app.core.identification import identity_from_variant
from app.core.catalog import demo_catalog
from app.core.models import Condition,MarketObservation,PriceSource

def test_unverified_imei_reduces_purchase_ceiling():
    observations=tuple(MarketObservation("x",Condition.WORKING,p,date(2026,9,21),PriceSource.MARKETPLACE) for p in (5000,5100,4900))
    model=demo_catalog().get("apple-iphone-11"); assert model
    identity=identity_from_variant(model,imei="123456789012345")
    clean=identity_from_variant(model,imei="123456789012345",imei_verified=True,carrier="Telcel",functional_test_completed=True)
    a=value_device(ValuationRequest(observations,Condition.WORKING,repair_cost=500,desired_profit=500,identity=identity))
    b=value_device(ValuationRequest(observations,Condition.WORKING,repair_cost=500,desired_profit=500,identity=clean))
    assert a.uncertainty.reserve>b.uncertainty.reserve
    assert a.valuation.maximum_purchase_price<b.valuation.maximum_purchase_price
