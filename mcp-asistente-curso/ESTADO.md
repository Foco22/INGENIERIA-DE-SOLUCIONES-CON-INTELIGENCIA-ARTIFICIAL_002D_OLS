# Estado del proyecto

Resumen rápido de dónde vamos y qué falta — el detalle de diseño está en `plan.md`.

## 🟢 Corriendo en producción

**`https://mcp-asistente-curso-99135830306.northamerica-northeast1.run.app/mcp`**

Probado de punta a punta contra el servidor real desplegado: auth con bearer token, las 3 tools (`buscar_contenido`, `detalle_pruebas`, `reportar_interaccion`) responden bien, logueo en Supabase real funcionando. Latencia real: **~1.6s en frío (cold start), ~1.0s con el contenedor caliente**.

Para conectarse: transporte `streamable-http`, header `Authorization: Bearer <MCP_AUTH_TOKENS>` (ver `.env`).

## Hecho — Fases 0 a 8, todas probadas contra servicios reales

- **Fase 0-3**: setup, ingesta (27 PDFs), chunking + embeddings (382 chunks), grafo de conocimiento (406 nodos, 494 aristas, DeepSeek).
- **Fase 4 — Retrieval híbrido**: `server/retrieval.py` (vector + grafo). Embeddings vía OpenAI (`text-embedding-ada-002`), sin reranker.
- **Fase 5 — MCP server**: `server/main.py` (SDK `mcp` 2.0, `streamable-http`) + `server/auth.py` (bearer token + rate limit por IP).
- **Fase 6 — GCS + CI/CD**: `utils/gcs.py` contra `gs://mcp-douc` (proyecto `duocuc-493611`). Workflows: `index-mcp-asistente-curso.yml`, `deploy-mcp-server.yml`, `eval-judge-mcp-asistente-curso.yml`. Service account `mcp-asistente-curso-ci@duocuc-493611` con los roles necesarios. **Deploy corrido y verificado en Cloud Run.**
- **Fase 7 — Pruebas**: `detalle_pruebas` en `server/tools.py` (junto a las demás tools, no en archivo aparte).
- **Fase 8 — Observabilidad**: tabla `interacciones` en Supabase, `utils/supabase.py`, `eval/judge.py` (LLM-as-judge con DeepSeek). Las 3 tools loguean y devuelven `interaccion_id`.

**62/62 tests pasan** (sin contar `test_ingest.py`, lento, no relacionado).

**Bugs reales encontrados y arreglados en el camino a producción:**
- `supabase-py` 2.8.0 no soporta las keys nuevas de Supabase (`sb_secret_`/`sb_publishable_`) — actualizado a `>=2.10`.
- La `sb_publishable_` (anon) de este proyecto no logra insertar pese a RLS correcta (401 sin causa clara) — **el server usa temporalmente `SUPABASE_SERVICE_ROLE_KEY` para todo** (más privilegio del que debería tener sobre esa tabla). Pendiente investigar y volver a separar en dos keys — no bloquea el uso normal.
- `server/retrieval.py` no manejaba un índice vacío (`data/chunks.parquet` sin filas) — arreglado.
- **Proyecto GCP equivocado a mitad de camino**: la primera service account se creó en `paes-484217` (el default de `gcloud config`), pero el bucket `gs://mcp-douc` vive en `duocuc-493611`. Corregido: SA recreada en el proyecto correcto, APIs habilitadas, key regenerada.
- **`GITHUB_TOKEN` sin permiso de escritura**: `index-mcp-asistente-curso.yml` fallaba con 403 al comitear `data/markdown/` (el token automático es de solo lectura por default) — se agregó `permissions: contents: write`.
- **`MCP_AUTH_TOKENS` mal cargado en GitHub** (el de pruebas locales en vez del de producción) — corregido, y de paso se simplificó a **un solo token** (local = producción, ver `.env`), en vez de dos (`MCP_AUTH_TOKENS` / `MCP_AUTH_TOKENS_PROD`) que solo generaban confusión.
- **`HTTP 421 Invalid Host header`**: el SDK `mcp` tiene protección anti-DNS-rebinding activada por default, que solo confía en `localhost` — rechazaba cualquier request al hostname real de Cloud Run. Se desactivó explícitamente (`enable_dns_rebinding_protection=False`) porque `AuthMiddleware` ya exige bearer token en cada request, la protección era redundante.

## Por hacer (no bloquea nada de lo anterior)

- Investigar por qué la `sb_publishable_` key de Supabase no puede insertar (ver "Bugs" arriba) y volver a separar las keys del server (insert-only) vs. `eval/judge.py` (select/update).
- **Fase 9 — Documentación**: README de conexión para estudiantes (`claude mcp add --transport http ...`, con la URL de arriba y el bearer token).

Ver `plan.md` §8 para el roadmap completo con detalle de cada fase.
