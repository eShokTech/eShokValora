from app.core.catalog import demo_catalog
from app.core.identification import identify_by_search


def test_search_finds_model_by_alias():
    results = identify_by_search(demo_catalog(), "S22 Ultra")
    assert results
    assert results[0].model.name == "Galaxy S22 Ultra"


def test_brand_filters_models():
    catalog = demo_catalog()
    models = catalog.models_for_brand("Motorola")
    assert models
    assert all(model.brand == "Motorola" for model in models)
