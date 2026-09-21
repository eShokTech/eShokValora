from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .catalog import DeviceCatalog, DeviceModel, DeviceVariant


class EvidenceState(str, Enum):
    CONFIRMED = "confirmed"
    ESTIMATED = "estimated"
    UNKNOWN = "unknown"
    NOT_AVAILABLE = "not_available"


@dataclass(frozen=True)
class IdentifiedField:
    value: str | int | None
    state: EvidenceState
    source: str = ""

    @property
    def confirmed(self) -> bool:
        return self.state == EvidenceState.CONFIRMED


@dataclass(frozen=True)
class DeviceIdentity:
    model: IdentifiedField
    variant: IdentifiedField = IdentifiedField(None, EvidenceState.UNKNOWN)
    ram_gb: IdentifiedField = IdentifiedField(None, EvidenceState.UNKNOWN)
    storage_gb: IdentifiedField = IdentifiedField(None, EvidenceState.UNKNOWN)
    imei: IdentifiedField = IdentifiedField(None, EvidenceState.UNKNOWN)

    @property
    def incomplete_fields(self) -> tuple[str, ...]:
        return tuple(
            name for name, field in (
                ("modelo exacto", self.model),
                ("variante", self.variant),
                ("RAM", self.ram_gb),
                ("almacenamiento", self.storage_gb),
                ("IMEI", self.imei),
            )
            if field.state not in (EvidenceState.CONFIRMED,)
        )


@dataclass(frozen=True)
class IdentificationCandidate:
    model: DeviceModel
    confidence: float
    source: str


def identify_by_search(catalog: DeviceCatalog, query: str) -> list[IdentificationCandidate]:
    return [
        IdentificationCandidate(model=m, confidence=1.0, source="catalog_search")
        for m in catalog.search(query)
    ]


def identify_by_visual_candidate(
    catalog: DeviceCatalog,
    model_id: str,
    confidence: float,
    source: str = "visual",
) -> IdentificationCandidate:
    model = catalog.get(model_id)
    if model is None:
        raise ValueError("El modelo candidato no existe en el catálogo.")
    if not 0 <= confidence <= 1:
        raise ValueError("La confianza visual debe estar entre 0 y 1.")
    return IdentificationCandidate(model=model, confidence=confidence, source=source)


def identity_from_variant(
    model: DeviceModel,
    variant: DeviceVariant | None = None,
    *,
    ram_gb: int | None = None,
    storage_gb: int | None = None,
    imei: str | None = None,
) -> DeviceIdentity:
    variant_field = (
        IdentifiedField(variant.model_number, EvidenceState.CONFIRMED, "manual")
        if variant and variant.model_number
        else IdentifiedField(None, EvidenceState.UNKNOWN)
    )
    return DeviceIdentity(
        model=IdentifiedField(model.name, EvidenceState.CONFIRMED, "catalog"),
        variant=variant_field,
        ram_gb=IdentifiedField(ram_gb, EvidenceState.CONFIRMED, "manual") if ram_gb else IdentifiedField(None, EvidenceState.UNKNOWN),
        storage_gb=IdentifiedField(storage_gb, EvidenceState.CONFIRMED, "manual") if storage_gb else IdentifiedField(None, EvidenceState.UNKNOWN),
        imei=IdentifiedField(imei, EvidenceState.CONFIRMED, "manual") if imei else IdentifiedField(None, EvidenceState.UNKNOWN),
    )
