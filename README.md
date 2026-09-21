# eShok Valora

Motor de valoración de equipos usados para compra, reparación y reventa.

## Principio

Valora no intenta responder cuánto "vale" un equipo nuevo. Estima cuánto puede pagarse por un equipo usado o dañado sin destruir el margen esperado.

## Capas

- Mercado usado: observaciones reales de precios.
- Reacondicionado: precio esperado después de reparar.
- Costos: reparación, venta, riesgo e imprevistos.
- Objetivo: utilidad mínima o margen deseado.
- Resultado: precio máximo de compra y oferta recomendada.

## Desarrollo

Requiere Python 3.14+.

```cmd
.venv\Scripts\activate
python -m app.main
```

El motor no depende de PySide6 y está preparado para futura integración con eShokFix, web o API.
