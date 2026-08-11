# Estado del proyecto

Resumen rápido de dónde vamos y qué falta — el detalle de diseño está en `plan.md`.

## Hecho

- **Fase 0 — Setup**: estructura de carpetas, `requirements.txt`, `Dockerfile` base.
- **Fase 1 — Ingesta**: `indexer/ingest.py` (PDF → Markdown, `pymupdf4llm` + OCR) + `indexer/manifest.py` (diff-aware). Los 27 `.md` del corpus están generados y comiteados en `data/markdown/`.
- **Fase 2 — Chunking + embeddings**: `indexer/chunk.py` + `utils/embeddings.py` (`fastembed`, sin torch) + `indexer/run.py`. `data/chunks.parquet` completo: **382 chunks, 27/27 PDFs**. Búsqueda vectorial simple validada con queries reales.

## En progreso

- **Fase 3 — Grafo de conocimiento**: código completo y probado (`indexer/graph.py`, `utils/llm.py`, tests con LLM simulado — todos pasan). Falta terminar el **bootstrap** (la primera corrida sobre el corpus completo):

  **`data/graph.json`: 16 nodos, 14 aristas — 1/27 PDFs procesados. Faltan 26.**

  **Por qué va lento:** el tier gratuito de Groq tiene un tope de **100,000 tokens/día por modelo** (`llama-3.3-70b-versatile`). Sacarle entidades/relaciones a los 27 PDFs completos no alcanza en una sola sentada — hay que hacerlo en varias tandas, esperando a que se libere cupo entre una y otra.

  **No se pierde nada entre intentos**: `indexer/run.py` guarda `graph.json` después de cada PDF (no solo al final) y es diff-aware — cada vez que se reintenta, retoma automáticamente donde quedó, no repite los PDFs ya procesados.

  Se evaluó usar `llama-3.1-8b-instant` (tiene presupuesto de tokens separado, más rápido) para terminar antes, pero sus relaciones tienen errores reales (ej. "GPT-3 es parte de LangGraph") — se descartó a favor de mantener la calidad con el modelo de 70B, aceptando que el bootstrap tome varias sesiones.

  **Para retomar:** `cd mcp-asistente-curso && python3 -m indexer.run` — si Groq todavía no tiene cupo, corta limpio con un mensaje claro (sin perder progreso); si tiene, sigue por donde quedó.

## Por hacer

- Terminar el bootstrap del grafo (26 PDFs restantes, sujeto al límite diario de Groq).
- **Fase 4 — Retrieval híbrido**: fusión vector+grafo, reranker, tool `buscar_contenido` funcionando localmente.
- **Fase 5 — MCP server remoto**: transporte `streamable-http`, auth, `instructions` del servidor, deploy a Cloud Run.
- **Fase 6 — GitHub Actions**: `index.yml` (diff-aware) y `deploy-mcp-server.yml`.
- **Fase 7 — Pruebas/evaluaciones**: tool `detalle_pruebas` (reutiliza el retrieval de la Fase 4).
- **Fase 8 — Observabilidad**: Supabase + `reportar_interaccion` + `eval/judge.py` (LLM-as-judge) + cron diario.
- **Fase 9 — Documentación**: README de conexión para estudiantes.

Ver `plan.md` §8 para el roadmap completo con detalle de cada fase.
