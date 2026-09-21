from app.core.catalog import demo_catalog
from app.data.catalog_io import load_catalog,save_catalog
def test_catalog_round_trip(tmp_path):
    path=tmp_path/"catalog.json";save_catalog(demo_catalog(),path);loaded=load_catalog(path)
    model=loaded.get("samsung-s22-ultra")
    assert model and len(model.variants)==2 and model.variants[0].ram_options_gb
