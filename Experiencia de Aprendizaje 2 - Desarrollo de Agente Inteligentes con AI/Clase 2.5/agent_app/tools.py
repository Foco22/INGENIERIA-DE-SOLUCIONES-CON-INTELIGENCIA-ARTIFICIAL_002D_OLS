import os
from typing import Optional
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

from agent_app.ingest import VECTORSTORE_PATH, EMBEDDING_MODEL

TOP_K = 6
_store: Optional[InMemoryVectorStore] = None


def get_store() -> InMemoryVectorStore:
    """Carga el índice una sola vez (lazy) para no pagar embeddings ni lectura en cada pregunta."""
    global _store
    if _store is None:
        if not os.path.exists(VECTORSTORE_PATH):
            raise FileNotFoundError(
                "No existe el vector store. Ejecuta primero: python -m agent_app.ingest"
            )
        _store = InMemoryVectorStore.load(VECTORSTORE_PATH, OpenAIEmbeddings(model=EMBEDDING_MODEL))
    return _store


# content_and_artifact: el LLM recibe el texto y el grafo recibe los documentos para la trazabilidad.
@tool(response_format="content_and_artifact")
def buscar_estados_financieros(query: str, year: Optional[int] = None):
    """Busca en los estados financieros consolidados de Abastible S.A. y Filiales (informes 2021 a 2025):
    ingresos, costos, ganancias, resultado operacional, activos, pasivos, patrimonio, flujos de efectivo,
    auditor, filiales, ventas de gas licuado, políticas contables y notas.
    Solo contiene información de Abastible. Usar `year` (2021-2025) para buscar en el informe de ese año."""
    store = get_store()
    doc_filter = (lambda d: d.metadata["year"] == year) if year else None
    docs = store.similarity_search(query, k=TOP_K, filter=doc_filter)
    if not docs:
        return "No se encontraron resultados en los estados financieros.", []

    content = "\n\n---\n\n".join(d.page_content for d in docs)
    artifact = [
        {"year": d.metadata["year"], "page": d.metadata["page"], "content": d.page_content}
        for d in docs
    ]
    return content, artifact


tools = [buscar_estados_financieros]
