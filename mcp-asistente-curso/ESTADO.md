# Estado del proyecto

Resumen rápido de dónde vamos y qué falta — el detalle de diseño está en `plan.md`.

## Hecho — todo el código, probado localmente contra servicios reales

- **Fase 0-3**: setup, ingesta (27 PDFs), chunking + embeddings (382 chunks), grafo de conocimiento (406 nodos, 494 aristas, DeepSeek).
- **Fase 4 — Retrieval híbrido**: `server/retrieval.py` (vector + grafo). Embeddings vía OpenAI (`text-embedding-ada-002`), sin reranker. ~650-700ms por búsqueda.
- **Fase 5 — MCP server**: `server/main.py` (SDK `mcp` 2.0, `streamable-http`) + `server/auth.py` (bearer token + rate limit por IP).
- **Fase 6 — GCS + CI/CD**: `utils/gcs.py` probado contra `gs://mcp-douc` real. Workflows: `index-mcp-asistente-curso.yml`, `deploy-mcp-server.yml`, `eval-judge-mcp-asistente-curso.yml`. Service account `mcp-asistente-curso-ci@duocuc-493611` creada con los roles necesarios (proyecto GCP correcto: **`duocuc-493611`**, no `paes-484217` — el bucket vivía ahí, se corrigió a mitad de camino, ver "Bugs" abajo).
- **Fase 7 — Pruebas**: `detalle_pruebas` en `server/tools.py` (junto a las demás tools, no en archivo aparte — corregido a pedido tuyo).
- **Fase 8 — Observabilidad**: tabla `interacciones` en Supabase (real, `eval/schema.sql`), `utils/supabase.py`, `eval/judge.py` (LLM-as-judge con DeepSeek). Las 3 tools MCP (`buscar_contenido`, `detalle_pruebas`, `reportar_interaccion`) probadas de punta a punta con un cliente MCP real + Supabase real: insertan y actualizan filas correctamente.

**Todos los tests pasan: 62/62** (sin contar `test_ingest.py`, lento, no relacionado con estos cambios).

**Bugs reales encontrados y arreglados en el camino:**
- `supabase-py` 2.8.0 no soporta las keys nuevas de Supabase (`sb_secret_`/`sb_publishable_`) — actualizado a `>=2.10`.
- La `sb_publishable_` (anon) de este proyecto no logra insertar pese a RLS correcta (401 sin causa clara) — **el server usa temporalmente `SUPABASE_SERVICE_ROLE_KEY` para todo** (más privilegio del que debería tener sobre esa tabla). Pendiente investigar y volver a separar en dos keys cuando haya tiempo — no bloquea el uso normal.
- `server/retrieval.py` no manejaba un índice vacío (`data/chunks.parquet` sin filas) — arreglado.
- **Proyecto GCP equivocado a mitad de camino**: armé la primera service account + roles en `paes-484217` (el que tenía seteado por default en `gcloud config`), pero el bucket `gs://mcp-douc` en realidad vive en `duocuc-493611` — el `describe` contra `paes-484217` funcionaba igual porque mi cuenta es owner en los dos proyectos, no porque el bucket estuviera ahí. Se corrigió: SA vieja borrada, SA nueva creada en `duocuc-493611` con los mismos 4 roles, APIs de Cloud Run/Artifact Registry habilitadas ahí, key nueva generada. `gcp-sa-key.json` y la tabla de secrets ya reflejan el proyecto correcto.

## Qué falta para que corra en Google — un solo paso: los secrets en GitHub

Todo el código está listo y probado. Lo único que falta es configurar **GitHub → Settings → Secrets and variables → Actions** con estos 8 secrets, y hacer el primer push a `main`:

| Secret | Valor |
|---|---|
| `GCP_PROJECT_ID` | `duocuc-493611` |
| `GCP_SA_KEY` | contenido de `mcp-asistente-curso/gcp-sa-key.json` (generado, gitignoreado — borralo del disco una vez pegado) |
| `DEEPSEEK_API_KEY` | ver `.env` |
| `OPENAI_API_KEY` | ver `.env` |
| `MCP_AUTH_TOKENS` | ver `.env` → `MCP_AUTH_TOKENS_PROD` |
| `SUPABASE_URL` | ver `.env` |
| `SUPABASE_SERVICE_ROLE_KEY` | ver `.env` |

Con eso puesto, el primer push a `main` que toque `server/**` dispara `deploy-mcp-server.yml` (build + deploy a Cloud Run), y cualquier cambio en un PDF de clase/evaluación dispara `index-mcp-asistente-curso.yml` (reindexar + publicar a GCS + reiniciar Cloud Run para que recoja el índice nuevo).

## Por hacer (no bloquea el deploy)

- Investigar por qué la `sb_publishable_` key de Supabase no puede insertar (ver arriba) y volver a separar las keys del server (insert-only) vs. `eval/judge.py` (select/update).
- **Fase 9 — Documentación**: README de conexión para estudiantes (`claude mcp add --transport http ...`, incluye el bearer token de producción).

Ver `plan.md` §8 para el roadmap completo con detalle de cada fase.
