from app.core.uncertainty import assess_uncertainty


def test_missing_imei_increases_reserve():
    complete = assess_uncertainty(
        market_price=5000,
        model_confirmed=True,
        exact_variant_confirmed=True,
        ram_confirmed=True,
        storage_confirmed=True,
        imei_verified=True,
        carrier_confirmed=True,
        functional_test_completed=True,
    )
    incomplete = assess_uncertainty(market_price=5000, model_confirmed=False, imei_verified=False)
    assert incomplete.reserve > complete.reserve


def test_unknown_storage_is_explicit():
    result = assess_uncertainty(market_price=5000, storage_confirmed=False)
    assert any(item.field == "almacenamiento" for item in result.items)
