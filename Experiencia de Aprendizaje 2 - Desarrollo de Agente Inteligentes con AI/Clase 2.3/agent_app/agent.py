from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from pydantic import BaseModel, Field
from typing import TypedDict, Annotated, Literal
from datetime import date
from dotenv import load_dotenv

from agent_app.tools import rag_search, schedule_meeting, get_available_slots, get_next_date_for_weekday
from agent_app.prompts import (
    SUPERVISOR_PROMPT,
    SUPERVISOR_DIRECT_PROMPT,
    RAG_AGENT_PROMPT,
    MEETING_AGENT_PROMPT,
    QUERY_REFORMULATION_PROMPT,
    APPROVAL_INTERPRETATION_PROMPT,
)

load_dotenv()

# Cada especialista ve solo sus propias herramientas.
rag_tools = [rag_search]
meeting_tools = [get_next_date_for_weekday, get_available_slots, schedule_meeting]

rag_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(rag_tools)
meeting_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(meeting_tools)
plain_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


class Route(BaseModel):
    """Decisión del supervisor sobre quién atiende al estudiante."""

    destino: Literal["rag", "meeting", "responder"] = Field(
        description="Especialista que debe atender el último mensaje."
    )
    motivo: str = Field(description="Una frase breve explicando la decisión.")


router_llm = plain_llm.with_structured_output(Route)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    destino: str
    motivo: str


# --------------------------------------------------------------------------- #
# Supervisor
# --------------------------------------------------------------------------- #

def supervisor(state: AgentState) -> AgentState:
    """Clasifica la conversación y decide qué especialista responde."""
    decision = router_llm.invoke(
        [SystemMessage(content=SUPERVISOR_PROMPT)] + state["messages"]
    )

    if decision.destino == "responder":
        answer = plain_llm.invoke(
            [SystemMessage(content=SUPERVISOR_DIRECT_PROMPT)] + state["messages"]
        )
        return {"destino": decision.destino, "motivo": decision.motivo, "messages": [answer]}

    return {"destino": decision.destino, "motivo": decision.motivo}


def route_supervisor(state: AgentState) -> str:
    return {"rag": "rag_agent", "meeting": "meeting_agent"}.get(state["destino"], END)


# --------------------------------------------------------------------------- #
# Especialista RAG
# --------------------------------------------------------------------------- #

def rag_agent(state: AgentState) -> AgentState:
    response = rag_llm.invoke(
        [SystemMessage(content=RAG_AGENT_PROMPT)] + state["messages"]
    )
    return {"messages": [response]}


def generate_query(state: AgentState) -> AgentState:
    """Reformula el historial en una consulta de búsqueda optimizada."""
    conversation = "\n".join(
        f"{m.type}: {m.content}" for m in state["messages"] if m.content
    )
    result = plain_llm.invoke([
        SystemMessage(content=QUERY_REFORMULATION_PROMPT),
        SystemMessage(content=f"Conversation:\n{conversation}"),
    ])
    search_query = result.content.strip()

    last_message = state["messages"][-1]
    updated_tool_calls = [
        {**tc, "args": {"query": search_query}}
        for tc in last_message.tool_calls
    ]
    updated_message = AIMessage(
        id=last_message.id,
        content=last_message.content,
        tool_calls=updated_tool_calls,
    )
    return {"messages": [updated_message]}


def route_rag(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "generate_query"
    return END


# --------------------------------------------------------------------------- #
# Especialista de reuniones (meeting)
# --------------------------------------------------------------------------- #

def meeting_agent(state: AgentState) -> AgentState:
    today = date.today().strftime("%Y-%m-%d")
    system = SystemMessage(content=MEETING_AGENT_PROMPT + f"\n\nFecha de hoy: {today}")
    response = meeting_llm.invoke([system] + state["messages"])
    return {"messages": [response]}


class Aprobacion(BaseModel):
    """Interpretación de la respuesta del estudiante en la confirmación."""

    confirma: bool = Field(
        description="True solo si el estudiante acepta agendar la reunión."
    )


approval_llm = plain_llm.with_structured_output(Aprobacion)


def _interpret_approval(user_response: str) -> bool:
    result = approval_llm.invoke([
        SystemMessage(content=APPROVAL_INTERPRETATION_PROMPT),
        SystemMessage(content=f"Respuesta del estudiante: {user_response}"),
    ])
    return result.confirma


def human_approval(state: AgentState) -> AgentState:
    """Pausa la ejecución y pide al usuario que confirme la reunión."""
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]

    user_response = interrupt({
        "question": "¿Confirmas agendar esta reunión?",
        "meeting": tool_call["args"],
    })

    if not _interpret_approval(user_response):
        # El tool_call se conserva: un ToolMessage sin su tool_call previo
        # es una secuencia inválida para la API del modelo.
        cancel_msg = ToolMessage(
            content="Reunión cancelada por el usuario. No se agendó nada.",
            tool_call_id=tool_call["id"],
        )
        return {"messages": [cancel_msg]}

    return {}


def route_meeting(state: AgentState) -> str:
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", None)
    if not tool_calls:
        return END
    if tool_calls[0]["name"] == "schedule_meeting":
        return "human_approval"
    return "meeting_tools"


def after_approval(state: AgentState) -> str:
    if isinstance(state["messages"][-1], ToolMessage):
        return "meeting_agent"   # el usuario canceló
    return "meeting_tools"       # el usuario confirmó


# --------------------------------------------------------------------------- #
# Grafo
# --------------------------------------------------------------------------- #

graph = StateGraph(AgentState)

graph.add_node("supervisor", supervisor)
graph.add_node("rag_agent", rag_agent)
graph.add_node("generate_query", generate_query)
graph.add_node("rag_tools", ToolNode(rag_tools))
graph.add_node("meeting_agent", meeting_agent)
graph.add_node("human_approval", human_approval)
graph.add_node("meeting_tools", ToolNode(meeting_tools))

graph.set_entry_point("supervisor")

graph.add_conditional_edges("supervisor", route_supervisor, {
    "rag_agent": "rag_agent",
    "meeting_agent": "meeting_agent",
    END: END,
})

# Rama RAG: rag_agent -> generate_query -> rag_tools -> rag_agent -> fin
graph.add_conditional_edges("rag_agent", route_rag, {
    "generate_query": "generate_query",
    END: END,
})
graph.add_edge("generate_query", "rag_tools")
graph.add_edge("rag_tools", "rag_agent")

# Rama meeting: meeting_agent -> (human_approval) -> meeting_tools -> meeting_agent -> fin
graph.add_conditional_edges("meeting_agent", route_meeting, {
    "human_approval": "human_approval",
    "meeting_tools": "meeting_tools",
    END: END,
})
graph.add_conditional_edges("human_approval", after_approval, {
    "meeting_tools": "meeting_tools",
    "meeting_agent": "meeting_agent",
})
graph.add_edge("meeting_tools", "meeting_agent")

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
