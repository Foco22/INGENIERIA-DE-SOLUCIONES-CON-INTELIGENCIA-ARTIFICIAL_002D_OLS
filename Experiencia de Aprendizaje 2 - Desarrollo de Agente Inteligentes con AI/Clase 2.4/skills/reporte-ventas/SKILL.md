---
name: reporte-ventas
description: Genera un reporte ejecutivo de ventas en HTML a partir de queries SQL predefinidas sobre la base de ventas 2025. Úsala cuando el usuario pida un reporte, informe, resumen ejecutivo, dashboard o KPIs de ventas, opcionalmente filtrado por período (mes, trimestre, rango de fechas).
---

# Reporte ejecutivo de ventas (HTML)

Esta skill contiene:
- `references/queries.sql`: las queries específicas del reporte (Q1 a Q7). Cada columna tiene como alias
  el marcador `{{...}}` que llena en la plantilla.
- `assets/plantilla.html`: la plantilla HTML del reporte (KPIs, gráficos Chart.js y rankings).

No escribas queries propias ni HTML a mano: usa estos archivos con las tools indicadas.

## Paso 1: definir el período

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

## Paso 2: obtener los datos

Llama a:

```
run_sql_file(sql_path="/skills/reporte-ventas/references/queries.sql", desde=..., hasta=...)
```

Devuelve un diccionario con los KPIs (total vendido, mejor/peor mes, rankings, etc.).

## Paso 3: redactar el resumen

Con esos datos, escribe un `resumen` en español de 3 a 5 oraciones: nivel de ventas del período,
mejor y peor mes, cliente y producto destacados, y una recomendación accionable.
Usa solo cifras que aparezcan en el resultado del paso 2 (formato `$34.408.990`).

## Paso 4: generar el HTML

Llama a:

```
render_report(
    sql_path="/skills/reporte-ventas/references/queries.sql",
    template_path="/skills/reporte-ventas/assets/plantilla.html",
    output_path="/reports/reporte_ventas.html",
    desde=..., hasta=..., periodo=..., resumen=...
)
```

Si devuelve un error, corrige el argumento indicado y vuelve a llamarla una vez.

## Paso 5: responder

Responde en español con:
- Una línea confirmando que el reporte HTML fue generado en `reports/reporte_ventas.html`.
- 3 o 4 viñetas con los KPIs principales (total vendido, mejor mes, cliente top, producto top).
