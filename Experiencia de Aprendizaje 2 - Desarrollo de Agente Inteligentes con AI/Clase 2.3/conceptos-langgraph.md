# Componentes de LangGraph

Clase 2.3 - Ingeniería de Soluciones con Inteligencia Artificial

Referencia de los bloques con los que se construye un agente en LangGraph. Los ejemplos
salen del agente de esta clase (`agent_app/agent.py`).

---

## La idea central

Un agente en LangGraph es un **grafo dirigido con estado compartido**. En vez de escribir
un `while` con ifs anidados, defines:

- **qué pasos existen** (nodos),
- **cómo se decide el siguiente paso** (aristas),
- **qué información viaja entre ellos** (estado).

LangGraph se encarga de ejecutarlos en orden, guardar el progreso y poder retomarlo.

```
Estado inicial → Nodo → decisión → Nodo → ... → END
       ▲                                          │
       └──────── el estado se acumula ────────────┘
```

---

## 1. State — la memoria de trabajo

El estado es un diccionario tipado que viaja por todo el grafo. Cada nodo recibe el estado
completo y devuelve **solo los campos que quiere cambiar**.

```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    destino: str
    motivo: str
```

### Reducers: la parte que confunde

El `Annotated[list, add_messages]` es lo importante. Un **reducer** define *cómo se combina*
lo que devuelve un nodo con lo que ya había:

| Campo | Comportamiento |
|-------|----------------|
| `destino: str` | Sin reducer: el valor nuevo **reemplaza** al anterior. |
| `messages: Annotated[list, add_messages]` | Con reducer: los mensajes nuevos se **agregan** a la lista. |

Por eso un nodo puede devolver `{"messages": [response]}` con un solo mensaje y no borra la
conversación: `add_messages` lo añade al final.

`add_messages` tiene además un truco: si el mensaje nuevo trae el **mismo `id`** que uno
existente, lo **reemplaza** en vez de agregarlo. Así funciona `generate_query`, que
reescribe la búsqueda del agente sin duplicar el mensaje:

```python
updated_message = AIMessage(
    id=last_message.id,          # mismo id -> reemplaza
    content=last_message.content,
    tool_calls=updated_tool_calls,
)
return {"messages": [updated_message]}
```

---

## 2. Node — un paso del proceso

Un nodo es una **función Python normal**: recibe el estado, hace algo, devuelve una
actualización parcial.

```python
def rag_agent(state: AgentState) -> AgentState:
    response = rag_llm.invoke(
        [SystemMessage(content=RAG_AGENT_PROMPT)] + state["messages"]
    )
    return {"messages": [response]}
```

No tiene nada de mágico: puede llamar a un LLM, consultar una base de datos, hacer un
cálculo, o no devolver nada (`return {}`) si no cambia el estado.

Se registra con un nombre, que es como lo verás en Studio:

```python
graph.add_node("rag_agent", rag_agent)
```

---

## 3. Edge — cómo se decide el siguiente paso

### Arista fija

Siempre va al mismo lugar. "Después de buscar, vuelve al agente":

```python
graph.add_edge("rag_tools", "rag_agent")
```

### Arista condicional

Una función mira el estado y **devuelve el nombre** del siguiente nodo:

```python
def route_supervisor(state: AgentState) -> str:
    return {"rag": "rag_agent", "meeting": "meeting_agent"}.get(state["destino"], END)

graph.add_conditional_edges("supervisor", route_supervisor, {
    "rag_agent": "rag_agent",
    "meeting_agent": "meeting_agent",
    END: END,
})
```

El tercer argumento es el **mapa de destinos posibles**. No es obligatorio, pero sin él
Studio no puede dibujar las flechas: las descubre recién al ejecutar.

La función de routing **no modifica el estado**, solo lo lee y decide.

### Punto de entrada y END

```python
graph.set_entry_point("supervisor")   # por dónde empieza
```

`END` es un marcador especial que significa "termina la ejecución". No es un nodo que
escribas tú.

---

## 4. Tools — darle capacidades al LLM

Una tool es una función decorada con `@tool`. El LLM no ejecuta nada: solo **pide** que se
ejecute, y LangGraph la corre.

```python
@tool
def get_available_slots(professor_email: str, date: str) -> str:
    """Get available time slots from the professor's calendar on a given date.

    Args:
        professor_email: Professor's email address.
        date: Date to check in format YYYY-MM-DD.
    """
    ...
```

**El docstring no es documentación, es el prompt de la tool.** LangChain construye un
esquema JSON a partir de la firma y el docstring, y eso es literalmente lo único que el
modelo ve para decidir si usarla. Un docstring vago produce una tool que nunca se invoca o
que se invoca a destiempo.

### El ciclo agente ↔ tools

```python
rag_llm = ChatOpenAI(model="gpt-4o-mini").bind_tools([rag_search])
graph.add_node("rag_tools", ToolNode([rag_search]))
```

1. `bind_tools` le pasa al modelo los esquemas de las tools disponibles.
2. El modelo responde con un `AIMessage` que trae `tool_calls` (nombre + argumentos).
3. `ToolNode` lee esos `tool_calls`, ejecuta las funciones y devuelve un `ToolMessage` por
   cada una, con el mismo `tool_call_id`.
4. Se vuelve al agente, que ahora ve el resultado y redacta la respuesta final.

El ciclo termina cuando el modelo responde **sin** `tool_calls`:

```python
def route_rag(state: AgentState) -> str:
    if getattr(state["messages"][-1], "tool_calls", None):
        return "generate_query"
    return END
```

> **Regla que rompe ejecuciones:** cada `ToolMessage` debe responder a un `tool_call`
> existente en el mensaje inmediatamente anterior. Si dejas un `ToolMessage` huérfano, la
> API del modelo devuelve `400 - messages with role 'tool' must be a response to a
> preceeding message with 'tool_calls'`.

### Darle tools distintas a cada agente

Un agente solo puede llamar a lo que le enlazaste. Por eso en este proyecto cada
especialista ve únicamente lo suyo, y el `rag_agent` no puede agendar nada por error:

```python
rag_tools = [rag_search]
meeting_tools = [get_next_date_for_weekday, get_available_slots, schedule_meeting]
```

---

## 5. `graph.compile()` — de plano a ejecutable

Hasta aquí `graph` es un `StateGraph`: un **plano**. No se puede ejecutar. `compile()` lo
valida (que no haya nodos inalcanzables ni destinos inexistentes) y devuelve un objeto
ejecutable:

```python
app = graph.compile(checkpointer=checkpointer)
```

El resultado es un *Runnable* de LangChain, con la interfaz habitual:

| Método | Para qué |
|--------|----------|
| `app.invoke(input, config)` | Ejecuta hasta el final y devuelve el estado. |
| `app.stream(input, config)` | Va emitiendo cada paso a medida que ocurre. |
| `app.get_state(config)` | Lee el estado guardado de una conversación. |
| `app.get_graph()` | Devuelve la estructura, para dibujarla. |

---

## 6. Checkpointer — memoria y capacidad de retomar

Sin checkpointer, cada `invoke` empieza de cero: el agente no recuerda nada del turno
anterior.

```python
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
```

El checkpointer **guarda una foto del estado después de cada paso**, agrupada por
`thread_id`. El `thread_id` es el identificador de la conversación:

```python
config = {"configurable": {"thread_id": "abc-123"}}
app.invoke({"messages": [HumanMessage(content="hola")]}, config=config)
```

Dos `thread_id` distintos son dos conversaciones independientes. El mismo `thread_id`
continúa donde quedó.

| Checkpointer | Uso |
|--------------|-----|
| `MemorySaver` | En memoria del proceso. Se pierde al reiniciar. Sirve para desarrollo. |
| `SqliteSaver`, `PostgresSaver` | Persistentes. Sobreviven a reinicios. |

Lo que habilita, además de la memoria conversacional:

- **Retomar** una ejecución pausada (ver `interrupt` abajo).
- **Inspeccionar** el estado en cualquier momento con `get_state`.
- **Time travel**: volver a un checkpoint anterior y reejecutar desde ahí.

---

## 7. `interrupt()` — human in the loop

Un nodo puede **suspender** la ejecución y esperar a una persona. Esto solo funciona si
hay checkpointer: es el checkpoint lo que permite congelar el estado y retomarlo después.

```python
def human_approval(state: AgentState) -> AgentState:
    tool_call = state["messages"][-1].tool_calls[0]

    user_response = interrupt({
        "question": "¿Confirmas agendar esta reunión?",
        "meeting": tool_call["args"],
    })
    ...
```

Al llegar ahí la ejecución se detiene. El valor que le pasas a `interrupt()` es lo que
recibe la interfaz para mostrárselo al usuario. Para continuar:

```python
app.invoke(Command(resume="sí, confirmo"), config=config)
```

Ese texto es lo que devuelve `interrupt()` dentro del nodo, que sigue **desde esa línea**.

Cómo detecta la interfaz que quedó pausado:

```python
state = app.get_state(config)
if state.next and "human_approval" in state.next:
    datos = state.tasks[0].interrupts[0].value
```

Un detalle que ahorra confusión: al reanudar, la ejecución **no vuelve a pasar por el nodo
inicial**. Retoma exactamente en el nodo interrumpido.

---

## 8. Cómo encaja todo

```python
graph = StateGraph(AgentState)                   # 1. el plano, con su estado

graph.add_node("supervisor", supervisor)         # 2. los pasos
graph.add_node("rag_agent", rag_agent)
graph.add_node("rag_tools", ToolNode(rag_tools))

graph.set_entry_point("supervisor")              # 3. por dónde empieza

graph.add_conditional_edges(                     # 4. las decisiones
    "supervisor", route_supervisor,
    {"rag_agent": "rag_agent", END: END},
)
graph.add_edge("rag_tools", "rag_agent")         # 5. los caminos fijos

app = graph.compile(checkpointer=MemorySaver())  # 6. a ejecutable, con memoria
```

---

## 9. Errores frecuentes

| Síntoma | Causa |
|---------|-------|
| `400 - messages with role 'tool' must be a response to a preceeding message with 'tool_calls'` | Un `ToolMessage` quedó sin su `tool_call` correspondiente, normalmente al modificar mensajes a mano. |
| El agente no recuerda el turno anterior | Falta el checkpointer, o cada llamada usa un `thread_id` distinto. |
| `interrupt()` no pausa nada | El grafo se compiló sin checkpointer. |
| LangGraph Studio rechaza el grafo | Se le pasó el grafo ya compilado con checkpointer propio. En `langgraph.json` hay que apuntar al `StateGraph` sin compilar: la plataforma pone su propia persistencia. |
| La tool nunca se invoca | El docstring no describe bien *cuándo* usarla, o no se enlazó con `bind_tools` al modelo de ese nodo. |
| Un nodo borra parte del estado | Se devolvió un campo sin reducer, que reemplaza en vez de acumular. |
