# Asistente Multi-Agente

Sistema de agentes inteligentes construido con LangGraph que permite consultar datos de ventas y generar reportes HTML en lenguaje natural.

## Arquitectura

```
Usuario
  └── Supervisor (decide la ruta)
        ├── sql_agent    → genera y ejecuta queries sobre la base SQLite según la pregunta
        └── report_agent → Deep Agent con la skill "reporte-ventas" → reporte HTML
```

- **sql_agent**: recibe el esquema en su system prompt en cada llamada, resuelve nombres con
  `find_value`, escribe la query y la ejecuta (`execute_query`).
  Recibe la conversación completa, así entiende preguntas de seguimiento.
- **report_agent**: sigue la skill `reporte-ventas` (queries y plantilla predefinidas).

## Skills (Deep Agents)

El `report_agent` es un [Deep Agent](https://docs.langchain.com/oss/python/deepagents/skills)
(`create_deep_agent`) que carga las skills de `skills/` con *progressive disclosure*:

1. **Metadatos**: al iniciar, el agente solo ve `name` y `description` del `SKILL.md`.
2. **Instrucciones**: cuando se le pide un reporte, lee `skills/reporte-ventas/SKILL.md`.
3. **Recursos**: las tools usan `references/queries.sql` (queries específicas del reporte) y
   `assets/plantilla.html` (plantilla del HTML).

```
skills/reporte-ventas/
├── SKILL.md                 # Pasos: período → datos → resumen → HTML
├── references/queries.sql   # Q1..Q7; cada alias = marcador {{...}} de la plantilla
└── assets/plantilla.html    # KPIs, gráficos Chart.js y rankings
```

Las tools del agente son genéricas (`run_sql_file`, `render_report`): el conocimiento
específico (qué consultar y cómo presentarlo) vive en la skill. Para cambiar el reporte
basta con editar `queries.sql` o `plantilla.html`, sin tocar código Python.
El HTML se escribe en `reports/reporte_ventas.html` y Streamlit lo muestra con un botón de descarga.

## Stack

- **LangGraph** — orquestación de agentes
- **OpenAI** (`gpt-4o-mini`) — LLM
- **Streamlit** — interfaz de chat
- **SQLite** — base de datos de ventas
- **Deep Agents** — skills del agente de reportes

## Estructura

```
agent_app/
├── agent.py      # Grafo LangGraph con Supervisor + agentes
├── prompts.py    # Prompts del sistema para cada agente
├── tools.py      # Tools: find_value, execute_query, run_sql_file, render_report
└── utils/
skills/
└── reporte-ventas/  # Skill del agente de reportes (SKILL.md, queries.sql, plantilla.html)
data/
├── seed.py       # Genera la base de datos SQLite con datos de ventas 2025
app.py            # Interfaz Streamlit
Dockerfile
requirements.txt
```

## Levantar con Docker

```bash
docker build -t ventas-agent .
docker run -p 8501:8501 --env-file .env ventas-agent
```

Abrir en: http://localhost:8501

## Variables de entorno

Crear un archivo `.env` con:

```
OPENAI_API_KEY=...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=...
LANGCHAIN_PROJECT=multi-agent-project
```

## Tarea

Crear una **nueva skill `detalle-pedidos`** para el `report_agent`, que permita ver el detalle
completo de los pedidos **como tabla** en un HTML.

Hoy el sistema responde preguntas puntuales (`sql_agent`) y genera un reporte agregado
(`reporte-ventas`), pero no hay forma de ver los pedidos línea por línea. Ejemplos de lo que
el usuario debe poder pedir:

- *"Muéstrame el detalle de los pedidos de marzo"*
- *"Quiero ver en una tabla todos los pedidos de Ana García"*
- *"Dame el detalle de los pedidos cancelados del primer trimestre"*

---

### Qué debe mostrar la tabla

Una fila por producto de cada pedido, con estas columnas:

| N° pedido | Fecha | Cliente | Ciudad | Estado | Producto | Categoría | Cantidad | Precio unitario | Subtotal |
|---|---|---|---|---|---|---|---|---|---|

Además, arriba de la tabla:
- Filtros aplicados (período, cliente y/o estado).
- Totales: cantidad de pedidos, unidades y monto total del detalle mostrado.

**Filtros** (todos opcionales, combinables):
- **Período**: mes, trimestre, semestre o año (por defecto, todo 2025).
- **Cliente**: por nombre, aunque el usuario lo escriba sin tildes.
- **Estado**: `entregado`, `pendiente` o `cancelado`.

---

### Qué se debe implementar

```
skills/detalle-pedidos/
├── SKILL.md                 # frontmatter (name, description) + pasos que sigue el agente
├── references/queries.sql   # queries con alias = marcadores de la plantilla
└── assets/plantilla.html    # tabla HTML con los marcadores {{...}}
```

1. **`SKILL.md`**
   - Frontmatter con `name: detalle-pedidos` (igual al nombre de la carpeta) y una `description`
     clara: es lo que el agente lee para decidir **cuándo** usar esta skill y no `reporte-ventas`.
   - Pasos: traducir el pedido a `desde`/`hasta` y filtros, llamar a `run_sql_file`, luego a
     `render_report` con `output_path="/reports/detalle_pedidos.html"` y responder.
2. **`references/queries.sql`**
   - Una o más queries con el formato `-- name: ...`, cada una devolviendo **una fila**.
   - Los filtros opcionales se pasan con `params`, por ejemplo:
     `AND (:cliente IS NULL OR c.nombre = :cliente)`.
3. **`assets/plantilla.html`**
   - Tabla con encabezados y los marcadores `{{...}}`. Puedes reutilizar el estilo de
     `skills/reporte-ventas/assets/plantilla.html`.
4. **Supervisor** (`agent_app/prompts.py`)
   - Ajustar `SUPERVISOR_SYSTEM_PROMPT` para que "detalle de pedidos", "tabla de pedidos",
     "listado de pedidos", etc. vayan a `report_agent` y no a `sql_agent`.
5. **`REPORT_SYSTEM_PROMPT`**
   - Hoy obliga a leer siempre `reporte-ventas/SKILL.md`. Cámbialo para que el agente elija la
     skill correcta según su `description` (las dos se cargan desde `/skills/`).

**No es necesario modificar** `tools.py`, `agent.py` ni `app.py`: el agente ya carga todas las
skills de `skills/`, y la interfaz muestra cualquier HTML nuevo que aparezca en `reports/`.

---

### Pistas

- `run_sql_file` y `render_report` ya aceptan un parámetro `params` (dict) para los filtros
  extra de tu `.sql`. Pasa **todas** las claves que use el `.sql` (usa `null` si no aplica).
- Para generar muchas filas en una sola celda, usa `group_concat(...)` como en
  `Q3_ranking_clientes` de `reporte-ventas/references/queries.sql`.
- Si el alias empieza con `FILAS_`, `run_sql_file` lo devuelve como texto legible al agente
  (sin etiquetas HTML).
- Usa `find_value` como referencia: el nombre del cliente debe coincidir exactamente con la
  base (`Ana García`, con tilde). Puedes indicarlo en `SKILL.md` o resolverlo en SQL.
- Para depurar, revisa en LangSmith qué archivos lee el agente (`read_file`) y con qué
  argumentos llama a las tools.

---

### Requisitos

- El reporte de ventas (`reporte-ventas`) y el `sql_agent` deben seguir funcionando.
- Los datos de la tabla deben coincidir con la base: verifica al menos un caso con una query
  manual.
- Debe funcionar en Docker (`docker build` + `docker run`).

## Ejemplos de uso

- *"¿Cuáles son las ventas por mes del 2025?"*
- *"¿Cuántos pedidos tiene Ana García?"*
- *"Dame un reporte de ventas del primer trimestre en HTML"*
- *"Quiero el informe de ventas del segundo semestre"*
- *"¿Cuál es el correo de Ana Garcia?"*
