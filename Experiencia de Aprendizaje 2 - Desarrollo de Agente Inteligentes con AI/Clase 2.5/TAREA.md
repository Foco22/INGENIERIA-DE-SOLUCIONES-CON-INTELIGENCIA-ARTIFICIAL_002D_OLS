# Actividad: Agente RAG con evaluación

**Clase 2.5 — Desarrollo de Agentes Inteligentes con IA**

## 1. Objetivo

Construir un agente conversacional con **LangGraph** cuya única tool sea un **RAG** sobre una base de
documentos elegida por ustedes, y **evaluar si funciona bien o mal** con un dataset propio de 20
preguntas, midiendo **Tool Accuracy** y **Answer Accuracy**.

Como referencia tienen el ejemplo de la clase (`Clase 2.5/`), un agente sobre los estados
financieros de Abastible 2021–2025. **Usen otra base de documentos.**

## 2. Elección de la base de documentos

Elijan documentos con contenido **verificable**: cifras, fechas, nombres o reglas concretas sobre las
que se puedan escribir preguntas con una única respuesta correcta. Conviértanlos a **markdown**
(`markdown/*.md`), igual que en la clase.

Ideas: memorias anuales o estados financieros de otra empresa (Lipigas, Copec, Falabella, Cencosud),
un reglamento académico, el manual de un producto, normativa pública (Código del Trabajo, leyes),
informes del Banco Central o bases de un fondo concursable.

## 3. Construcción del agente

### 3.1 Ingesta y vector store (`agent_app/ingest.py`)

- Leer los markdown, dividirlos en chunks y guardar metadata útil (documento, página o sección).
- Generar embeddings y persistir el índice en `vectorstore/`.

### 3.2 Tool RAG (`agent_app/tools.py`)

- Una tool con `@tool` que reciba la consulta (y filtros opcionales, como año o documento) y devuelva
  los fragmentos recuperados con su cita.
- El **docstring** debe dejar claro qué contiene la base, porque el LLM lo lee para decidir si llamarla.

### 3.3 Grafo LangGraph (`agent_app/agent.py`)

Construyan el grafo **explícitamente** con `StateGraph`, sin `create_react_agent`, para que se vean el
state, los nodos y las aristas.

```
START ──► reset ──► agent ──(¿tool_calls?)──► tools ──► agent
                         └──────────────────► END
```

| Elemento | Qué hace |
|---|---|
| **State** | `TypedDict` con `messages` (reducer `add_messages`) y campos de trazabilidad: `tool_used`, `tool_calls`, `retrieved_docs`. |
| **Nodo `reset`** | Pone en cero la trazabilidad al inicio de cada turno. |
| **Nodo `agent`** | LLM con `bind_tools` y system prompt. Decide si llama la tool o responde directo. |
| **Nodo `tools`** | Ejecuta la tool y guarda en el state los argumentos y documentos recuperados. |
| **Aristas** | Arista condicional después de `agent`; `tools` vuelve a `agent`. |
| **Memoria** | `MemorySaver` con un `thread_id` por conversación. |

### 3.4 Prompts (`agent_app/prompts.py`)

- `AGENT_SYSTEM_PROMPT`: rol, **cuándo SÍ y cuándo NO** usar la tool, formato de respuesta con citas
  y reglas para no inventar datos.
- `JUDGE_SYSTEM_PROMPT`: el LLM-as-judge que decide si una respuesta es correcta.

### 3.5 Interfaz Streamlit (`app.py`)

- Pestaña **Chat**: conversación con memoria y un panel de **trazabilidad** bajo cada respuesta (si se
  llamó la tool, con qué argumentos y qué fragmentos trajo).
- Pestaña **Evaluación**: un botón que corre el dataset y muestra las dos métricas, por categoría y
  por pregunta.

## 4. Dataset de evaluación (`evaluation/dataset.json`)

Armen **20 preguntas**:

| Categoría | Cantidad | `expected_tools` | Qué son |
|---|---|---|---|
| `rag` | 10 | `["<nombre de su tool>"]` | Preguntas cuya respuesta está en los documentos. Repartidas entre los distintos documentos. |
| `no_tool` | 5 | `[]` | Saludos, small talk, preguntas ajenas al tema. |
| `falso_positivo` | 5 | `[]` | Preguntas que **parecen** requerir la tool pero no deben usarla: conceptos generales, otras entidades, cálculos con datos que entrega el usuario. |

Formato de cada pregunta:

```json
{
  "id": "q01",
  "category": "rag",
  "question": "¿...?",
  "expected_tools": ["buscar_documentos"],
  "expected_answer": "Respuesta correcta verificada en el documento"
}
```

Consejos:

- Verifiquen en el markdown cada respuesta de `rag`: si la respuesta esperada está mal, la métrica
  también lo estará.
- Incluyan algunas preguntas `rag` difíciles: comparar dos documentos, comparar años o un dato que
  aparece en una tabla.
- Para `no_tool` y `falso_positivo`, `expected_answer` describe qué debería responder el agente.

## 5. Métricas (`evaluation/evaluate.py`)

- **Tool Accuracy**: % de preguntas donde los **nombres** de las tools llamadas coinciden con
  `expected_tools`. Llamar la misma tool varias veces cuenta como una.
- **Answer Accuracy**: % de respuestas correctas según el LLM-as-judge, que compara la respuesta con
  `expected_answer` y devuelve `{"correct": bool, "reason": str}`.

Corran cada pregunta con un `thread_id` nuevo, para que ninguna dependa de la anterior.

## 6. ¿Funciona bien o mal?

Con los resultados en pantalla, revisen:

1. Las dos métricas, globales y por categoría.
2. Las preguntas que fallaron: ¿el error vino de la decisión de usar la tool, de la recuperación (trajo
   los fragmentos equivocados) o de la generación (tenía el dato y respondió mal)?
3. Una mejora (prompt, chunking, metadata, k, etc.): apliquen el cambio y comparen las métricas antes
   y después.

> El objetivo **no** es llegar al 100%, sino que el dataset ponga a prueba al agente y entender
> dónde falla y por qué.
