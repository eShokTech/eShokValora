# eShok Valora

Motor de valoración de equipos usados para compra, reparación y reventa.

## Principio

**Valora no determina cuánto vale un equipo. Determina cuánto puedes pagar por él sin destruir tu margen.**

Valora está pensado para el mercado de segunda vida. El precio de un equipo nuevo es una referencia separada y no debe sustituir el precio real de reventa usada.

La aplicación trata la incertidumbre como dinero. Un dato desconocido no es solamente una alerta: cuando puede cambiar el resultado económico, reduce el techo de compra.

## Backend construido

- **Catálogo canónico:** marcas, modelos, variantes, números de modelo, aliases, regiones, RAM y almacenamiento posibles.
- **Búsqueda híbrida:** consultas como `Moto G65`, `S22 Ultra` o `SM-S908U` pueden resolver al mismo modelo.
- **Identificación por evidencia:** búsqueda manual y candidatos visuales separados de la confirmación real.
- **Certeza por campo:** confirmado, verificado, estimado, desconocido, no disponible y reportado cuando aplica.
- **Escenarios de variantes:** el motor conserva las variantes plausibles y puede elegir un escenario conservador cuando RAM, almacenamiento o variante no están confirmados.
- **IMEI con estado económico:** ingresado no equivale a verificado. Un IMEI reportado bloquea la valoración como inventario vendible.
- **Mercado separado:** segunda vida, venta rápida, reacondicionado y nuevo son categorías distintas. La estimación por defecto usa segunda vida.
- **Mercado basado en evidencia:** mediana, recencia, confianza y cantidad de observaciones evitan depender de un precio fijo.
- **Riesgo de reparación:** fallas conocidas, fallas desconocidas, costo relativo y complejidad generan una reserva independiente.
- **Motor de compra:** combina mercado, reparación, riesgo, incertidumbre, costos de venta y utilidad para obtener máximo de compra y oferta recomendada.
- **SQLite persistente:** catálogo y observaciones de mercado quedan preparados para crecer sin depender de archivos temporales.
- **Importación/exportación de catálogo:** el catálogo puede viajar como JSON, evitando hardcodear miles de modelos en Python.

## Flujo conceptual

1. Buscar o identificar el equipo.
2. Confirmar lo que realmente se conoce.
3. Mantener como desconocido lo que no puede comprobarse.
4. Determinar las variantes plausibles.
5. Proteger el valor usando el escenario conservador cuando exista ambigüedad económica.
6. Separar riesgo de reparación de incertidumbre de identidad.
7. Verificar IMEI y demás datos críticos cuando sea posible.
8. Estimar el mercado de segunda vida con observaciones reales.
9. Calcular cuánto se puede pagar sin destruir el margen.
10. Explicar qué datos hicieron bajar o subir el techo de compra.

## Estructura

    app/
      core/
        catalog.py
        identification.py
        scenario.py
        uncertainty.py
        market.py
        risk.py
        calculator.py
        engine.py
      data/
        database.py
        catalog_io.py
        catalog_seed.py
      ui/
      main.py
    tests/

## Desarrollo

Requiere Python 3.14+.

    .venv\\Scripts\\activate
    pytest
    python -m app.main

La interfaz visual se construirá después de cerrar y probar el núcleo de valoración.
