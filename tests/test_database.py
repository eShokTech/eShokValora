from datetime import date
from app.core.catalog import demo_catalog
from app.core.market import MarketType
from app.core.models import Condition,MarketObservation,PriceSource
from app.data.database import Database

def test_database_persists_catalog_and_market_type(tmp_path):
    db=Database(tmp_path/"valora.db"); db.initialize(); model=demo_catalog().get("samsung-s22-ultra"); assert model
    db.add_device_model(model)
    loaded=db.list_device_models("Samsung")
    assert loaded[0].name=="Galaxy S22 Ultra" and loaded[0].variants
    db.add_observation(MarketObservation("samsung|s22",Condition.WORKING,5000,date(2026,9,21),PriceSource.MARKETPLACE,market_type=MarketType.SECOND_LIFE.value))
    rows=db.list_observations("samsung|s22")
    assert rows[0].market_type==MarketType.SECOND_LIFE.value
