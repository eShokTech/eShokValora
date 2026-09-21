from app.core.catalog import demo_catalog
from app.core.identification import EvidenceState,identify_by_visual_candidate,identity_from_candidate,identity_from_variant
def test_visual_candidate_is_not_confirmed():
    candidate=identify_by_visual_candidate(demo_catalog(),"samsung-s22-ultra",.82)
    identity=identity_from_candidate(candidate)
    assert identity.model.state==EvidenceState.ESTIMATED and not identity.model.confirmed
def test_imei_requires_verification():
    model=demo_catalog().get("apple-iphone-11"); assert model
    entered=identity_from_variant(model,imei="123456789012345")
    verified=identity_from_variant(model,imei="123456789012345",imei_verified=True)
    assert entered.imei.state==EvidenceState.CONFIRMED and not entered.imei.verified
    assert verified.imei.state==EvidenceState.VERIFIED
