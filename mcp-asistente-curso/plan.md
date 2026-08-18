# Plan: MCP Server — Asistente del Curso

Servidor MCP remoto que responde preguntas de **contenido/materia** (RAG híbrido vector+grafo sobre los PDFs del curso) y de **pruebas/evaluaciones** (pauta, indicadores de logro, requisitos), accesible por los estudiantes desde sus propios equipos.

## 1. Objetivo

- Dar a cualquier estudiante del curso un MCP server al que conectar su Claude (Desktop/Code) y preguntar por el contenido de las clases, resúmenes por tema, y qué cubren las pruebas/evaluaciones.
- Mantener el índice de contenido siempre al día automáticamente cuando se actualiza el repositorio, sin intervención manual.

## 2. Alcance

**Incluido (fase 1):**
- Pipeline de indexación (PDF → Markdown → chunks + grafo de conocimiento).
- Retrieval híbrido (vectorial + grafo), entregado como contexto **combinado** (fragmentos + relaciones de grafo, no una sola lista fusionada — ver §4.2).
- MCP server remoto (streamable-http) desplegado en Cloud Run, con `buscar_contenido` (contenido/materia) y `detalle_pruebas` (pruebas/evaluaciones) — ambas sobre la misma infraestructura de retrieval (§4.4).
- Actualización automática del índice vía GitHub Actions cuando cambia el repo.

**Fuera de alcance:**
- Autenticación por estudiante individual (se parte con un token compartido).
- UI propia (el "cliente" es Claude Desktop/Code de cada estudiante).
- Tools de calendario general de clases (`proxima_clase`, `calendario_entre`, `entregables_pendientes`) — se descartaron. Sin fuente de datos confirmada y sin fecha para resolverlo, no vale la pena diseñar/mantener esa parte del server. Se puede retomar más adelante si aparece una fuente clara.

## 3. Arquitectura general

```
┌─────────────────────────────┐        ┌──────────────────────────────────────┐
│ GitHub Actions (index.yml)  │        │ Cloud Run (mcp-server, streamable-http)│
│                              │        │                                        │
│ 1. Detecta PDFs nuevos/      │  sube  │  Al arrancar / on-demand:              │
│    modificados (hash diff)   │──────▶ │  descarga índice más reciente de GCS   │
│ 2. PDF → Markdown             │  GCS   │                                        │
│ 3. Chunking + embeddings      │ bucket │  Tools MCP:                           │
│ 4. Extracción de grafo (LLM)  │        │   - buscar_contenido(query, ...)      │
│ 5. Publica index/vN/* en GCS  │        │     → fragmentos + conceptos_relacionados │
│                              │        │   - detalle_pruebas(query, ...)       │
└─────────────────────────────┘        │   - reportar_interaccion (opcional)    │
                                        └──────────────────────────────────────┘
                                                        ▲
                                                        │ streamable-http + Bearer token
                                                        │
                                          Claude Desktop / Claude Code
                                          de cada estudiante (conexión remota)
```

## 4. Componentes

### 4.1 Pipeline de indexación (`indexer/`)

1. **Ingesta — PDF → Markdown**: `pymupdf4llm` (con OCR vía Tesseract — los PDFs del curso traen texto incrustado como imagen, típico de exportaciones de Google Slides, así que la extracción de texto plano no lo agarra pero el OCR sí) por cada PDF de `Experiencia de Aprendizaje */Clase */` **y también** los 3 PDFs de `evaluaciones/` (uno por Experiencia — pauta, instrucciones, indicadores de logro de cada evaluación parcial). Salida: `.md` con headings preservados, etiquetado con `tipo: clase | evaluacion` según de dónde vino, **comiteado al repo** en `data/markdown/` (mismo layout que la fuente) — decisión explícita para poder revisar la conversión directo en GitHub sin correr el pipeline. Validado sobre el corpus completo (27 PDFs): ver §4.1 abajo.
   > Se descartó `docling` (elección original del plan): su árbol de dependencias (torch, easyocr, transformers) tardó más de 30s solo en resolverse al instalar, e impráctico de correr en CI sin un salto grande en tiempo/imagen. `pymupdf4llm` se instala en segundos y da buenos resultados con OCR — si algún PDF con estructura muy compleja sale mal más adelante, se puede reevaluar puntualmente.
2. **Diff-aware processing**: `manifest.json` con hash sha256 por PDF. Solo se reprocesan (conversión, embeddings, grafo) los archivos nuevos o modificados desde la última corrida — evita recomputar todo el repo en cada push.
3. **Chunking**: split por heading (cualquier nivel — en la práctica los `#`/`##`/`###` del OCR **no son jerárquicos de verdad**, dependen del tamaño de fuente detectado en cada slide, no de una estructura lógica; la jerarquía real `Experiencia → Clase` sale de la metadata del PDF, no de anidar niveles de heading). Secciones muy cortas se funden con la siguiente, secciones muy largas se dividen por párrafo. Umbrales calibrados sobre el corpus real (27 PDFs, 394 secciones): 382 chunks finales, sin vacíos, sin ids duplicados.
4. **Embeddings**: **OpenAI** (`text-embedding-ada-002`) sobre cada chunk → export a Parquet (`data/chunks.parquet`, gitignored — no se comitea un binario de vector DB; se reconstruye a partir del export). Diff-aware de punta a punta: un PDF sin cambios ni siquiera se re-chunkea ni re-embebe, sus filas del parquet quedan intactas. Validado con búsqueda vectorial simple (coseno) sobre los 382 chunks reales: resultados correctos y bien acotados por `tipo` (clase vs. evaluación).
   > **Cambio de proveedor:** se probó primero local con `fastembed`/ONNX (`intfloat/multilingual-e5-large`, gratis, sin API key). Funcionaba, pero el modelo (>1GB) se descarga a un caché efímero — cada vez que se pierde (reboot local, contenedor nuevo en Cloud Run) la primera query paga varios minutos de descarga antes de responder, inaceptable para un servidor que debe responder rápido a preguntas de estudiantes. Se migró a la API de OpenAI: sin modelo que cargar, costo por token insignificante para este corpus, latencia real medida ~650-700ms por búsqueda completa (embed de la query + similitud + traversal de grafo, ver §4.2).
5. **Grafo de conocimiento**: pase de extracción con LLM sobre el `.md` de cada PDF → entidades (conceptos, frameworks, técnicas) y relaciones entre ellas. Merge incremental en `graph.json` (`networkx`, serializado) — se guarda **después de cada PDF**, no solo al final, para no perder progreso si se corta a mitad de camino. LLM: **DeepSeek**, `deepseek-chat`, vía el SDK `openai` apuntando a `base_url=https://api.deepseek.com` (la API de DeepSeek es compatible con el formato OpenAI). Corre solo en el pipeline de indexación, no por pregunta de estudiante.
   > **Cambio de proveedor:** se probó primero con Groq (`llama-3.3-70b-versatile`, gratis), pero su tier gratuito tiene tope de **100,000 tokens/día por modelo** — sacarle entidades/relaciones a los 27 PDFs completos de una sentada no alcanzaba (solo 1/27 en la primera sesión). Se migró a DeepSeek: pago por token pero sin tope diario práctico para este corpus y costo de fracciones de centavo (~85K tokens totales estimados); con eso el bootstrap completo (27/27 PDFs, 406 nodos, 494 aristas) corrió en una sola sesión. El guardado incremental + diff-aware se mantiene igual (retoma solo lo que falta si algo corta a mitad de camino) — ver `ESTADO.md`.
6. **Publicación**: sube `manifest.json`, `chunks.parquet`, `graph.json` a `gs://<bucket>/index/latest/` (versionado también en `index/<run_id>/` para poder hacer rollback).

**Validación de la conversión PDF → Markdown (paso 1):**
- **Chequeos automáticos** (test `pytest`, corre en CI cuando cambia `indexer/ingest.py`): output no vacío, longitud de texto no muy por debajo de un baseline de extracción plana (`pypdf`), al menos N headings, sin basura de mala extracción (`�`, texto mezclado), tablas markdown presentes si el PDF tenía tablas.
- **Revisión manual puntual**: 2-3 PDFs representativos (texto simple, con tablas, con diagramas) comparados a mano contra su `.md` — se repite solo cuando cambia la librería de conversión, no por cada PDF nuevo.
- **Chequeo a escala (opcional, DeepSeek vía `utils/llm.py`)**: mismo patrón de LLM-as-judge de §4.5, aplicado a comparar texto plano vs markdown cuando ya no es viable revisar todo a mano.

### 4.2 Retrieval híbrido (`server/retrieval.py`)

**Dos fuentes de retrieval, salida combinada, expuestas por tool según la intención.** `explorar_grafo` y `resumen_clase` como tools separadas de `buscar_contenido` quedaron descartadas — para el estudiante, "buscar un concepto", "ver cómo se relaciona con otro" y "resumen de una clase" son la misma intención (pregunta de materia de clases), así que forzar al modelo del cliente a elegir entre tres tools solo agregaba ambigüedad. Las pruebas/evaluaciones (§4.4) sí quedan en su propia tool (`detalle_pruebas`) porque es una intención distinta y bien delimitada ("qué entra en la prueba" vs. "explícame un concepto") — pero **por debajo usa exactamente esta misma función de retrieval**, no un pipeline aparte, solo con `tipo="evaluacion"` fijo en vez de `tipo="clase"`. Por cada llamada (de cualquiera de las dos tools) corren **dos búsquedas independientes sobre la misma query**:

- **(a) Vectorial**: embedding de la query (OpenAI) → top-N chunks por similitud de coseno (opcionalmente filtrado por `experiencia`/`clase` si el estudiante pregunta por una clase puntual — esto reemplaza lo que hacía `resumen_clase`). Sin reranker: se probó un cross-encoder local (`bge-reranker-base` vía `fastembed`) pero se sacó por el mismo problema de costo de arranque que el embedder (ver §4.1, paso 4) — el orden final queda directo por similitud de coseno.
- **(b) Grafo**: se identifican conceptos mencionados en la query (match de texto contra los nombres de nodos de `graph.json`, sin LLM — ver `indexer/graph.py:normalize_concepto`) → traversal de vecinos directos, entrantes y salientes (esto reemplaza lo que hacía `explorar_grafo`).

(a) y (b) **no compiten en el mismo ranking** — son un tipo de información distinta (texto vs. relaciones entre conceptos) — así que se devuelven aparte. La tool entrega **ambas fuentes explícitas en la salida**: `fragmentos` (de la búsqueda vectorial, con cita `experiencia/clase/archivo`) y `conceptos_relacionados` (de la búsqueda en grafo), para que el modelo del cliente tenga las dos señales al armar su respuesta, en vez de tener que adivinar cuál tool traía qué.

> El embedding de la pregunta corre vía API (OpenAI, igual que la indexación — mismo modelo en los dos lados, ver §4.1 paso 4) — la llamada a LLM (DeepSeek, extracción de grafo) sigue corriendo solo en el pipeline de indexación, no por cada pregunta de un estudiante. Latencia real medida end-to-end (embed + similitud + traversal de grafo): ~650-700ms por búsqueda.

### 4.3 MCP Server (`server/main.py`)

> **Quién genera la respuesta final:** el servidor MCP **no redacta respuestas en lenguaje natural**. Por diseño del protocolo, un servidor MCP solo expone *tools* que devuelven datos (texto/JSON) cuando el cliente las invoca. Cada tool de este servidor devuelve **fragmentos recuperados + su cita** (`experiencia/clase/archivo`), no una respuesta compuesta. El modelo que interpreta esos fragmentos y redacta la respuesta al estudiante es el LLM del lado del cliente — el que el propio estudiante tenga conectado en su Claude Desktop/Code (o cualquier otro cliente MCP que use). Consecuencia práctica: **no se necesita ningún LLM corriendo en el servidor en tiempo de consulta** — el embedding de la query es una llamada de API liviana, no un LLM generativo (ver §4.2); DeepSeek solo se usa offline, en el pipeline de indexación (§4.1), nunca por pregunta de estudiante.

- SDK oficial `mcp` (Python), transporte `streamable-http`.
- **Quién decide qué tool llamar**: el LLM del cliente, no el servidor — el servidor solo publica nombre/descripción/schema de cada tool, y el modelo elige según eso al leer la pregunta del estudiante. Consecuencia práctica: las descripciones deben ser **prescriptivas sobre cuándo usarlas**, no solo decir qué hacen.

**Tools fase 1 (contenido/materia + pruebas — ninguna bloqueada):**

Ambas tools comparten la misma infraestructura de retrieval (`server/retrieval.py`, §4.2) — no hay dos pipelines ni dos índices. La única diferencia es qué `tipo` de contenido queda fijo en cada una, y eso las hace más fáciles de distinguir para el modelo del cliente que un parámetro `tipo` que tendría que acordarse de setear.

| Tool | Parámetros | Devuelve | Descripción (texto que ve el modelo del cliente) |
|---|---|---|---|
| `buscar_contenido` | `query: str`, `experiencia: str` opcional, `clase: str` opcional | `interaccion_id`, `fragmentos: [{texto, experiencia, clase, archivo, score}]`, `conceptos_relacionados: [{nodo, tipo_relacion, concepto_relacionado, clase_donde_aparece}]` | Busca contenido de las clases del curso — conceptos de materia, relaciones entre temas, o el contenido de una clase puntual (ej. "qué es RAG", "cómo se relaciona con prompt engineering", "qué vimos en la clase 2.3"). Si la pregunta es sobre una clase específica, pasa `experiencia`/`clase`. No cubre pruebas/evaluaciones (para eso usa `detalle_pruebas`) ni fechas de calendario. |
| `detalle_pruebas` | `query: str`, `experiencia: str` opcional | `interaccion_id`, `fragmentos: [{texto, experiencia, archivo, score}]` | Busca información sobre las pruebas/evaluaciones del curso: pauta, indicadores de logro, requisitos de entrega, % de ponderación, cronograma por semana. Úsala para preguntas tipo "qué entra en la Evaluación Parcial 1", "cómo se evalúa el encargo", "qué debo entregar". No da fechas de calendario absolutas — los PDFs de evaluación solo tienen semanas relativas del cronograma, no fechas concretas (no hay tools de calendario general para eso, se descartaron — §2). |

Ambas insertan en Supabase (§4.5) y devuelven `interaccion_id`.

**Tool de observabilidad, opcional/best-effort (§4.5):**

| Tool | Parámetros | Devuelve | Descripción |
|---|---|---|---|
| `reportar_interaccion` | `interaccion_id: str`, `respuesta: str`, `util: bool \| None` | confirmación | Reporta la respuesta final que le diste al estudiante para esta interacción. Llámala **una sola vez por turno**, inmediatamente después de responder. Si en ese turno usaste más de una tool de este servidor (ej. `buscar_contenido` y luego `detalle_pruebas`), usa el `interaccion_id` de la **última** que llamaste — no hace falta reportar cada una por separado. |

**Por qué queda así:** el servidor no tiene forma de saber por sí solo cuál de varias llamadas en un mismo turno corresponde a la respuesta final (§4.5) — resolver eso automáticamente requeriría que el servidor mantenga estado de sesión entre llamadas, lo que complica el diseño sin necesidad. Es más simple documentarlo así: un `reportar_interaccion` por turno, contra el último `interaccion_id`. Sigue siendo best-effort (depende de que el cliente lo llame), pero al menos sin ambigüedad sobre cuál id usar.
- Middleware de auth: valida `Authorization: Bearer <token>` contra token(s) configurados (env var / secret). Rate limit básico por token.
- Al iniciar el proceso (o vía tool interna de refresh), descarga `index/latest/` de GCS a memoria/disco local del contenedor.
- **`instructions` del servidor MCP**: al declarar el `Server` en `server/main.py`, se setea el campo `instructions` con el texto que le pide al modelo del cliente llamar a `reportar_interaccion` una vez por turno (§4.5, mecanismo 1 — el automático). La mayoría de los clientes MCP (Claude Desktop, Claude Code) lo agregan solos al contexto al conectarse, sin que el estudiante configure nada.

### 4.4 Pruebas/evaluaciones (fase 1, confirmado)

Los datos están en `evaluaciones/` en la raíz del repo: 3 PDFs, uno por Experiencia de Aprendizaje, cada uno con instrucciones, pauta de evaluación, indicadores de logro, % de ponderación y cronograma por semana del encargo/evaluación correspondiente. Es texto/estructura igual que las clases (no un archivo de datos tabulares), así que **no necesita pipeline de indexación aparte**: entra al mismo `indexer/ingest.py` → `chunk.py` → embeddings (§4.1), etiquetado `tipo: evaluacion` y asociado a su `experiencia` (sin `clase` puntual, porque aplica a toda la Experiencia). Sí se expone como **tool MCP separada** (`detalle_pruebas`, §4.3) — misma infraestructura de retrieval por debajo, pero como tool distinta para que el modelo del cliente la identifique más fácil que un parámetro que tendría que recordar setear.

**Límite importante:** las fechas en esos PDFs son **semanas relativas del cronograma** ("semana 2", "semana 6"), no fechas de calendario absolutas. `detalle_pruebas` puede responder bien "qué entra en la Evaluación Parcial 1" o "cómo se evalúa", pero **no** "en qué fecha exacta es" — no hay tools de calendario general para resolver eso (se descartaron, §2).

### 4.5 Observabilidad — logging y evaluación de calidad (`server/tools.py` + `utils/supabase.py`)

**Qué puede ver el servidor y qué no.** El servidor solo se activa cuando el cliente llama a una tool — ve la query y lo que él mismo devuelve (los fragmentos, §4.3). **No ve la respuesta final que el LLM del estudiante redacta** — eso pasa enteramente del lado del cliente y nunca vuelve al servidor. Esto define dos niveles de visibilidad:

1. **Siempre disponible, sin nada adicional:** cada invocación de `buscar_contenido` / `detalle_pruebas` — query, fragmentos y/o conceptos_relacionados recuperados + score de similitud, timestamp, latencia.
2. **Opcional / best-effort:** la respuesta final que recibió el estudiante — solo si su asistente decide llamar a una tool adicional para reportarla. No se puede forzar, depende de que el cliente coopere.

**Registro de interacciones → Supabase (nivel 1)**
- Al final de cada invocación de tool de consulta (`buscar_contenido`, `detalle_pruebas`), el server hace un **insert directo a una tabla en Supabase** (Postgres gratis, tier free de sobra para este volumen) — fire-and-forget, no bloquea la respuesta al cliente.
- Esquema propuesto (`interacciones`):

  | columna | tipo | notas |
  |---|---|---|
  | `id` | `uuid`, pk | `default gen_random_uuid()` |
  | `created_at` | `timestamptz` | `default now()` |
  | `tool` | `text` | `buscar_contenido` \| `detalle_pruebas` \| ... |
  | `query` | `text` | |
  | `fragmentos` | `jsonb` | `[{experiencia, clase, archivo, score}, ...]` (buscar_contenido) |
  | `conceptos_relacionados` | `jsonb`, nullable | resultado del lado de grafo (solo buscar_contenido) |
  | `latencia_ms` | `int` | |
  | `respuesta` | `text`, nullable | solo si el cliente reporta (ver nivel 2) |
  | `util` | `boolean`, nullable | idem |
  | `reportado_at` | `timestamptz`, nullable | idem |

- Sin identidad de estudiante (token compartido — consistente con §5.4).
- Credenciales: `SUPABASE_URL` + una key con permiso **solo de insert** en esta tabla (Row Level Security: policy de insert acotada al rol que usa el server; el `service_role` completo no debería vivir en el contenedor Cloud Run). Se agregan como secrets/env vars.
- Dashboard: te conectas directo a la tabla desde **Supabase Studio** (ya trae vistas y gráficos básicos) o cualquier BI que prefieras (Metabase, Grafana, etc.) apuntando al Postgres de Supabase — la tabla es la fuente de datos, no hace falta construir nada adicional del lado del servidor para verla.

**Tool opcional para capturar la respuesta final (nivel 2)**
- Cada tool de consulta (`buscar_contenido`, `detalle_pruebas`) devuelve el `interaccion_id` de la fila que insertó, junto con su resultado.
- `reportar_interaccion(interaccion_id: str, respuesta: str, util: bool | None)` hace un `UPDATE` sobre esa misma fila (`respuesta`, `util`, `reportado_at`). No es garantizado, pero cuando se usa da visibilidad real sobre qué está diciendo el modelo del estudiante, no solo qué material se le entregó.

**Cómo se le avisa al modelo del cliente que la llame** (de más a menos automático — conviene usar las tres):
1. **`instructions` del servidor MCP (principal)**: al inicializar la conexión, el servidor manda un texto de instrucciones generales que la mayoría de los clientes (Claude Desktop, Claude Code) agregan solos al contexto del modelo, sin que el estudiante configure nada — ahí va la instrucción de llamar a `reportar_interaccion` una vez por turno, con el `interaccion_id` de la última tool usada.
2. **Descripción de `buscar_contenido`/`detalle_pruebas` (refuerzo)**: un recordatorio corto también en la descripción de cada tool, para una segunda oportunidad de que el modelo lo note.
3. **README de conexión (respaldo manual)**: documentado para el estudiante que quiera agregarlo a mano a su propio system prompt, por si su cliente no soporta bien el punto 1.

**Evaluación de calidad — "¿cómo ver si responde bien?"**
- **Proxy de calidad del retrieval (siempre disponible):** cualquier query cuyo mejor score de similitud quede bajo un umbral es señal automática de que el material no cubre bien esa pregunta — se puede calcular directo en el dashboard con una query SQL sobre `fragmentos`, sin nada adicional.
- **LLM-as-judge por lotes (DeepSeek, offline):** `eval/judge.py`, corrido periódicamente vía GitHub Actions con cron (§5.5), lee directo de Supabase (`select * from interacciones where evaluado_at is null limit N`), le pide a DeepSeek evaluar (a) si los fragmentos recuperados son relevantes a la pregunta, y (b) cuando exista `respuesta` reportada, si está bien fundamentada en esos fragmentos — y escribe el resultado de vuelta en Supabase (tabla `evaluaciones`, o columnas adicionales en `interacciones`), para que el dashboard también pueda filtrar/graficar por esos scores. Reutiliza el mismo proveedor ya usado para el grafo (§4.1) — no agrega dependencia nueva, costo marginal (pago por token, muy barato).

> Esto encaja directo con lo que ya cubre el curso (Experiencia de Aprendizaje 3 — Observabilidad, trazabilidad y procesamiento de logs), así que el diseño reutiliza deliberadamente ese enfoque en vez de improvisar algo distinto.

## 5. Infraestructura y despliegue

### 5.1 GitHub Actions — `index.yml`
- Trigger: `push` a `main` con `paths` filtrados a `**/*.pdf` y carpetas `Clase */**`, más `workflow_dispatch`.
- Corre el pipeline de indexación (§4.1) y publica en GCS.
- Secrets requeridos: credenciales de GCP (auth ya usada en `deploy-cloud-run.yml`), `DEEPSEEK_API_KEY` (extracción de grafo) y `OPENAI_API_KEY` (embeddings, §4.1 paso 4 / §7).

### 5.2 GitHub Actions — `deploy-mcp-server.yml`
- Trigger: `push` a `main` con `paths` filtrados a `mcp-asistente-curso/server/**`.
- Build de imagen Docker, push a Artifact Registry, deploy a Cloud Run — mismo patrón que `.github/workflows/deploy-cloud-run.yml` ya existente en el repo.
- El server no necesita rebuild cuando solo cambia el índice (eso lo resuelve la descarga desde GCS), así que este workflow solo se dispara con cambios de código del server.

### 5.3 Cloud Run
- Servicio `mcp-asistente-curso`, región consistente con el resto del repo (`northamerica-northeast1`).
- Env vars: bucket GCS del índice, token(s) de auth, `OPENAI_API_KEY` (embeddings en tiempo de consulta, §4.2).
- `--allow-unauthenticated` a nivel de Cloud Run (el control de acceso real lo hace el middleware de bearer token de la app, no IAM — así los estudiantes no necesitan cuentas de GCP).

### 5.4 Auth y rate limiting
- **Decidido**: un único bearer token compartido por todos los estudiantes del curso (mismo token para todos, no uno por persona). Se distribuye vía el README/instrucciones de conexión.
- Como no hay token por estudiante, el rate limit no puede ser por identidad — se aplica por IP para evitar que un abuso puntual tumbe el servicio o dispare costos.
- Si más adelante se necesita trackear uso individual o revocar acceso a una sola persona, hay que migrar a tokens por estudiante (queda anotado como mejora futura, no bloquea la Fase 5).

### 5.5 GitHub Actions — `eval-judge.yml` (observabilidad, cron)
- Trigger: `schedule` — **todos los días a las 8am (hora de Chile)** — más `workflow_dispatch` para correrlo manualmente cuando se quiera revisar antes.
  - GitHub Actions solo acepta cron en UTC, así que el `cron` queda como `0 12 * * *` (8am `America/Santiago` en horario estándar, UTC-4). Con el cambio de hora de verano en Chile (UTC-3) el disparo cae ~7am local en vez de 8am — desfase menor, no crítico para un reporte de calidad; se puede ajustar el offset dos veces al año si molesta.
- Corre `eval/judge.py` (§4.5): lee interacciones no evaluadas directo de Supabase, corre el LLM-as-judge con DeepSeek, escribe los scores de vuelta en Supabase.
- Secrets requeridos: `SUPABASE_URL` + key con permiso de select/update (distinta de la key de solo-insert que usa el server en Cloud Run) y `DEEPSEEK_API_KEY` (mismo secret que `index.yml`).
- Sin salida propia que gestionar — el dashboard (Supabase Studio u otro BI conectado al Postgres) ya refleja los scores apenas se escriben.

## 6. Estructura de carpetas propuesta

**Criterio de diseño:** todo lo que se usa en más de un módulo (embeddings, cliente LLM/DeepSeek, GCS, Supabase, los "shapes" de datos) vive en `utils/` — nada de reimplementar el mismo cliente dos veces. Cada módulo (`indexer/`, `server/`, `eval/`) solo tiene lo que le pertenece exclusivamente a esa etapa, con nombres consistentes por etapa del pipeline (sustantivo/verbo corto, sin mezclar convenciones). Los tests viven aparte, en `tests/`, espejando la estructura de módulos (`tests/indexer/test_chunk.py` para `indexer/chunk.py`, etc.) — `pytest.ini` fija `pythonpath = .` para que las importaciones absolutas (`from indexer.chunk import ...`) resuelvan sin importar desde dónde se invoque pytest.

```
mcp-asistente-curso/
├── plan.md
├── utils/                    # compartido entre indexer/, server/ y eval/ — evita duplicar clientes y esquemas
│   ├── __init__.py
│   ├── models.py                # dataclasses compartidas: Chunk, Fragmento, GraphNode, GraphEdge
│   ├── embeddings.py             # wrapper cliente OpenAI (embeddings, text-embedding-ada-002) — lo usa indexer Y server (§4.2)
│   ├── llm.py             # wrapper cliente DeepSeek (SDK openai) — lo usa indexer/graph.py (§4.1) Y eval/judge.py (§4.5)
│   ├── gcs.py                      # subir/bajar del bucket de índice — lo usa indexer (publicar) Y server (descargar al iniciar)
│   ├── supabase.py                  # insert/select/update sobre la tabla de interacciones — lo usa server (insert) Y eval (select+update)
│   └── paths.py                      # recorrer "Experiencia de Aprendizaje */Clase */" y extraer (experiencia, clase) de un path
├── indexer/
│   ├── __init__.py
│   ├── run.py                  # orquesta ingest+manifest+chunk+embeddings -> data/chunks.parquet (diff-aware, §4.1 pasos 1-4)
│   ├── ingest.py                 # PDF → Markdown (pymupdf4llm + OCR), escribe a data/markdown/
│   ├── chunk.py                    # Markdown → chunks (split por heading, sin asumir jerarquía real)
│   ├── graph.py                     # chunks → entidades/relaciones (usa utils/llm.py), merge en graph.json
│   └── manifest.py                   # hash sha256 por PDF, diff-aware processing (específico de esta etapa, no se comparte)
├── server/
│   ├── __init__.py
│   ├── main.py                 # entrypoint MCP streamable-http; setea `instructions` del Server (§4.3)
│   ├── retrieval.py              # búsqueda híbrida (usa utils/embeddings.py)
│   ├── tools.py                    # las 3 tools MCP (buscar_contenido, detalle_pruebas, reportar_interaccion); loguea a Supabase vía utils/supabase.py (§4.5)
│   └── auth.py                       # middleware bearer token
├── eval/
│   ├── __init__.py
│   └── judge.py                 # lee de Supabase, LLM-as-judge (usa utils/llm.py + utils/supabase.py)
├── tests/                     # espejo de la estructura de módulos — ver pytest.ini (pythonpath=.)
│   └── indexer/
│       ├── test_run.py           # tests de build_index (embeddings simulados, sin cargar el modelo real)
│       ├── test_ingest.py         # chequeos automáticos de la conversión, ver §4.1
│       ├── test_chunk.py           # tests del chunking (markdown sintético)
│       └── test_manifest.py         # tests del diff-aware processing (archivos sintéticos, sin OCR)
├── data/
│   ├── markdown/               # .md generados — SE COMITEA al repo (mismo layout que la fuente)
│   ├── manifest.json             # hash por PDF para diff-aware processing — gitignored
│   ├── chunks.parquet             # chunks + embeddings (382 filas validadas) — gitignored
│   └── graph.json                  # grafo de conocimiento (Fase 3) — gitignored
├── pytest.ini
├── Dockerfile
├── requirements.txt
└── .github/workflows/ (o entradas agregadas al .github/workflows/ raíz del repo)
    ├── index.yml
    ├── deploy-mcp-server.yml
    └── eval-judge.yml
```

## 7. Stack tecnológico

| Pieza | Elección | Motivo |
|---|---|---|
| PDF → Markdown | `pymupdf4llm` (con OCR) | `docling` resultó impráctico de instalar (dependencias muy pesadas); `pymupdf4llm` es liviano y su OCR captura bien el texto incrustado como imagen que traen los PDFs del curso |
| Chunking | Split por heading (sin asumir jerarquía por nivel) | Los niveles `#`/`##`/`###` del OCR no son jerárquicos de verdad (dependen del tamaño de fuente del slide); la jerarquía real Experiencia/Clase ya viene de la metadata del PDF |
| Embeddings (indexación y query en caliente) | **OpenAI** (`text-embedding-ada-002`), API | Se probó local primero (`intfloat/multilingual-e5-large` vía `fastembed`/ONNX, gratis) — funcionaba, pero el modelo (>1GB) vive en un caché efímero; cada vez que se pierde, la primera query paga varios minutos de descarga, inaceptable en un servidor que debe responder rápido. Mismo modelo en indexación y query evita desalineamiento entre el espacio vectorial de índice y de consulta; costo por pregunta de estudiante insignificante |
| Grafo | `networkx` + extracción LLM | Suficiente para ~15-20 clases, sin infra de BD de grafos |
| LLM extracción de grafo | **DeepSeek** (`deepseek-chat`) | Pago por token pero muy barato, sin tope diario práctico; corre solo en CI (no por pregunta de estudiante); API compatible con el SDK de OpenAI, fácil de integrar. (Se probó Groq primero — gratis pero tope de 100K tokens/día/modelo insuficiente para el corpus completo en una sesión.) |
| Reranker | Ninguno — orden final por similitud de coseno directa | Se probó `BAAI/bge-reranker-base` local (vía `fastembed`) pero se sacó por el mismo problema de costo de arranque que el embedder local; sin equivalente de rerank en la API de OpenAI. Menos preciso que con cross-encoder, pero sin modelos locales que mantener |
| Server MCP | SDK `mcp` (Python) + `streamable-http` | Transporte remoto estándar del protocolo |
| Hosting | Cloud Run | Ya usado en el repo, mismo patrón de CD |
| Storage del índice | GCS bucket | Desacopla actualización de índice de redeploy del server |
| Registro de interacciones | Supabase (Postgres, tier gratis) | Insert por interacción, dashboard nativo (Studio) o BI externo apuntando al Postgres, sin infra propia que mantener |
| Evaluación de calidad | LLM-as-judge con DeepSeek | Lee/escribe directo en Supabase; reutiliza el mismo proveedor del pipeline de indexación |

## 8. Roadmap por fases

- [x] **Fase 0 — Setup**: estructura de carpetas, `requirements.txt`, Dockerfile base.
- [x] **Fase 1 — Ingesta**: `indexer/ingest.py` + `indexer/manifest.py` (diff-aware). Validado sobre el corpus completo (27 PDFs, todos pasan los chequeos automáticos de §4.1) y con un smoke test de dos corridas que confirma que los PDFs sin cambios se saltan.
- [x] **Fase 2 — Chunking + embeddings**: `indexer/chunk.py` + `utils/embeddings.py` + `indexer/run.py` (diff-aware, chunk+embed+export). Validado sobre el corpus completo: 382 chunks en `data/chunks.parquet`, búsqueda vectorial simple (coseno) probada con queries reales y resultados correctos. Nota de performance: el bootstrap inicial (embeber todo por primera vez) tardó ~13.5 min en CPU — costo único, las corridas siguientes solo re-embeben lo que cambió.
- [x] **Fase 3 — Grafo**: extracción de entidades/relaciones con LLM (DeepSeek) sobre el material ya convertido, merge incremental. Bootstrap completo sobre el corpus real: 406 nodos, 494 aristas, 27/27 PDFs.
- [x] **Fase 4 — Retrieval híbrido**: fusión vector+grafo, `server/retrieval.py` (con `fragmentos` + `conceptos_relacionados`, §4.2). Sin reranker (ver tabla de stack, §7). Validado con queries reales sobre el corpus completo: resultados correctos, latencia ~650-700ms end-to-end.
- [x] **Fase 5 — MCP server remoto**: `server/main.py` (SDK `mcp` 2.0, `streamable-http`, `instructions`), `server/auth.py` (bearer token + rate limit por IP). Probado de punta a punta con un cliente MCP real. Deploy a Cloud Run: workflow escrito (Fase 6), todavía no corrido — falta el primer push que lo dispare.
- [x] **Fase 6 — GCS + GitHub Actions**: `utils/gcs.py` (`publish_index`/`download_latest_index`), probado con el bucket real `gs://mcp-douc`. Workflows escritos: `.github/workflows/index-mcp-asistente-curso.yml` y `deploy-mcp-server.yml` (mismo patrón que `deploy-cloud-run.yml`). Service account dedicada creada (`mcp-asistente-curso-ci`) con los roles necesarios. Todavía no corrieron en CI de verdad.
- [x] **Fase 7 — Pruebas/evaluaciones**: `detalle_pruebas` en `server/tools.py` (tipo="evaluacion" fijo, reutiliza `server/retrieval.py`) — no en un archivo separado (`server/pruebas.py` se descartó, es la misma clase de tool que `buscar_contenido`, vive junto a ella).
- **Fase 8 — Observabilidad** (en progreso): tabla `interacciones` creada en Supabase (`eval/schema.sql`), `utils/supabase.py` (insert/select/update) probado contra el proyecto real, `buscar_contenido`/`detalle_pruebas` loguean cada llamada y devuelven `interaccion_id`, tool `reportar_interaccion` registrada. Falta: `eval/judge.py` (LLM-as-judge) y `eval-judge.yml` (cron). Nota de seguridad pendiente: por un problema no resuelto con la key pública nueva de Supabase (`sb_publishable_`, HTTP 401 pese a RLS correcta), el server usa temporalmente la `service_role` key (privilegio de más) en vez de una key de solo-insert — ver `utils/supabase.py`.
- [ ] **Fase 9 — Documentación**: README para que los estudiantes agreguen el server a su Claude (`claude mcp add --transport http ...`), incluyendo la instrucción sugerida para activar `reportar_interaccion` (una vez por turno, con el último `interaccion_id`).

## 9. Decisiones pendientes

- ~~Formato de los datos de pruebas/evaluaciones~~ — resuelto: `evaluaciones/*.pdf` en la raíz del repo, mismo pipeline que las clases (§4.4).
- ~~Modelo de auth definitivo~~ — resuelto: token compartido único para todo el curso (§5.4).
- ~~Fuente de datos del calendario general de clases~~ — descartado del alcance (§2), no bloquea nada.

Sin decisiones abiertas por ahora.

## 10. Modo de trabajo

Igual que en los demás proyectos del repo (`Clase 2.3`, `Clase 2.4`): implementación paso a paso, sin avanzar varias fases de golpe sin revisión — se construye y valida una fase antes de pasar a la siguiente.
