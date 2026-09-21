from __future__ import annotations
from dataclasses import dataclass,field
@dataclass(frozen=True)
class DeviceVariant:
    model_id:str;model_number:str="";ram_options_gb:tuple[int,...]=();storage_options_gb:tuple[int,...]=();aliases:tuple[str,...]=();region:str="";active:bool=True
@dataclass(frozen=True)
class DeviceModel:
    id:str;brand:str;name:str;year:int|None=None;aliases:tuple[str,...]=();variants:tuple[DeviceVariant,...]=();active:bool=True
@dataclass(frozen=True)
class DeviceCatalog:
    models:tuple[DeviceModel,...]=field(default_factory=tuple)
    def brands(self)->list[str]:return sorted({m.brand for m in self.models if m.active})
    def models_for_brand(self,brand:str)->list[DeviceModel]:
        key=brand.strip().casefold();return [m for m in self.models if m.active and m.brand.casefold()==key]
    def search(self,query:str,limit:int=12)->list[DeviceModel]:
        q=query.strip().casefold()
        if not q:return []
        scored=[]
        for m in self.models:
            if not m.active:continue
            variant_terms=tuple(x for v in m.variants for x in (v.model_number,*v.aliases) if x)
            hay=" ".join((m.brand,m.name,*m.aliases,*variant_terms)).casefold()
            if q==m.name.casefold():score=100
            elif any(q==x.casefold() for x in variant_terms):score=98
            elif m.name.casefold().startswith(q):score=80
            elif q in hay:score=60
            else:continue
            scored.append((score,m))
        scored.sort(key=lambda x:(-x[0],x[1].brand,x[1].name));return [m for _,m in scored[:limit]]
    def get(self,model_id:str)->DeviceModel|None:return next((m for m in self.models if m.id==model_id),None)
def demo_catalog()->DeviceCatalog:
    return DeviceCatalog(models=(
        DeviceModel("samsung-s22-ultra","Samsung","Galaxy S22 Ultra",2022,("S22 Ultra","S22U"),(DeviceVariant("samsung-s22-ultra","SM-S908U",(8,12),(128,256,512),("S908U",),"US"),DeviceVariant("samsung-s22-ultra","SM-S908B",(8,12),(128,256,512),("S908B",),"Global"))),
        DeviceModel("motorola-moto-g65","Motorola","Moto G65",None,("Moto G65 5G","G65"),(DeviceVariant("motorola-moto-g65","",(4,8),(128,256),("XT-G65",)),)),
        DeviceModel("apple-iphone-11","Apple","iPhone 11",2019,("iPhone11",)),DeviceModel("xiaomi-redmi-note-13","Xiaomi","Redmi Note 13",2024,("Note 13",)),DeviceModel("huawei-pura-70","Huawei","Pura 70",2024)
    ))
