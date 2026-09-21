from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UncertaintyItem:
    field: str
    reason: str
    penalty_rate: float
    fixed_penalty: float = 0.0
    critical: bool = False


@dataclass(frozen=True)
class UncertaintyAssessment:
    reserve: float
    score: float
    level: str
    items: tuple[UncertaintyItem, ...]

    @property
    def reasons(self) -> tuple[str, ...]:
        return tuple(item.reason for item in self.items)


def assess_uncertainty(
    *,
    market_price: float,
    model_confirmed: bool = True,
    exact_variant_confirmed: bool = False,
    ram_confirmed: bool = False,
    storage_confirmed: bool = False,
    imei_verified: bool = False,
    carrier_confirmed: bool = True,
    functional_test_completed: bool = False,
) -> UncertaintyAssessment:
    if market_price <= 0:
        raise ValueError("El precio de mercado debe ser mayor que cero.")

    items: list[UncertaintyItem] = []
    if not model_confirmed:
        items.append(UncertaintyItem("modelo", "El modelo es estimado, no confirmado.", 0.08, critical=True))
    if not exact_variant_confirmed:
        items.append(UncertaintyItem("variante", "La variante exacta no está confirmada.", 0.04))
    if not ram_confirmed:
        items.append(UncertaintyItem("RAM", "La RAM es desconocida; se protege contra una variante inferior.", 0.03))
    if not storage_confirmed:
        items.append(UncertaintyItem("almacenamiento", "El almacenamiento es desconocido; se protege contra una variante inferior.", 0.05))
    if not imei_verified:
        items.append(UncertaintyItem("IMEI", "El IMEI no fue verificado; existe riesgo de reporte o blacklist.", 0.10, critical=True))
    if not carrier_confirmed:
        items.append(UncertaintyItem("red/operador", "El operador o bloqueo de red no está confirmado.", 0.05))
    if not functional_test_completed:
        items.append(UncertaintyItem("pruebas", "El funcionamiento completo no ha sido comprobado.", 0.04))

    raw_score = sum(item.penalty_rate * 100 for item in items)
    score = min(100.0, raw_score)
    level = "low" if score < 15 else "medium" if score < 30 else "high"

    reserve = market_price * min(0.35, sum(item.penalty_rate for item in items))
    if any(item.critical for item in items):
        reserve += market_price * 0.03
    reserve = min(reserve, market_price * 0.40)

    return UncertaintyAssessment(
        reserve=round(reserve, 2),
        score=round(score, 2),
        level=level,
        items=tuple(items),
    )
