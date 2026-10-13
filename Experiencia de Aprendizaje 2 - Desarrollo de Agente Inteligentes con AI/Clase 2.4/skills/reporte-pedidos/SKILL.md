---
name: reporte-pedidos
description: Genera en HTML una TABLA con el detalle línea por línea de los pedidos (N° pedido, fecha, cliente, ciudad, estado, producto, categoría, cantidad, precio unitario y subtotal), con filtros opcionales por período, cliente y estado. Úsala cuando el usuario pida el detalle, listado o tabla de pedidos (ej. "detalle de los pedidos de marzo", "tabla con los pedidos de Ana García", "pedidos cancelados del primer trimestre"). NO la uses para reportes ejecutivos, KPIs, gráficos o rankings de ventas, para eso está reporte-ventas.
---

# Detalle de pedidos (tabla HTML)

Esta skill contiene:
- `references/queries.sql`: la query del detalle (Q1). Cada columna tiene como alias
  el marcador `{{...}}` que llena en la plantilla.
- `assets/plantilla.html`: la plantilla HTML (filtros aplicados y tabla de detalle; sin KPIs ni resumen).

No escribas queries propias ni HTML a mano: usa estos archivos con las tools indicadas.

## Paso 1: definir período y filtros

Traduce lo que pide el usuario a `desde` y `hasta` (`YYYY-MM-DD`) y a un texto `periodo` legible:

| Pedido del usuario | desde | hasta | periodo |
|---|---|---|---|
| (sin período) / "anual" / "2025" | 2025-01-01 | 2025-12-31 | Enero – Diciembre 2025 |
| "primer trimestre" / "Q1" | 2025-01-01 | 2025-03-31 | Q1 2025 (Ene – Mar) |
| "segundo trimestre" / "Q2" | 2025-04-01 | 2025-06-30 | Q2 2025 (Abr – Jun) |
| "tercer trimestre" / "Q3" | 2025-07-01 | 2025-09-30 | Q3 2025 (Jul – Sep) |
| "cuarto trimestre" / "Q4" | 2025-10-01 | 2025-12-31 | Q4 2025 (Oct – Dic) |
| "primer semestre" | 2025-01-01 | 2025-06-30 | 1er semestre 2025 |
| "segundo semestre" | 2025-07-01 | 2025-12-31 | 2do semestre 2025 |
| un mes, ej. "marzo" | 2025-03-01 | 2025-03-31 | Marzo 2025 |

Arma además `params` con **las dos claves siempre presentes** (usa `null` si no aplica):

- `cliente`: el nombre tal como lo escribió el usuario (ej. `"ana garcia"`). La query ignora
  tildes y mayúsculas y acepta nombres parciales, así que no necesitas corregirlo. Sin cliente → `null`.
- `estado`: `"entregado"`, `"pendiente"` o `"cancelado"` (singular, minúsculas).
  "entregados" → `"entregado"`, "cancelados" → `"cancelado"`, etc. Sin estado → `null`.

Ejemplo: "pedidos cancelados de Ana García en el primer trimestre" →
`desde="2025-01-01"`, `hasta="2025-03-31"`, `params={"cliente": "Ana García", "estado": "cancelado"}`.

## Paso 2: obtener los datos

Llama a:

```
run_sql_file(
    sql_path="/skills/reporte-pedidos/references/queries.sql",
    desde=..., hasta=...,
    params={"cliente": ..., "estado": ...}
)
```

Devuelve los filtros aplicados, `FILAS_DETALLE` (una línea por producto de cada pedido) y
`TOTAL_PEDIDOS` (solo para saber si hay datos).

Si `TOTAL_PEDIDOS` es 0, no generes el HTML: dile al usuario que no hay pedidos con esos filtros
(si `FILTRO_CLIENTE` es "Sin coincidencias", indica que no se encontró ese cliente).

## Paso 3: generar el HTML

Llama a:

```
render_report(
    sql_path="/skills/reporte-pedidos/references/queries.sql",
    template_path="/skills/reporte-pedidos/assets/plantilla.html",
    output_path="/reports/detalle_pedidos.html",
    desde=..., hasta=..., periodo=..., resumen="",
    params={"cliente": ..., "estado": ...}
)
```

Usa exactamente los mismos `desde`, `hasta` y `params` del paso 2. El HTML es solo la tabla:
`resumen` va siempre vacío (`""`).
Si devuelve un error, corrige el argumento indicado y vuelve a llamarla una vez.

## Paso 4: responder

Responde en español con:
- Una línea confirmando que la tabla HTML fue generada en `reports/detalle_pedidos.html`.
- Los filtros aplicados (período, cliente, estado).
