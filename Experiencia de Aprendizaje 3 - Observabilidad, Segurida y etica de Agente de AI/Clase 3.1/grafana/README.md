# Agente Matemático con Observabilidad (Grafana + OpenTelemetry)

Agente LangGraph que resuelve operaciones con 4 tools (`sumar`, `restar`, `multiplicar`, `dividir`).
Envía trazas por OpenTelemetry a un Grafana local (imagen `grafana/otel-lgtm`: Grafana + Tempo + Loki + Prometheus).

```
Streamlit → agente LangGraph → OpenTelemetry (OTLP :4318) → Tempo → Grafana (:3000)
```

## Requisitos

- Python 3.10+
- Docker Desktop (abierto)
- Una `OPENAI_API_KEY`

## 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 2. Configurar `.env`

Crear un archivo `.env` en esta carpeta:

```
OPENAI_API_KEY=tu_api_key
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_SERVICE_NAME=agente-matematico
```

No requiere token: es un Grafana local. El `.env` está en `.gitignore`.

## 3. Levantar Grafana con Docker

```bash
docker compose up -d
```

Entrar a http://localhost:3000 (usuario `admin`, contraseña `admin`). El dashboard
`Agente Matematico` se carga solo desde `dashboards/`, incluso tras borrar los volúmenes.

| Comando | Acción |
|---|---|
| `docker compose stop` / `start` | Detener / reiniciar (conserva los datos) |
| `docker compose down -v` | Borrar contenedor y datos |

## 4. Ejecutar el agente

```bash
streamlit run app.py
```

Abre http://localhost:8501. Cada pregunta genera una traza.

## 5. Ver la telemetría en Grafana

- **Trazas:** Explore → fuente de datos **Tempo** → TraceQL:
  `{resource.service.name="agente-matematico"}`
- Al abrir una traza, hacer clic en un span y expandir **Span Attributes**:
  `input.value` y `output.value` muestran lo que entró y salió de cada nodo y tool.
- **Dashboard** `Agente Matematico`: http://localhost:3000/d/agente-matematico
  (totales de sesiones y mensajes, mensajes por sesión, latencia promedio/p10/p90 por
  componente, y detalle de tools y LLM filtrable por `session`).

## Cómo se conecta `telemetry.py` con LangGraph

La conexión son dos líneas en `agent_app/agent.py`, antes de crear el grafo y el LLM:

```python
from agent_app.telemetry import setup_telemetry

load_dotenv()          # carga el .env con las variables OTEL_*
setup_telemetry()      # activa la telemetría
```

`setup_telemetry()` (en `telemetry.py`) hace tres cosas:

1. Lee `OTEL_EXPORTER_OTLP_ENDPOINT`. Si no existe, no hace nada.
2. Crea un `TracerProvider` con el servicio `agente-matematico`, que envía los spans por OTLP a `http://localhost:4318`.
3. Ejecuta `LangChainInstrumentor().instrument()`, que es lo que conecta con LangGraph.

LangGraph está construido sobre LangChain y reporta lo que hace (inicio de un nodo, llamada al LLM,
ejecución de una tool) mediante callbacks de LangChain. El instrumentador se engancha a esos
callbacks de forma global, por eso no hay que modificar los nodos ni las tools:

```
Streamlit → app.invoke() → LangGraph/LangChain emiten eventos
                                  ↓ LangChainInstrumentor los captura
                           spans con input.value / output.value
                                  ↓ TracerProvider
                     OTLP http://localhost:4318 → Tempo → Grafana
```

- Cualquier ejecución del grafo genera trazas (Streamlit, un script o `langgraph dev`), siempre que importe `agent.py`.
- Si se eliminan esas dos líneas, el agente funciona igual pero no envía nada a Grafana.
- El `session.id` sale del `thread_id` que se pasa en `config={"configurable": {"thread_id": ...}}`.

## ¿Dónde se guardan los datos?

Grafana **no guarda datos**: solo es la interfaz que los muestra. Los datos los guarda el
contenedor `lgtm` (imagen `grafana/otel-lgtm`), que incluye varias herramientas:

```
Agente (Python)
  └─ OpenTelemetry (telemetry.py) ── OTLP HTTP :4318 ──► contenedor "lgtm"
                                                           ├─ OTel Collector → recibe los datos
                                                           ├─ Tempo          → guarda las trazas
                                                           ├─ Loki           → guarda logs
                                                           ├─ Prometheus     → guarda métricas
                                                           └─ Grafana (:3000) → los visualiza
```

- Nuestro agente solo exporta **trazas**, así que sus datos quedan en **Tempo**.
- Grafana consulta a Tempo (con TraceQL) para dibujar las trazas y los paneles del dashboard.

### Persistencia en disco

En `docker-compose.yml` el volumen `lgtm-data:/data` es un **volumen nombrado de Docker**: los datos
viven en el almacenamiento interno de Docker, no en la carpeta del proyecto.

| Acción | ¿Se conservan los datos? |
|---|---|
| `docker compose stop` / `start` | Sí |
| `docker compose down` | Sí (el volumen sigue existiendo) |
| `docker compose down -v` | **No**, se borra el volumen |

- En Windows el volumen está dentro de la VM de Docker Desktop (WSL2). Para inspeccionarlo:
  `docker volume inspect grafana_lgtm-data`.
- Los **dashboards no se guardan en el volumen**: se montan como archivos de solo lectura desde
  `dashboards/`, por eso reaparecen aunque se borren los datos.
- Los datos son **locales**: van a tu contenedor porque `OTEL_EXPORTER_OTLP_ENDPOINT` apunta a
  `http://localhost:4318`. Si apuntara a una URL de Grafana Cloud, se guardarían en la nube.

## Estructura

```
app.py                  # interfaz Streamlit
docker-compose.yml      # Grafana + Tempo + Loki + Prometheus
dashboards/             # dashboard (JSON) provisionado automáticamente al iniciar Docker
agent_app/agent.py      # grafo LangGraph
agent_app/telemetry.py  # configuración OpenTelemetry
agent_app/tools.py      # tools matemáticas
agent_app/prompts.py    # prompt del agente
```

## Problemas comunes

- **No aparecen trazas:** revisar que las variables `OTEL_*` estén en el `.env`, reiniciar Streamlit y ampliar el rango de tiempo en Grafana.
- **Puerto 3000 ocupado:** cambiar `"3000:3000"` por `"3001:3000"` en `docker-compose.yml`.
- **Cambios al dashboard:** se guardan en el volumen. Para versionarlos, exportar el JSON desde Grafana (Share → Export) y reemplazar `dashboards/agente-matematico.json`.
