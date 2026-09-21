# eShok Valora

Motor de valoración de equipos usados para compra, reparación y reventa.

## Principio

**Valora no determina cuánto vale un equipo. Determina cuánto puedes pagar por él sin destruir tu margen.**

La aplicación trata la incertidumbre como parte del precio. Un dato desconocido no es solamente una alerta: cuando puede afectar el resultado económico, genera una reserva económica.

## Arquitectura actual

- Catálogo: marcas, modelos, variantes, números de modelo, aliases, regiones, RAM y almacenamiento posibles.
- Selección híbrida: búsqueda libre como "Moto G65", selección por marca/modelo y selección posterior de variante/capacidad.
- Identificación: una fuente visual puede proponer un modelo candidato, pero no confirma automáticamente RAM, almacenamiento, variante ni IMEI.
- Certeza por campo: confirmado, estimado, desconocido o no disponible.
- Incertidumbre económica: faltantes críticos como IMEI, variante, capacidad o pruebas funcionales afectan económicamente la valuación.
- Mercado de segunda vida: observaciones reales con fecha, fuente, condición, ciudad y confianza.
- Valuación: precio máximo y oferta recomendada después de reparación, riesgo, costos de venta y utilidad.

## Flujo conceptual

1. Buscar o identificar el equipo.
2. Confirmar lo que realmente se conoce.
3. Mantener como desconocido lo que no puede comprobarse.
4. Determinar las variantes plausibles.
5. Usar el escenario conservador cuando una característica económica importante no está confirmada.
6. Aplicar reserva adicional por incertidumbre y riesgo.
7. Calcular cuánto se puede pagar.

## Desarrollo

Requiere Python 3.14+.

    .venv\Scripts\activate
    pytest
    python -m app.main
