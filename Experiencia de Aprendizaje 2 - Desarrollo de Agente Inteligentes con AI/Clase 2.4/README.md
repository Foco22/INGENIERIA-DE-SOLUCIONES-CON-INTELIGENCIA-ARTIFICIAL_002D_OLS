# Asistente Multi-Agente

Sistema de agentes inteligentes construido con LangGraph que permite consultar y visualizar datos de ventas en lenguaje natural.

## Arquitectura

```
Usuario
  └── Supervisor (decide la ruta)
        ├── sql_agent    → consulta la base de datos SQLite
        ├── python_agent → genera visualizaciones con Plotly
        └── sql_agent → python_agent → (SQL + gráfico en un solo paso)
```

Antes de invocar cada sub-agente, un **summarizer** resume la conversación y le entrega una instrucción limpia y concisa, evitando ruido del historial acumulado.

## Stack

- **LangGraph** — orquestación de agentes
- **OpenAI** (`gpt-4o-mini`) — LLM
- **Streamlit** — interfaz de chat
- **SQLite** — base de datos de ventas
- **Plotly** — visualizaciones

## Estructura

```
agent_app/
├── agent.py      # Grafo LangGraph con Supervisor + agentes
├── prompts.py    # Prompts del sistema para cada agente
├── tools.py      # Tools: get_schema, execute_query, transform_data_to_visualization
└── utils/
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

Implementar **uno** de los siguientes agentes e integrarlo al sistema multi-agente existente:

---

### Opción A — Agente de Reporte Ejecutivo

Un agente que, ante una solicitud del usuario ("dame un reporte", "resumen de ventas"), ejecuta múltiples queries SQL y genera un resumen estructurado con los KPIs principales.

**Lo que debe incluir el reporte:**
- Total vendido en el período
- Mejor y peor mes
- Cliente con más compras
- Producto más vendido
- Tendencia general

**Lo que se debe implementar:**
- Tool `generate_report` en `tools.py`
- Nodo `report_agent` en `agent.py`
- Ruta `"report_agent"` en el supervisor
- Prompt `REPORT_SYSTEM_PROMPT` en `prompts.py`

---

### Opción B — Agente de Proyecciones

Un agente que toma los datos históricos de ventas y proyecta los próximos meses usando una tendencia calculada (promedio móvil o regresión lineal).

**Lo que debe mostrar:**
- Proyección de ventas para los próximos 3 meses
- Gráfico que combine datos reales y proyección
- Intervalo de confianza o margen de error estimado

**Lo que se debe implementar:**
- Tool `project_sales` en `tools.py`
- Nodo `forecast_agent` en `agent.py`
- Ruta `"forecast_agent"` en el supervisor
- Prompt `FORECAST_SYSTEM_PROMPT` en `prompts.py`

---

**Requisitos comunes:**
- El nuevo agente debe integrarse al grafo LangGraph existente sin romper los agentes actuales.
- El supervisor debe reconocer cuándo derivar al nuevo agente.
- Debe funcionar correctamente en Docker (`docker build` + `docker run`).

## Ejemplos de uso

- *"¿Cuáles son las ventas por mes del 2025?"*
- *"Haz un gráfico de las ventas por categoría"*
- *"¿Cuántos pedidos tiene Ana García?"*
- *"Muéstrame las ventas de Ana García por mes en un gráfico de líneas"*
