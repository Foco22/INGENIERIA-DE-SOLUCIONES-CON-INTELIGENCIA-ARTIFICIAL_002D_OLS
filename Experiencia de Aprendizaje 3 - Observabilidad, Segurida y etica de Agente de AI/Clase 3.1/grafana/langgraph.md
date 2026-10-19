# LangGraph — Guía de Clase

Clase 2.3 - Ingeniería de Soluciones con Inteligencia Artificial

---

## 1. ¿Cómo se estructura un proceso en LangGraph?

LangGraph permite construir agentes como **grafos dirigidos**, donde cada nodo representa una operación y las aristas (edges) definen el flujo entre ellas.

Un proceso en LangGraph siempre sigue esta estructura base:

```
Estado → Nodo → Decisión → Nodo → ... → FIN
```

Los tres conceptos clave son:

| Concepto | Descripción |
|----------|-------------|
| **State** | El estado compartido que se pasa entre nodos. Es un diccionario tipado. |
| **Node** | Una función Python que recibe el estado y retorna una actualización del estado. |
| **Edge** | La conexión entre nodos. Puede ser fija o condicional. |

---

## 2. Nodos y Edges — ¿Qué representan?

### Nodo (Node)
Un nodo es simplemente una **función** que:
- Recibe el estado actual del grafo
- Realiza una operación (llamar al LLM, ejecutar una tool, pedir confirmación, etc.)
- Retorna una actualización parcial del estado

```python
def call_model(state: AgentState) -> AgentState:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}
```

### Edge fija
Conecta dos nodos de forma directa y siempre sigue el mismo camino.

```python
graph.add_edge("generate_query", "tools")
graph.add_edge("tools", "agent")
```

### Edge condicional
Evalúa el estado actual y decide a qué nodo ir según una función de routing.

```python
graph.add_conditional_edges("agent", should_continue, {
    "generate_query": "generate_query",
    "tools": "tools",
    "human_approval": "human_approval",
    END: END,
})
```

---

## 3. Estructura del proyecto

```
agent_app/
├── agent.py       # Construcción del grafo LangGraph
├── prompts.py     # Prompts del sistema para el LLM
├── tools.py       # Herramientas disponibles para el agente
└── utils/
    ├── embeddings.py   # Cliente de embeddings (OpenAI)
    └── calendar.py     # Cliente de Google Calendar
```

---

## 4. `agent.py` — El grafo

Es el archivo central del proyecto. Aquí se define:

- El **estado** del agente (`AgentState`)
- Los **nodos** del grafo (funciones que ejecutan cada paso)
- La **lógica de routing** (`should_continue`, `after_approval`)
- La **compilación** del grafo con checkpointer para memoria

Responsabilidades de cada nodo:

| Nodo | Función | Descripción |
|------|---------|-------------|
| `agent` | `call_model` | Llama al LLM y decide qué tool usar |
| `generate_query` | `generate_query` | Reformula la pregunta del usuario para RAG |
| `human_approval` | `human_approval` | Pausa y pide confirmación antes de agendar |
| `tools` | `ToolNode` | Ejecuta la tool que el LLM seleccionó |

---

## 5. `prompts.py` — Los prompts

Contiene las instrucciones que guían el comportamiento del LLM. Hay tres prompts:

| Prompt | Propósito |
|--------|-----------|
| `AGENT_SYSTEM_PROMPT` | Instrucciones principales del agente: qué herramientas usar y cuándo |
| `QUERY_REFORMULATION_PROMPT` | Le pide al LLM que reformule la pregunta del usuario en una query de búsqueda óptima |
| `APPROVAL_INTERPRETATION_PROMPT` | Interpreta la respuesta del usuario (sí/no) para confirmar o cancelar una reunión |

Los prompts son críticos porque determinan la **calidad del razonamiento** del agente.

---

## 6. `tools.py` — Las herramientas

Las tools son funciones decoradas con `@tool` que el agente puede invocar. Cada tool tiene:
- Un nombre (el nombre de la función)
- Un docstring que el LLM lee para saber cuándo usarla
- Los parámetros tipados que el LLM debe completar

| Tool | Descripción |
|------|-------------|
| `rag_search` | Busca en MongoDB usando vector search para responder preguntas del curso |
| `get_next_date_for_weekday` | Calcula la fecha exacta de un día de la semana mencionado por el usuario |
| `get_available_slots` | Consulta los horarios disponibles del profesor en Google Calendar |
| `schedule_meeting` | Crea un evento en Google Calendar (requiere confirmación humana) |

---

## 7. `utils/` — Clientes externos

Contiene los clientes que conectan con servicios externos:

- **`embeddings.py`** — Genera embeddings con OpenAI para la búsqueda vectorial en MongoDB
- **`calendar.py`** — Se autentica con Google Calendar API para leer disponibilidad y crear eventos

---

## 8. Arquitectura del agente — Ejemplo real

```python
tool_node = ToolNode(tools)

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("generate_query", generate_query)
graph.add_node("human_approval", human_approval)
graph.add_node("tools", tool_node)

graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {
    "generate_query": "generate_query",   # rag_search
    "tools": "tools",                     # cualquier otra tool
    "human_approval": "human_approval",   # schedule_meeting
    END: END,
})
graph.add_edge("generate_query", "tools")
graph.add_conditional_edges("human_approval", after_approval, {
    "tools": "tools",
    "agent": "agent",
})
graph.add_edge("tools", "agent")

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
```

### Flujo del agente paso a paso

```
Usuario escribe → [agent]
                     |
          ¿Qué tool se llamó?
         /           |          \          \
  rag_search   schedule_meeting  otra tool  ninguna
       |               |              |         |
[generate_query]  [human_approval]  [tools]   END
       |            sí |   no |       |
     [tools]       [tools] [agent]  [agent]
       |               |
     [agent]         [agent]
```

### ¿Por qué `rag_search` pasa por `generate_query`?

Porque la pregunta del usuario puede estar mal formulada para una búsqueda vectorial. El nodo `generate_query` reformula la pregunta en una query más precisa antes de ejecutar la búsqueda en MongoDB.

### ¿Por qué `schedule_meeting` pasa por `human_approval`?

Porque crear un evento en el calendario es una acción irreversible. El nodo `human_approval` usa `interrupt()` de LangGraph para **pausar la ejecución** y esperar confirmación explícita del usuario antes de proceder.

### ¿Por qué las demás tools van directo a `tools`?

Las tools como `get_available_slots` y `get_next_date_for_weekday` son operaciones de solo lectura, no necesitan pre-procesamiento ni confirmación. Cualquier tool nueva que se agregue al agente seguirá este mismo camino por defecto.