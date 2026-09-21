from __future__ import annotations
import json
from pathlib import Path
from app.core.catalog import DeviceCatalog,DeviceModel,DeviceVariant

def catalog_from_dict(data:dict)->DeviceCatalog:
    models=[]
    for item in data.get("models",[]):
        variants=tuple(DeviceVariant(model_id=item["id"],model_number=v.get("model_number",""),ram_options_gb=tuple(v.get("ram_options_gb",())),storage_options_gb=tuple(v.get("storage_options_gb",())),aliases=tuple(v.get("aliases",())),region=v.get("region",""),active=v.get("active",True)) for v in item.get("variants",()))
        models.append(DeviceModel(id=item["id"],brand=item["brand"],name=item["name"],year=item.get("year"),aliases=tuple(item.get("aliases",())),variants=variants,active=item.get("active",True)))
    return DeviceCatalog(tuple(models))

def load_catalog(path:str|Path)->DeviceCatalog:
    source=Path(path)
    with source.open("r",encoding="utf-8") as handle:return catalog_from_dict(json.load(handle))

def save_catalog(catalog:DeviceCatalog,path:str|Path)->None:
    target=Path(path);target.parent.mkdir(parents=True,exist_ok=True)
    payload={"models":[{"id":m.id,"brand":m.brand,"name":m.name,"year":m.year,"aliases":list(m.aliases),"active":m.active,"variants":[{"model_number":v.model_number,"ram_options_gb":list(v.ram_options_gb),"storage_options_gb":list(v.storage_options_gb),"aliases":list(v.aliases),"region":v.region,"active":v.active} for v in m.variants]} for m in catalog.models]}
    target.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
