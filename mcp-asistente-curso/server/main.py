"""Entrypoint del servidor MCP (streamable-http).

Declara el Server MCP con sus `instructions` (plan.md §4.3, §4.5 — instruye
al modelo del cliente a llamar reportar_interaccion), registra las tools de
server/tools.py y server/pruebas.py, y expone la app ASGI para Cloud Run
(escuchando en el puerto de la env var PORT, ver Dockerfile).

Si `GCS_BUCKET` está seteado, descarga `index/latest/` (utils/gcs.py) a
`data/` ANTES de construir la app — un contenedor de Cloud Run arranca sin
`data/chunks.parquet`/`graph.json` (gitignored, no se comitean, §6), así que
sin esta descarga el servidor respondería siempre vacío. Es una llamada a
nivel de módulo (no un hook de lifespan del SDK MCP): Dockerfile hace
`uvicorn server.main:app`, así que uvicorn importa este módulo una sola vez
al arrancar el proceso — exactamente el momento en que plan.md §4.3 pide
"al iniciar el proceso" descargar el índice. Sin `GCS_BUCKET` (dev local) no
se toca GCS, se sigue leyendo `data/` tal cual está en disco.
"""

from __future__ import annotations

import os

from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

from server.auth import AuthMiddleware
from server.tools import buscar_contenido as _buscar_contenido
from server.tools import detalle_pruebas as _detalle_pruebas
from server.tools import reportar_interaccion as _reportar_interaccion
from utils.gcs import download_latest_index
from utils.paths import REPO_ROOT

_DATA_DIR = REPO_ROOT / "mcp-asistente-curso" / "data"

if os.environ.get("GCS_BUCKET"):
    download_latest_index(_DATA_DIR)

_INSTRUCTIONS = """Este servidor expone herramientas de búsqueda sobre el contenido y las \
pruebas/evaluaciones del curso. No genera respuestas en lenguaje natural: cada tool devuelve \
fragmentos de texto recuperados con su cita (experiencia/clase/archivo) — arma la respuesta \
al estudiante vos mismo a partir de esos fragmentos, citando de dónde salió cada dato.

Cada vez que uses buscar_contenido o detalle_pruebas para responder una pregunta del \
estudiante, al final de tu respuesta en ESE turno llamá una sola vez a reportar_interaccion, \
pasando el interaccion_id de la ÚLTIMA de esas dos tools que hayas usado en el turno (no hace \
falta reportar cada una por separado si usaste varias) junto con la respuesta final que le \
diste al estudiante."""

mcp = MCPServer(name="asistente-curso", instructions=_INSTRUCTIONS)


@mcp.tool(
    name="buscar_contenido",
    description=(
        "Busca contenido de las clases del curso — conceptos de materia, relaciones entre "
        'temas, o el contenido de una clase puntual (ej. "qué es RAG", "cómo se relaciona con '
        'prompt engineering", "qué vimos en la clase 2.3"). Si la pregunta es sobre una clase '
        "específica, pasa experiencia/clase. No cubre pruebas/evaluaciones (para eso usa "
        "detalle_pruebas) ni fechas de calendario."
    ),
)
def buscar_contenido(query: str, experiencia: str | None = None, clase: str | None = None) -> dict:
    return _buscar_contenido(query, experiencia=experiencia, clase=clase)


@mcp.tool(
    name="detalle_pruebas",
    description=(
        "Busca información sobre las pruebas/evaluaciones del curso: pauta, indicadores de "
        "logro, requisitos de entrega, % de ponderación, cronograma por semana. Úsala para "
        'preguntas tipo "qué entra en la Evaluación Parcial 1", "cómo se evalúa el encargo", '
        '"qué debo entregar". No da fechas de calendario absolutas — los PDFs de evaluación '
        "solo tienen semanas relativas del cronograma, no fechas concretas."
    ),
)
def detalle_pruebas(query: str, experiencia: str | None = None) -> dict:
    return _detalle_pruebas(query, experiencia=experiencia)


@mcp.tool(
    name="reportar_interaccion",
    description=(
        "Reporta la respuesta final que le diste al estudiante para esta interacción. "
        "Llamala una sola vez por turno, inmediatamente después de responder. Si en ese turno "
        "usaste más de una tool de este servidor, usa el interaccion_id de la ÚLTIMA que "
        "llamaste — no hace falta reportar cada una por separado."
    ),
)
def reportar_interaccion(interaccion_id: str, respuesta: str, util: bool | None = None) -> dict:
    return _reportar_interaccion(interaccion_id, respuesta=respuesta, util=util)


# enable_dns_rebinding_protection=False: por default el SDK solo confía en
# Host headers de localhost -- cualquier hostname real (ej. el de Cloud Run)
# devuelve 421 "Invalid Host header" (encontrado en la primera corrida real,
# ver ESTADO.md). No hace falta esa protección acá: AuthMiddleware (arriba)
# ya exige un bearer token válido para CUALQUIER request antes de llegar a
# esta capa -- un Host header falsificado no le da a nadie acceso sin token.
app = mcp.streamable_http_app(
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False)
)
app.add_middleware(AuthMiddleware)