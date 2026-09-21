from app.core.catalog import demo_catalog
from app.core.scenario import build_variant_scenario
def test_unknown_storage_keeps_multiple_configurations():
    model=demo_catalog().get("samsung-s22-ultra");assert model
    scenario=build_variant_scenario(model,model_number="SM-S908U",ram_gb=8)
    assert len(scenario.candidates)==3
    assert scenario.conservative and scenario.conservative.storage_gb==128
def test_exact_storage_reduces_scenario():
    model=demo_catalog().get("samsung-s22-ultra");assert model
    scenario=build_variant_scenario(model,model_number="SM-S908U",ram_gb=8,storage_gb=256)
    assert len(scenario.candidates)==1 and scenario.candidates[0].storage_gb==256
