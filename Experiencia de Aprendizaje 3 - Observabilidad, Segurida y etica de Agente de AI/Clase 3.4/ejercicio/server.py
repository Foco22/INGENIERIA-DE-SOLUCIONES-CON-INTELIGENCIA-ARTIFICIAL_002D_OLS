"""Servidor MCP con la información del curso
"Ingeniería de Soluciones con Inteligencia Artificial" (DuocUC).

Expone tools que Claude Desktop (u otro cliente MCP) puede invocar.
Transporte: Streamable HTTP en /mcp  (apto para Google Cloud Run).
"""
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from agent_app.tools import retrieve

load_dotenv()

mcp = FastMCP(
    "curso-ingenieria-soluciones-ia",
    instructions=(
        "Información del curso 'Ingeniería de Soluciones con Inteligencia Artificial' "
        "del profesor Francisco Macaya (DuocUC). Usa search_course_content para "
        "responder preguntas sobre el contenido, clases y apuntes del curso."
    ),
    host="0.0.0.0",
    port=int(os.getenv("PORT", "8080")),
    stateless_http=True,  # necesario en Cloud Run (múltiples instancias)
)

COURSE_INFO = {
    "nombre": "Ingeniería de Soluciones con Inteligencia Artificial",
    "institucion": "DuocUC",
    "profesor": "Francisco Macaya",
    "temas": [
        "LLMs y prompting",
        "RAG, embeddings y bases de datos vectoriales",
        "Agentes con LangChain / LangGraph",
        "MCP (Model Context Protocol)",
        "APIs con FastAPI y Docker",
        "Costos, latencia y evaluación de modelos",
        "Observabilidad (LangSmith, Grafana)",
        "Seguridad, guardrails y ética en IA",
    ],
}


@mcp.tool()
def get_course_info() -> dict:
    """Información general del curso: nombre, institución, profesor y temas que cubre."""
    return COURSE_INFO


@mcp.tool()
def list_course_topics() -> list[str]:
    """Lista los temas principales que cubre el curso."""
    return COURSE_INFO["temas"]


@mcp.tool()
def search_course_content(query: str, top_k: int = 5) -> str:
    """Busca en la base de conocimiento del curso (apuntes y clases) los fragmentos
    más relevantes para la consulta. Úsala para responder preguntas sobre el
    contenido de la asignatura.

    Args:
        query: Consulta en lenguaje natural (ej. "¿qué es un guardrail?").
        top_k: Cantidad de fragmentos a devolver (1-10).
    """
    top_k = max(1, min(top_k, 10))
    docs = retrieve(query, top_k=top_k)
    if not docs:
        return "No se encontró información relevante en el material del curso."
    parts = []
    for i, d in enumerate(docs, 1):
        source = os.path.basename(str((d.get("metadata") or {}).get("source", "")))
        header = f"[{i}] (relevancia {d.get('score', 0):.2f})" + (f" {source}" if source else "")
        parts.append(f"{header}\n{d['text']}")
    return "\n\n".join(parts)


@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    from starlette.responses import PlainTextResponse
    return PlainTextResponse("ok")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
