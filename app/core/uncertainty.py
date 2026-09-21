from __future__ import annotations
from dataclasses import dataclass
from .catalog import DeviceModel,DeviceVariant
@dataclass(frozen=True)
class UncertaintyItem:
    field:str; reason:str; penalty_rate:float; fixed_penalty:float=0.0; critical:bool=False
@dataclass(frozen=True)
class UncertaintyAssessment:
    reserve:float; score:float; level:str; items:tuple[UncertaintyItem,...]
    @property
    def reasons(self)->tuple[str,...]: return tuple(i.reason for i in self.items)
def assess_uncertainty(*,market_price:float,model_confirmed:bool=True,exact_variant_confirmed:bool=False,ram_confirmed:bool=False,storage_confirmed:bool=False,imei_verified:bool=False,carrier_confirmed:bool=True,functional_test_completed:bool=False)->UncertaintyAssessment:
    if market_price<=0: raise ValueError("El precio de mercado debe ser mayor que cero.")
    items=[]
    if not model_confirmed: items.append(UncertaintyItem("modelo","El modelo es estimado, no confirmado.",.08,critical=True))
    if not exact_variant_confirmed: items.append(UncertaintyItem("variante","La variante exacta no está confirmada; se protege contra el escenario inferior.",.04))
    if not ram_confirmed: items.append(UncertaintyItem("RAM","La RAM es desconocida; se protege contra una variante inferior.",.03))
    if not storage_confirmed: items.append(UncertaintyItem("almacenamiento","El almacenamiento es desconocido; se protege contra una variante inferior.",.05))
    if not imei_verified: items.append(UncertaintyItem("IMEI","El IMEI no está verificado; existe riesgo de reporte, blacklist o imposibilidad de venta.",.10,critical=True))
    if not carrier_confirmed: items.append(UncertaintyItem("red/operador","El operador o bloqueo de red no está confirmado.",.05))
    if not functional_test_completed: items.append(UncertaintyItem("pruebas","El funcionamiento completo no ha sido comprobado.",.04))
    score=min(100,sum(i.penalty_rate*100 for i in items)); level="low" if score<15 else "medium" if score<30 else "high"
    reserve=market_price*min(.35,sum(i.penalty_rate for i in items))
    if any(i.critical for i in items): reserve+=market_price*.03
    return UncertaintyAssessment(round(min(reserve,market_price*.40),2),round(score,2),level,tuple(items))
def possible_variants(model:DeviceModel,*,model_number:str|None=None,ram_gb:int|None=None,storage_gb:int|None=None)->tuple[DeviceVariant,...]:
    variants=[v for v in model.variants if v.active]
    if model_number:
        n=model_number.strip().casefold(); variants=[v for v in variants if n==v.model_number.casefold() or n in {a.casefold() for a in v.aliases}]
    if ram_gb is not None: variants=[v for v in variants if ram_gb in v.ram_options_gb]
    if storage_gb is not None: variants=[v for v in variants if storage_gb in v.storage_options_gb]
    return tuple(variants)
def conservative_variant(variants:tuple[DeviceVariant,...])->DeviceVariant|None:
    return min(variants,key=lambda v:(min(v.storage_options_gb) if v.storage_options_gb else 0,min(v.ram_options_gb) if v.ram_options_gb else 0,v.model_number)) if variants else None
