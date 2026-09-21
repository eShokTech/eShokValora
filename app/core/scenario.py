from __future__ import annotations
from dataclasses import dataclass
from .catalog import DeviceModel,DeviceVariant
from .uncertainty import conservative_variant,possible_variants
@dataclass(frozen=True)
class VariantScenario:
    candidates:tuple[DeviceVariant,...]; conservative:DeviceVariant|None; reason:str
    @property
    def ambiguous(self)->bool: return len(self.candidates)>1
def build_variant_scenario(model:DeviceModel,*,model_number:str|None=None,ram_gb:int|None=None,storage_gb:int|None=None)->VariantScenario:
    candidates=possible_variants(model,model_number=model_number,ram_gb=ram_gb,storage_gb=storage_gb)
    conservative=conservative_variant(candidates)
    if not candidates: reason="No hay variantes suficientes en el catálogo para acotar el escenario."
    elif len(candidates)==1: reason="La información disponible deja una sola variante plausible."
    else: reason="Existen varias variantes plausibles; se conserva la configuración de menor valor conocida."
    return VariantScenario(candidates,conservative,reason)
