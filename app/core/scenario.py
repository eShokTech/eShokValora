from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from .catalog import DeviceModel,DeviceVariant
from .uncertainty import possible_variants
@dataclass(frozen=True)
class VariantConfiguration:
    variant:DeviceVariant;ram_gb:int|None;storage_gb:int|None
@dataclass(frozen=True)
class VariantScenario:
    candidates:tuple[VariantConfiguration,...];conservative:VariantConfiguration|None;reason:str
    @property
    def ambiguous(self)->bool:return len(self.candidates)>1
def build_variant_scenario(model:DeviceModel,*,model_number:str|None=None,ram_gb:int|None=None,storage_gb:int|None=None)->VariantScenario:
    variants=possible_variants(model,model_number=model_number,ram_gb=ram_gb,storage_gb=storage_gb)
    candidates=[]
    for v in variants:
        rams=(ram_gb,) if ram_gb is not None else (v.ram_options_gb or (None,))
        storages=(storage_gb,) if storage_gb is not None else (v.storage_options_gb or (None,))
        candidates.extend(VariantConfiguration(v,r,s) for r,s in product(rams,storages))
    conservative=min(candidates,key=lambda c:(c.storage_gb or 0,c.ram_gb or 0,c.variant.model_number)) if candidates else None
    if not candidates:reason="No hay variantes suficientes en el catálogo para acotar el escenario."
    elif len(candidates)==1:reason="La información disponible deja una sola configuración plausible."
    else:reason="Existen varias configuraciones plausibles; se conserva la de menor capacidad y RAM conocidas."
    return VariantScenario(tuple(candidates),conservative,reason)
