# Agente Inteligente con RAG y Google Calendar

Clase 2.3 - Ingeniería de Soluciones con Inteligencia Artificial

## Descripción

Agente conversacional construido con **LangGraph** que usa una arquitectura de
**supervisor con especialistas**: un nodo orquestador clasifica cada mensaje y lo deriva
al agente que corresponde.

- **RAG (Retrieval-Augmented Generation):** responde preguntas sobre el contenido de la
  clase usando una base de datos vectorial en MongoDB Atlas.
- **Agendamiento de reuniones:** agenda reuniones con el profesor a través de la API de
  Google Calendar, con confirmación del usuario antes de ejecutar la acción
  (human-in-the-loop).

## Arquitectura del agente

```
                    __start__
                        │
                   ┌────▼─────┐
                   │supervisor│  decide: rag | meeting | responder
                   └──┬───┬───┴──────────┐
        ┌─────────────┘   │              │  (responder: contesta
        ▼                 ▼              ▼   él mismo y termina)
  ┌───────────┐    ┌────────────┐    __end__
  │ rag_agent │    │meeting_agent│
  └─────┬─────┘    └─────┬──────┘
        │                │ (si la tool es schedule_meeting)
        ▼                ▼
┌──────────────┐  ┌──────────────┐
│generate_query│  │human_approval│ ◄── se detiene y pide confirmación
└──────┬───────┘  └──────┬───────┘
       ▼                 ▼
 ┌───────────┐    ┌─────────────┐
 │ rag_tools │    │meeting_tools│
 └─────┬─────┘    └──────┬──────┘
       └──► vuelve a su agente ◄──┘
```

Nodos:

- `supervisor` — clasifica el mensaje y escribe `destino` y `motivo` en el estado. Si es
  un saludo o algo trivial, responde él mismo y termina.
- `rag_agent` — especialista en el contenido del curso. Solo conoce `rag_search`.
- `generate_query` — reformula la conversación en una consulta optimizada antes de buscar.
- `rag_tools` — ejecuta la búsqueda vectorial.
- `meeting_agent` — especialista en reuniones. Conoce las tools de fecha y calendario.
- `human_approval` — suspende la ejecución y pide confirmación antes de agendar.
- `meeting_tools` — ejecuta las tools de calendario.

Cada especialista ve **solo sus propias herramientas**, de modo que no puede invocar las
del otro.

## Tecnologías

- Python
- LangGraph + LangChain
- OpenAI (GPT-4o-mini + embeddings)
- MongoDB Atlas (vector store)
- Google Calendar API
- Streamlit (interfaz de chat)
- LangSmith (trazas)

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

### Streamlit

```bash
streamlit run app.py
```

### LangGraph Studio

```bash
langgraph dev
```

Abre el link que imprime en consola. Si LangSmith bloquea el dominio, agrégalo en
*Advanced Settings* de la pantalla de error, o usa `langgraph dev --tunnel`.

## Configuración

### Variables de entorno

Crear un archivo `.env` con:

```
OPENAI_API_KEY=...
MONGODB_CONNECTION_STRING=...
LANGCHAIN_API_KEY=...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=...
```

### Credenciales de Google Calendar

1. En Google Cloud Console, habilitar la **Google Calendar API**.
2. Crear un **ID de cliente de OAuth** de tipo **Aplicación de escritorio** (el JSON debe
   empezar con `"installed"`; uno de tipo web no funciona con `run_local_server`).
3. Guardar el archivo descargado como `credentials.json` en la raíz del proyecto.
4. Agregar tu correo en *Usuarios de prueba* de la pantalla de consentimiento.

En la primera ejecución se abre el navegador para autorizar y se genera `token.pickle`.

### Base de conocimiento

La colección `agent-rag-duoc-uc.embeddings` debe existir en MongoDB Atlas con un índice
vectorial llamado `vector_index` sobre el campo `embedding` (1536 dimensiones,
`text-embedding-3-small`).

## Tarea

El agente hoy sabe responder con el material del curso y agendar reuniones. Cuando le
preguntan por algo del mundo real —quién es una persona, qué es un concepto general—
no tiene dónde buscar.

**Tu tarea es reemplazar el agente de reuniones (`meeting_agent`) por un agente de
Wikipedia (`wiki_agent`).** Al terminar, el supervisor debe derivar solo a dos
especialistas: `rag_agent` y `wiki_agent`.

Parte de la tarea es que tú identifiques qué partes del proyecto debes eliminar, cuáles
modificar y qué debes crear. Revisa bien cómo está construido el agente actual antes de
empezar.

### Requisitos

- El agente de reuniones y todo lo que depende de él deja de existir en el proyecto.
- El nuevo especialista obtiene su información de la API de Wikipedia en español
  (`https://es.wikipedia.org/w/api.php`) y devuelve un resumen del artículo junto con su
  URL.
- Cada especialista solo puede usar sus propias herramientas.
- La aplicación funciona tanto en Streamlit como en LangGraph Studio.
- El README refleja la nueva arquitectura.

### Criterio de éxito

- "¿Qué técnicas de prompt engineering vimos en clase?" → debe ir a `rag_agent`.
- "¿Quién es Yann LeCun?" → debe ir a `wiki_agent` y citar la URL del artículo.
- En el grafo ya no existe ningún nodo de reuniones.
- El agente nunca debe confundir ambas fuentes ni inventar contenido del curso.

### Pistas

- La API de Wikipedia responde **403** a las peticiones sin cabecera `User-Agent`.
- Si no hay resultados, la tool debe devolver un mensaje claro, no lanzar una excepción.

Sube tu solución a GitHub.
