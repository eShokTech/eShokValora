from __future__ import annotations

from .models import ValuationInput, ValuationResult


def calculate_valuation(data: ValuationInput) -> ValuationResult:
    fixed_costs = (
        data.repair_cost
        + data.risk_reserve
        + data.selling_cost
        + data.other_cost
    )

    # Cuando se define margen, la utilidad mínima se calcula sobre el precio
    # esperado de venta, no sobre el costo de compra.
    margin_profit = 0.0
    if data.desired_margin_percent is not None:
        margin_profit = data.market_price * (data.desired_margin_percent / 100.0)

    target_profit = max(data.desired_profit, margin_profit)

    maximum_purchase = max(0.0, data.market_price - fixed_costs - target_profit)
    recommended = max(
        0.0,
        maximum_purchase - data.recommendation_buffer,
    )

    profit_at_max = data.market_price - fixed_costs - maximum_purchase
    profit_at_recommended = data.market_price - fixed_costs - recommended

    margin_at_max = (
        (profit_at_max / data.market_price) * 100
        if data.market_price else 0.0
    )
    margin_at_recommended = (
        (profit_at_recommended / data.market_price) * 100
        if data.market_price else 0.0
    )

    viable = maximum_purchase > 0

    notes: list[str] = []
    if not viable:
        notes.append("Los costos y la utilidad objetivo consumen todo el valor de reventa.")
    if data.desired_margin_percent is not None and margin_profit > data.desired_profit:
        notes.append("Se aplicó el objetivo de margen porque supera la utilidad fija.")
    if data.recommendation_buffer > 0:
        notes.append("La oferta recomendada conserva un colchón adicional frente al máximo.")

    return ValuationResult(
        market_price=round(data.market_price, 2),
        total_non_purchase_cost=round(fixed_costs, 2),
        maximum_purchase_price=round(maximum_purchase, 2),
        recommended_offer=round(recommended, 2),
        expected_profit_at_max=round(profit_at_max, 2),
        expected_profit_at_recommended=round(profit_at_recommended, 2),
        expected_margin_at_max_percent=round(margin_at_max, 2),
        expected_margin_at_recommended_percent=round(margin_at_recommended, 2),
        viable=viable,
        notes=tuple(notes),
    )
