from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from .catalog import DeviceCatalog,DeviceModel,DeviceVariant
class EvidenceState(str,Enum):
    CONFIRMED="confirmed"; VERIFIED="verified"; REPORTED="reported"; ESTIMATED="estimated"; UNKNOWN="unknown"; NOT_AVAILABLE="not_available"
@dataclass(frozen=True)
class IdentifiedField:
    value:str|int|bool|None; state:EvidenceState; source:str=""
    @property
    def confirmed(self)->bool:return self.state in (EvidenceState.CONFIRMED,EvidenceState.VERIFIED)
    @property
    def verified(self)->bool:return self.state==EvidenceState.VERIFIED
@dataclass(frozen=True)
class DeviceIdentity:
    model:IdentifiedField
    variant:IdentifiedField=IdentifiedField(None,EvidenceState.UNKNOWN); ram_gb:IdentifiedField=IdentifiedField(None,EvidenceState.UNKNOWN); storage_gb:IdentifiedField=IdentifiedField(None,EvidenceState.UNKNOWN); imei:IdentifiedField=IdentifiedField(None,EvidenceState.UNKNOWN); carrier:IdentifiedField=IdentifiedField(None,EvidenceState.UNKNOWN); functional_test:IdentifiedField=IdentifiedField(None,EvidenceState.UNKNOWN)
    @property
    def incomplete_fields(self)->tuple[str,...]:return tuple(n for n,f in (("modelo exacto",self.model),("variante",self.variant),("RAM",self.ram_gb),("almacenamiento",self.storage_gb),("IMEI",self.imei),("operador/red",self.carrier),("prueba funcional",self.functional_test)) if not f.confirmed)
@dataclass(frozen=True)
class IdentificationCandidate:
    model:DeviceModel; confidence:float; source:str
def identify_by_search(catalog:DeviceCatalog,query:str)->list[IdentificationCandidate]:return [IdentificationCandidate(m,1.0,"catalog_search") for m in catalog.search(query)]
def identify_by_visual_candidate(catalog:DeviceCatalog,model_id:str,confidence:float,source:str="visual")->IdentificationCandidate:
    model=catalog.get(model_id)
    if model is None:raise ValueError("El modelo candidato no existe en el catálogo.")
    if not 0<=confidence<=1:raise ValueError("La confianza visual debe estar entre 0 y 1.")
    return IdentificationCandidate(model,confidence,source)
def identity_from_candidate(candidate:IdentificationCandidate)->DeviceIdentity:
    return DeviceIdentity(IdentifiedField(candidate.model.name,EvidenceState.CONFIRMED if candidate.confidence>=1 else EvidenceState.ESTIMATED,candidate.source))
def identity_from_variant(model:DeviceModel,variant:DeviceVariant|None=None,*,ram_gb:int|None=None,storage_gb:int|None=None,imei:str|None=None,imei_verified:bool=False,imei_reported:bool=False,carrier:str|None=None,functional_test_completed:bool=False)->DeviceIdentity:
    vf=IdentifiedField(variant.model_number,EvidenceState.CONFIRMED,"manual") if variant and variant.model_number else IdentifiedField(None,EvidenceState.UNKNOWN)
    ist=EvidenceState.REPORTED if imei and imei_reported else EvidenceState.VERIFIED if imei and imei_verified else EvidenceState.CONFIRMED if imei else EvidenceState.UNKNOWN
    return DeviceIdentity(IdentifiedField(model.name,EvidenceState.CONFIRMED,"catalog"),vf,IdentifiedField(ram_gb,EvidenceState.CONFIRMED,"manual") if ram_gb is not None else IdentifiedField(None,EvidenceState.UNKNOWN),IdentifiedField(storage_gb,EvidenceState.CONFIRMED,"manual") if storage_gb is not None else IdentifiedField(None,EvidenceState.UNKNOWN),IdentifiedField(imei,ist,"verification" if (imei_verified or imei_reported) else "manual"),IdentifiedField(carrier,EvidenceState.CONFIRMED,"manual") if carrier else IdentifiedField(None,EvidenceState.UNKNOWN),IdentifiedField(True,EvidenceState.CONFIRMED,"test") if functional_test_completed else IdentifiedField(None,EvidenceState.UNKNOWN))
