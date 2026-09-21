from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DeviceVariant:
    model_id: str
    model_number: str = ""
    ram_options_gb: tuple[int, ...] = ()
    storage_options_gb: tuple[int, ...] = ()
    aliases: tuple[str, ...] = ()
    region: str = ""
    active: bool = True


@dataclass(frozen=True)
class DeviceModel:
    id: str
    brand: str
    name: str
    year: int | None = None
    aliases: tuple[str, ...] = ()
    variants: tuple[DeviceVariant, ...] = ()
    active: bool = True


@dataclass(frozen=True)
class DeviceCatalog:
    models: tuple[DeviceModel, ...] = field(default_factory=tuple)

    def brands(self) -> list[str]:
        return sorted({m.brand for m in self.models if m.active})

    def models_for_brand(self, brand: str) -> list[DeviceModel]:
        key = brand.strip().casefold()
        return [m for m in self.models if m.active and m.brand.casefold() == key]

    def search(self, query: str, limit: int = 12) -> list[DeviceModel]:
        q = query.strip().casefold()
        if not q:
            return []
        scored: list[tuple[int, DeviceModel]] = []
        for model in self.models:
            if not model.active:
                continue
            hay = " ".join((model.brand, model.name, *model.aliases)).casefold()
            if q == model.name.casefold():
                score = 100
            elif model.name.casefold().startswith(q):
                score = 80
            elif q in hay:
                score = 60
            else:
                continue
            scored.append((score, model))
        scored.sort(key=lambda item: (-item[0], item[1].brand, item[1].name))
        return [model for _, model in scored[:limit]]

    def get(self, model_id: str) -> DeviceModel | None:
        return next((m for m in self.models if m.id == model_id), None)


def demo_catalog() -> DeviceCatalog:
    return DeviceCatalog(models=(
        DeviceModel(
            id="samsung-s22-ultra",
            brand="Samsung",
            name="Galaxy S22 Ultra",
            year=2022,
            aliases=("S22 Ultra", "S22U"),
            variants=(
                DeviceVariant("samsung-s22-ultra", "SM-S908U", (8, 12), (128, 256, 512), ("S908U",), "US"),
                DeviceVariant("samsung-s22-ultra", "SM-S908B", (8, 12), (128, 256, 512), ("S908B",), "Global"),
            ),
        ),
        DeviceModel(
            id="motorola-moto-g65",
            brand="Motorola",
            name="Moto G65",
            aliases=("Moto G65 5G", "G65"),
            variants=(
                DeviceVariant("motorola-moto-g65", "", (4, 8), (128, 256), ("XT-G65",)),
            ),
        ),
        DeviceModel(id="apple-iphone-11", brand="Apple", name="iPhone 11", year=2019, aliases=("iPhone11",)),
        DeviceModel(id="xiaomi-redmi-note-13", brand="Xiaomi", name="Redmi Note 13", year=2024, aliases=("Note 13",)),
        DeviceModel(id="huawei-pura-70", brand="Huawei", name="Pura 70", year=2024),
    ))
