from datetime import date
from app.core.market import MarketType,estimate_market
from app.core.models import Condition,MarketObservation,PriceSource
def test_market_defaults_to_second_life():
    observations=(MarketObservation("x",Condition.WORKING,5000,date(2026,9,1),PriceSource.MARKETPLACE),MarketObservation("x",Condition.WORKING,8000,date(2026,9,1),PriceSource.OTHER,market_type=MarketType.NEW.value))
    estimate=estimate_market(observations,condition=Condition.WORKING,today=date(2026,9,10))
    assert estimate.price==5000 and estimate.market_type==MarketType.SECOND_LIFE.value
