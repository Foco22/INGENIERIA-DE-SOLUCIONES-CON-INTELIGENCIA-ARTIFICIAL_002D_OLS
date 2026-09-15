# Job Match Agent — Evaluador de ofertas con LangGraph

Agente que cruza **ofertas de empleo scrapeadas de Chile** (JobSpy) contra **mi perfil real**
(CV en markdown + datos duros en JSON) y entrega, por cada oferta, un **score de 1 a 10** en tres
bandas — pesimista / neutral / optimista — con un comentario honesto de por qué ese score, todo
persistido en base de datos.

El scoring lo decide **el LLM en una sola llamada**, no una fórmula. Simple a propósito: primero
que clasifique bien, después se ajusta.

**Alcance de v1:** ingesta → evalúa → guarda score y comentario → lo reviso en una tabla filtrable. El
human-in-the-loop (que yo corrija los scores y el agente aprenda de eso) está pensado en la
sección 8 pero **no se implementa todavía**: nada en v1 debe asumir que existe feedback.

Stack: Python 3.12 · LangGraph · LangChain · OpenAI · Pydantic · SQLite · JobSpy · Streamlit.

---

## 0. Convención de idioma (regla dura)

**Todo el código va en inglés. Toda la documentación va en español.**

| Va en inglés | Va en español |
|---|---|
| Nombres de funciones, clases, variables, módulos | Este CLAUDE.md y cualquier README |
| Campos de Pydantic y claves de `profile.json` | Docstrings y comentarios del código |
| Columnas y tablas de la DB | El **texto** de los prompts en `prompts.py` |
| Nombres de nodos, tools y campos del state | La salida del agente (comentarios, reporte CLI) |
| Flags del CLI (`ingest`, `evaluate`) | `data/cv.md` |

O sea: `def evaluate_job(...)` con docstring `"""Evalúa una oferta contra el perfil completo."""`.
Y `EVALUATOR_SYSTEM_PROMPT` es una constante en inglés cuyo contenido está escrito en español,
porque el comentario final lo leo yo.

---

## 1. Estructura del proyecto

```
app/
├── CLAUDE.md
├── .env.example              # OPENAI_API_KEY, OPENAI_MODEL, DB_PATH
├── requirements.txt
├── main.py                   # CLI: ingest | evaluate
├── streamlit_app.py          # UI: tabla filtrable sobre la DB
│
├── data/                     # TODO input del usuario vive acá
│   ├── cv.md                 # MI CV en markdown (texto libre, va entero al prompt)
│   ├── profile.json          # MIS datos duros (va entero al prompt, serializado)
│   ├── profile.example.json  # plantilla versionada del schema
│   ├── cv.template.md        # plantilla del CV (copiar a cv.md)
│   └── raw/                  # CSVs crudos de JobSpy
│       └── jobs_chile_data_scientist.csv   # 48 ofertas ya scrapeadas
│
├── db/
│   ├── schema.sql            # DDL: jobs, evaluations, runs
│   └── jobs.db               # SQLite (gitignored)
│
└── src/
    ├── agents/               # EL AGENTE: todo lo que toca al LLM
    │   ├── agent.py          # el loop sobre las ofertas y el manejo de errores
    │   ├── graph.py          # build_evaluator_graph(): el nodo, el ToolNode y los edges
    │   ├── prompts.py        # TODOS los prompts como constantes (nada inline)
    │   ├── states.py         # EvaluationState: los mensajes + job, run_id, evaluation
    │   └── tools.py          # SOLO la tool save_evaluation (+ sus guardrails)
    │
    └── utils/                # TODO LO DEMAS: no sabe nada de LangGraph
        ├── config.py         # settings desde .env (pydantic-settings) + SCORE_BANDS
        ├── models.py         # Pydantic: JobOffer, CandidateProfile, Evaluation
        ├── llm.py            # get_llm(): el modelo, configurado en un solo lugar
        ├── db/
        │   ├── database.py   # get_connection(), init_db() desde schema.sql
        │   └── repository.py # save_evaluation, get_pending_jobs, get_evaluations_df
        ├── ingestion/        # La API de datos
        │   ├── jobspy_client.py  # fetch_jobs() -> DataFrame
        │   ├── normalizer.py     # DataFrame/CSV -> list[JobOffer] (limpieza, dedupe)
        │   └── loader.py         # upsert_jobs(): persiste JobOffer en tabla jobs
        └── profile/
            └── loader.py     # load_profile(): cv.md + profile.json -> CandidateProfile
```

**Regla de capas:** `utils/` no importa LangChain/LangGraph (la excepcion es `llm.py`, que solo
construye el modelo). `agents/` no arma SQL ni lee archivos: usa `utils/db/repository.py` y
`utils/profile/loader.py`. `agent.py` no arma strings de prompt: viven en `prompts.py`.
Ningún módulo lee rutas hardcodeadas: todas salen de `utils/config.py`.

---

## 2. La carpeta `data/` — las dos fuentes del perfil

El CV solo no alcanza: las ofertas dicen "5+ años", "experiencia liderando equipos", "magíster
deseable", "sector retail". Esos datos hay que dárselos explícitos al modelo, no esperar que los
deduzca de un párrafo de narrativa. Por eso el perfil son dos archivos, ambos en `data/`, y
**los dos van completos al prompt**:

| Archivo | Formato | Para qué |
|---|---|---|
| `data/cv.md` | Markdown libre, en español | Narrativa, logros, contexto cualitativo |
| `data/profile.json` | JSON validado, claves en inglés | Los datos duros que el CV no deja comparar |
| `data/raw/*.csv` | CSV de JobSpy | Ofertas crudas antes de entrar a la DB |

### Schema de `data/profile.json`

Claves en inglés (son campos de Pydantic); los **valores** pueden ir en español.

```jsonc
{
  "name": "string",
  "current_title": "string",
  "experience": {
    "total_years": 3.5,
    "years_by_area": { "data_science": 2.0, "data_engineering": 1.5, "backend": 1.0 },
    "years_by_skill": { "python": 3.5, "sql": 3.0, "pytorch": 1.0, "gcp": 1.5, "spark": 0.5 }
  },
  "industries": ["retail", "banca", "educación"],
  "leadership": { "has_led": true, "max_team_size": 3, "years_leading": 1.0 },
  "education": {
    "max_level": "master",              // technical | bachelor | master | phd
    "degrees": ["Ingeniería Civil Industrial", "MSc Data Science (en curso)"],
    "certifications": ["GCP Professional ML Engineer"]
  },
  "languages": { "spanish": "nativo", "english": "B2" },
  "preferences": {
    "work_mode": ["hybrid", "remote"],  // remote | hybrid | onsite
    "location": "Santiago, Chile",
    "min_salary_clp_monthly": 2500000,
    "deal_breakers": ["100% presencial fuera de RM", "turnos rotativos"],
    "interests": ["GenAI", "MLOps", "NLP"]
  }
}
```

`profile.example.json` es la plantilla versionada; `profile.json` son los datos reales y va al
`.gitignore`. Si `profile.json` no existe, el pipeline **falla explícito** — no se inventan datos
del candidato ni se infieren números desde el CV.

---

## 3. El agente: un grafo de UN nodo y UNA tool

LangGraph explicito, pero minimo: **un solo nodo propio** (`evaluator`) mas el `ToolNode` que ya
viene hecho. Se compila una vez por corrida.

```
   system prompt = rubrica + CV + profile.json   (se carga siempre: no es una tool)
   user message  = la oferta
                     │
                     ▼
   START ──▶ ┌───────────────┐ ◀─────────────┐
             │   evaluator   │               │  la UNICA llamada al LLM: aqui se
             └───────┬───────┘               │  generan score y review, como
                     │                       │  argumentos del tool call
              tools_condition                │
                ┌────┴─────┐                 │
             si │          │ no              │
                ▼          ▼                 │
        ┌───────────────┐  END               │
        │   ToolNode    │  save_evaluation:  │
        └───────┬───────┘  valida y guarda   │
                │                            │
         route_after_tools ──── rechazado ───┘   (score invalido, modalidad mal usada)
                │
                ▼ guardado
               END
```

```python
graph = StateGraph(EvaluationState)
graph.add_node("evaluator", evaluator)      # nuestro
graph.add_node("tools", ToolNode(TOOLS))    # prearmado
graph.add_edge(START, "evaluator")
graph.add_conditional_edges("evaluator", tools_condition)
graph.add_conditional_edges("tools", route_after_tools, {"evaluator": "evaluator", END: END})
```

### Donde se genera el score (la pregunta clave)

En `agents/graph.py`, en `llm.invoke(...)` dentro del nodo `evaluator`. OpenAI lee la rubrica, el CV, el
perfil y la oferta, y devuelve un `AIMessage` con un `tool_call` cuyos `args` ya traen `score`,
`review`, `strengths`, `gaps` y `deal_breaker`. **La tool no evalua nada: recibe lo ya decidido.**

### La unica tool: `save_evaluation` (`src/agents/tools.py`)

```python
@tool
def save_evaluation(score, review, strengths, gaps, deal_breaker=None, *,
                    state: Annotated[dict, InjectedState],
                    tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
```

Hace tres cosas, y ninguna es evaluar:

1. **Es el esquema.** Su firma y docstring son lo que `bind_tools` le manda a OpenAI: el
   "formulario" que obliga al modelo a estructurar la respuesta en vez de escribir prosa.
2. **Es la aduana.** Valida el score, rechaza el mal uso de la modalidad (`_modality_misuse`),
   calcula la banda con `band_for()` — que el modelo no controla — y agrega `job_id`, `run_id`,
   `model`, `prompt_version`. Si rechaza, responde en texto y el grafo vuelve al evaluador para
   que corrija.
3. **Guarda** en la DB y deja el resultado en `state["evaluation"]`.

`job` y `run_id` no son argumentos del modelo: la tool los lee del state con `InjectedState`.
Por eso el state es `EvaluationState` (`agents/states.py`) y no `MessagesState` pelado.

**Por que una tool y no structured output.** Con una tool el modelo puede razonar antes de llenar
los argumentos, y si la tool rechaza, corrige y vuelve a llamar. Con structured output hay una
sola salida rigida y sin segunda oportunidad.

**Por que una tool y no dos.** Hubo una version con `evaluate_offer` + `save_evaluation`. La
segunda no recibia nada: solo persistia lo que la primera dejo en el state. No aportaba decision,
solo una llamada LLM extra por oferta. Se fusionaron.

**Por que el CV y el perfil no son tools.** Se necesitan en el 100% de las evaluaciones, asi que
van en el system prompt. Una tool se justifica cuando el modelo debe *decidir* si la usa.

**Si el modelo no llama la tool**, `tools_condition` va a END, la oferta queda `pending` y el caso
entra en `errors`; no se pierde en silencio.

**Costo: 1 llamada LLM por oferta** (mas una por cada rechazo, que es raro).

---

## 4. El codigo de la evaluacion

Un archivo por responsabilidad:

| Archivo | Que tiene |
|---|---|
| `src/agents/tools.py` | `save_evaluation` — **la unica tool**, mas su guardrail |
| `src/agents/states.py` | `EvaluationState` — job, run_id y el resultado |
| `src/agents/graph.py` | `build_evaluator_graph()` + el nodo `evaluator` + `route_after_tools` |
| `src/agents/agent.py` | `evaluate_offer()` (una oferta) y `evaluate_offers()` (el loop) |
| `src/utils/llm.py` | `get_llm()` — el modelo, configurado en un solo lugar |

```python
# src/agents/graph.py
def build_evaluator_graph(profile):
    """Compila el grafo una vez: sirve para toda la corrida."""

def route_after_tools(state) -> str:
    """Guardado -> END. Rechazado -> el evaluador corrige."""

# src/agents/agent.py
def evaluate_offer(graph, job, run_id) -> Evaluation | None:
    """Evalua UNA oferta. None si el agente no guardo."""

def evaluate_offers(jobs, profile, run_id=None) -> tuple[list[Evaluation], list[str]]:
    """Recorre las ofertas. Un fallo no bota la corrida."""
```

`evaluate_offers` abre el run, compila el grafo una vez, itera, captura errores por oferta y
cierra el run. No sabe como esta armado el grafo; `graph.py` no sabe que hay mas de una oferta.

---

## 5. El output del LLM: score, banda y comentario

El LLM devuelve **un score de 1 a 10** y **un comentario que explica por qué ese score**. Nada más.
No hay fórmula ni pesos en Python: la rúbrica es **texto dentro del prompt**, para poder ajustarla
escribiendo en vez de recalibrando números.

### Las tres bandas

| Score | `band` (código) | Etiqueta (CLI) | Qué significa |
|---|---|---|---|
| 1–6 | `pessimistic` | **pesimista** | No postular. El calce es malo o falta algo que no se cierra rápido |
| 7–8 | `neutral` | **neutral** | Postulable con reservas: hay calce pero también dudas reales |
| 9–10 | `optimistic` | **optimista** | Postular con prioridad. Postularía esta semana |

La banda la **deriva el código** desde el score (`utils/config.py: SCORE_BANDS`), no el modelo. Si el LLM
dice `score=9` con `band="pessimistic"`, gana el score. Así la banda nunca contradice el número.

### Qué mira el modelo para decidir el score

Guía en el prompt, no aritmética:

- **Años y seniority** vs. lo que pide la oferta
- **Skills obligatorias**: si falta la que da nombre al rol, no puede ser optimista
- **Tipo de problema** por sobre el nombre del cargo (un "Analista" haciendo ML pesa más que un
  "Data Scientist" haciendo reportería)
- **Industria y empresa**: producto propio vs. consultora vs. staffing
- **Condiciones**: modalidad, ubicación y salario mínimo del perfil
- **Deal breakers**: si aparece uno, score ≤ 4 y se llena el campo `deal_breaker`

### El comentario: honesto, concreto y verificable

`review` es el campo que más importa, porque es lo que me deja corregir el score con criterio.
Reglas que van **explícitas en el system prompt**:

1. **Explica el número, no la oferta.** "7 porque piden 5 años de producción y tengo 3.5" sirve;
   "es una buena oportunidad en una empresa sólida" no dice nada.
2. **Cita evidencia de ambos lados.** Cada afirmación se apoya en algo que dice la oferta y algo
   que dice mi CV o mi `profile.json`. Nada de impresiones generales.
3. **Prohibido inventar.** Si la oferta no dice el sueldo, el comentario dice "no informa sueldo",
   no lo estima. Si no dice modalidad, no la supone.
4. **Lo malo primero y sin suavizar.** Si no califico, lo dice derecho: "piden liderazgo de equipo
   y no tengo experiencia liderando". Nada de "sería un desafío interesante".
5. **Nada de coaching motivacional.** No es un consejero de carrera, es un filtro. No cierra con
   ánimo ni con "igual vale la pena intentarlo".
6. **Incertidumbre explícita.** Si la descripción es vaga o genérica, lo dice y eso mismo baja el
   score — una oferta que no se entiende no puede ser un 9.
7. **3 a 5 líneas.** Si necesita más, es que está adornando.

`strengths` y `gaps` salen separados del `review` para leerlos de un vistazo en el ranking sin
abrir el comentario completo.

**No todas pueden ser 9.** Un 9–10 significa "postularía esta semana"; el prompt lo dice explícito
para que el modelo no infle. `report` imprime la distribución por banda: si más de un tercio sale
optimista, el prompt está blando y hay que apretarlo.

---

## 6. Base de datos (`db/schema.sql`, SQLite)

Tablas y columnas en inglés; los valores de texto quedan como vienen (español).

```sql
CREATE TABLE jobs (
  id TEXT PRIMARY KEY,              -- hash estable de job_url
  site TEXT, title TEXT, company TEXT, location TEXT,
  date_posted TEXT, job_url TEXT UNIQUE, description TEXT,
  is_remote INTEGER, min_amount REAL, max_amount REAL, currency TEXT,
  raw_json TEXT,                    -- fila original de JobSpy
  status TEXT DEFAULT 'pending',    -- pending | evaluated | error
  ingested_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evaluations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT NOT NULL REFERENCES jobs(id),
  run_id TEXT NOT NULL,
  score INTEGER NOT NULL CHECK (score BETWEEN 1 AND 10),
  band TEXT NOT NULL,               -- pessimistic | neutral | optimistic
  review TEXT NOT NULL,             -- el comentario, en español
  strengths_json TEXT, gaps_json TEXT, deal_breaker TEXT,
  model TEXT, prompt_version TEXT, tokens INTEGER,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (job_id, run_id)
);

CREATE TABLE runs (
  run_id TEXT PRIMARY KEY, started_at TEXT, finished_at TEXT,
  n_jobs INTEGER, profile_hash TEXT, prompt_version TEXT
);
```

Una oferta puede tener varias evaluaciones (una por `run_id`): así se compara cómo cambia el match
cuando cambia el perfil o el prompt. `ingestion/loader.py` hace **upsert por `job_url`**;
re-ingestar no duplica ni pierde el histórico.

---

## 7. La UI (`streamlit_app.py`)

Reemplaza al reporte por consola. Es **solo lectura sobre la DB**: no llama al LLM, no scrapea, no
evalúa. Si la app se cae, el pipeline no se entera.

```bash
streamlit run streamlit_app.py
```

### Layout

**Sidebar — filtros** (todo se aplica sobre el DataFrame, no sobre SQL, para que sea instantáneo):

- `score` — slider de rango 1–10
- `band` — multiselect: pesimista / neutral / optimista
- `site` — indeed / linkedin
- `company` — texto libre, match parcial
- `title` — texto libre (ej. "scientist" para sacar los data engineer)
- `is_remote` / modalidad
- `date_posted` — rango de fechas
- `deal_breaker` — checkbox "ocultar las descartadas"
- `run_id` — selector de corrida, default la última

**Main — tabla** (`st.dataframe`, ordenable por cualquier columna):

| score | band | title | company | location | date_posted | gaps | link |
|---|---|---|---|---|---|---|---|

- `score` con `st.column_config.ProgressColumn` (0–10) para leerlo de un vistazo
- `band` con color: rojo / amarillo / verde
- `link` con `st.column_config.LinkColumn` → abre la oferta en el portal
- `gaps` truncado a los 2 primeros; el detalle va abajo

**Detalle** — al seleccionar una fila (`on_select="rerun"`), abajo se muestra el `review` completo,
`strengths`, `gaps`, el `deal_breaker` si lo hay, y la descripción original de la oferta en un
`st.expander`.

**Arriba — métricas** (`st.metric`): total evaluadas, cuántas optimistas, score promedio,
distribución por banda en un `st.bar_chart`. Es lo que antes iba a imprimir el CLI, y sirve para
detectar de una si el prompt quedó inflado.

### Cómo lee los datos

```python
@st.cache_data(ttl=60)
def load_evaluations(run_id: str | None = None) -> pd.DataFrame:
    """Trae jobs + evaluations en un DataFrame plano para la tabla."""
```

Vive en `src/utils/db/repository.py` como `get_evaluations_df()`; `streamlit_app.py` solo la envuelve con
el cache. Un `st.button("Recargar")` llama a `st.cache_data.clear()` para ver una corrida recién
terminada sin reiniciar la app.

Conexión SQLite en modo lectura y `check_same_thread=False` — Streamlit corre en otro hilo y si
`evaluate` está escribiendo al mismo tiempo, la app no debe bloquearlo.

### Por qué acá y no en el grafo

El grafo escribe, la UI lee, y la DB es el único punto de contacto. Así puedo re-evaluar mientras
tengo la app abierta, y la UI sirve igual para corridas viejas (`run_id`) sin volver a gastar
tokens.

---

## 8. Fase 2 — human in the loop (todavía NO)

Anotado para no perderlo, pero **no se implementa hasta que v1 clasifique bien**. Si los scores de
v1 no son razonables, el feedback no arregla nada: sería una capa encima de un evaluador que no
sirve.

La idea, cuando llegue: yo corrijo los scores que no me hacen sentido y explico por qué; esas
correcciones entran como ejemplos de calibración en las corridas siguientes, y el agente aprende
mis gustos en vez de solo la rúbrica.

Lo que habría que agregar entonces:

- Tabla `feedback` (`evaluation_id`, `job_id`, `model_score`, `user_score`, `note`) — la `note`,
  el *por qué* de la corrección, es lo más valioso
- La corrección se hace **en la misma tabla de Streamlit** (columna editable de score +
  campo de nota), no por CLI — es el lugar natural: estoy leyendo el ranking, corrijo ahí mismo
- Nodo `load_calibration` antes del loop, que inyecta al prompt las N correcciones más útiles
- Métrica de si funciona: MAE entre el score del modelo y mis correcciones, por corrida

**Lo único que v1 hace para dejarlo preparado:** guardar `model` y `prompt_version` en cada
evaluación, y que `evaluations.id` sea estable. Con eso el feedback se cuelga después sin migrar
nada. No se crea la tabla ni el nodo todavía.

---

## 9. Comandos

```bash
pip install -r requirements.txt
cp .env.example .env                    # poner OPENAI_API_KEY

python main.py ingest --query "data scientist" --location "Santiago, Chile" --results 30
python main.py ingest --from-csv data/raw/jobs_chile_data_scientist.csv
python main.py evaluate --limit 10      # corre el grafo sobre los jobs pending

streamlit run streamlit_app.py          # la tabla filtrable: acá reviso todo
```

---

## 10. Convenciones y gotchas

- **Idioma:** ver sección 0. Si encuentras un identificador en español en el código, renómbralo.
- **Un nodo propio.** Si aparece la tentación de agregar nodos, primero preguntarse si no es
  un `for` disfrazado. El loop de ofertas se lee mejor en Python que como grafo.
- **OpenAI:** `ChatOpenAI(model=settings.openai_model, temperature=0)`. Modelo configurable por
  `.env` (`OPENAI_MODEL`), nunca hardcodeado en `nodes.py`. Salidas tipadas siempre con
  `with_structured_output(Model)`, no parseo de JSON a mano.
- **`temperature=0` no es opcional:** si el mismo par (oferta, perfil) da scores distintos entre
  corridas, el ranking no es comparable.
- **Prompts versionados:** cada cambio a `EVALUATOR_SYSTEM_PROMPT` sube `PROMPT_VERSION` en
  `utils/config.py`, y ese valor se guarda en `evaluations.prompt_version`. Es lo que permite comparar
  dos corridas y saber si el cambio de prompt mejoró o empeoró.
- **Prompts:** todos en `src/agents/prompts.py` como constantes en MAYÚSCULAS y en inglés
  (`EVALUATOR_SYSTEM_PROMPT`, `EVALUATION_USER_PROMPT`), con `{placeholders}`
  de `str.format`. El contenido va en español.
- **JobSpy en Chile:** `country_indeed="chile"`. **Glassdoor no soporta Chile** (lanza
  `Exception: Glassdoor is not available for CHILE`) y Google suele devolver 0 resultados
  → sitios efectivos: `["indeed", "linkedin"]`. Ver `test.py`.
- **Encoding:** todo I/O con `encoding="utf-8"` explícito. La consola de Windows es cp1252 y rompe
  los acentos al imprimir; los archivos quedan bien. Para imprimir, `errors="replace"`.
- **Costo:** una oferta = **1 llamada LLM**. 217 ofertas ≈ 217 llamadas.
- **Idempotencia:** `evaluate` salta las ofertas ya evaluadas en el mismo `run_id`.
- **Errores por oferta:** un fallo marca `status='error'` en esa fila y el grafo sigue con la
  siguiente; nunca se cae el pipeline completo.
- **Nunca** commitear `.env`, `db/jobs.db`, `data/cv.md` ni `data/profile.json` (datos personales).

---

## 11. Orden de implementación

1. `models.py` (los contratos primero)
2. `db/` + `schema.sql` + `ingestion/` (cargar las 48 ofertas del CSV existente)
3. `profile/loader.py` + `data/profile.json` real
4. `prompts.py` + `tools.save_evaluation` — probar con UNA oferta primero
5. `agent.py` (el agente y el loop)
6. `main.py`: `ingest`, `evaluate`
7. `streamlit_app.py` — la tabla

Ahí termina v1. La fase 2 (sección 8) se evalúa recién después de leer un ranking completo.
