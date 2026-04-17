# Agente Inteligente con RAG y Google Calendar

Clase 2.3 - Ingeniería de Soluciones con Inteligencia Artificial

## Descripción

Agente conversacional construido con **LangGraph** que combina dos capacidades principales:

- **RAG (Retrieval-Augmented Generation):** responde preguntas sobre el contenido de la clase usando una base de datos vectorial en MongoDB.
- **Agendamiento de reuniones:** permite agendar reuniones con el profesor a través de la API de Google Calendar, con confirmación del usuario antes de ejecutar la acción (human-in-the-loop).

## Arquitectura del agente

El grafo tiene los siguientes nodos:

- `agent` — modelo LLM que decide qué herramienta usar
- `generate_query` — reformula la pregunta del usuario para optimizar la búsqueda RAG
- `tools` — ejecuta las herramientas (búsqueda, calendario)
- `human_approval` — pausa y pide confirmación antes de agendar una reunión

## Tecnologías

- Python
- LangGraph + LangChain
- OpenAI (GPT-4o-mini + embeddings)
- MongoDB Atlas (vector store)
- Google Calendar API
- Streamlit (interfaz de chat)
- Docker (LangGraph Studio)

## Ejecución

### Streamlit
```bash
streamlit run app.py
```

### LangGraph Studio
```bash
cp -rL ~/clase23 /tmp/clase23 && cd /tmp/clase23 && langgraph up
```
Luego abrir: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123

## Variables de entorno

Crear un archivo `.env` con:
```
OPENAI_API_KEY=...
MONGODB_CONNECTION_STRING=...
LANGCHAIN_API_KEY=...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=...
```

## Tarea

1. Clona o copia este repositorio en tu entorno local.
2. Crea una **nueva tool** en `agent_app/tools.py` usando el decorador `@tool` de LangChain. Puede ser cualquier herramienta útil, por ejemplo:
   - Consultar el clima
   - Buscar información en Wikipedia
   - Calcular fechas
   - Cualquier idea propia
3. Registra la tool en `agent_app/agent.py` agregándola a la lista `tools`.
4. Asegúrate de que el agente pueda invocarla correctamente desde el chat en Streamlit.
5. Sube tu solución a GitHub.

> **Criterio de éxito:** el agente debe detectar cuándo usar tu nueva tool y ejecutarla correctamente en una conversación real.