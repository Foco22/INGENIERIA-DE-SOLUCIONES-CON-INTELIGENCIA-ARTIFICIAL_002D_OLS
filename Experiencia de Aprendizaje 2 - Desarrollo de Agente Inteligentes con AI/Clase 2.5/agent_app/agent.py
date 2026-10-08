from typing import Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from agent_app.tools import tools
from agent_app.prompts import (
    AGENT_SYSTEM_PROMPT,
    NOT_FOUND_ANSWER,
    VALIDATION_RETRY_PROMPT,
    VALIDATOR_SYSTEM_PROMPT,
)

# Reintentos que el validador concede antes de reemplazar la respuesta por "No encontré...".
MAX_VALIDATION_RETRIES = 1


# ---------- State ----------
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]   # historial: Human / AI (con tool_calls) / Tool
    tool_used: bool                           # ¿se invocó la tool en este turno?
    tool_calls: list[dict]                    # [{"name", "args": {"query", "year"}}]
    retrieved_docs: list[dict]                # [{"year", "page", "content"}] devueltos por el RAG
    validations: list[dict]                   # [{"supported", "reason", "answer"}] uno por intento
    validator_feedback: str                   # motivo del rechazo, se le pasa al agente en el reintento


# ---------- Tools ----------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}


class Validation(BaseModel):
    supported: bool
    reason: str


validator = llm.with_structured_output(Validation)


# ---------- Nodos ----------
def reset_node(state: AgentState) -> dict:
    # Los campos de trazabilidad son por turno: sin esto arrastrarían datos de la pregunta anterior.
    return {"tool_used": False, "tool_calls": [], "retrieved_docs": [],
            "validations": [], "validator_feedback": ""}


def agent_node(state: AgentState) -> dict:
    messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT)] + state["messages"]
    # El feedback del validador va solo en esta llamada: no queda en el historial de la conversación.
    if state.get("validator_feedback"):
        messages.append(SystemMessage(content=VALIDATION_RETRY_PROMPT.format(reason=state["validator_feedback"])))
    response = llm_with_tools.invoke(messages)
    return {"messages": [response], "validator_feedback": ""}


def tools_node(state: AgentState) -> dict:
    # Implementado a mano (en vez de ToolNode) para guardar argumentos y documentos en el estado.
    last = state["messages"][-1]
    tool_messages, calls, docs = [], [], []
    for call in last.tool_calls:
        tool_message = tools_by_name[call["name"]].invoke(call)   # devuelve un ToolMessage
        tool_messages.append(tool_message)
        calls.append({"name": call["name"], "args": call["args"]})
        docs.extend(tool_message.artifact or [])
    return {
        "messages": tool_messages,
        "tool_used": True,
        "tool_calls": state.get("tool_calls", []) + calls,
        "retrieved_docs": state.get("retrieved_docs", []) + docs,
    }


def validator_node(state: AgentState) -> dict:
    """Verifica que cada cifra de la respuesta esté respaldada explícitamente por los chunks recuperados."""
    answer_msg = state["messages"][-1]
    question = next(m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage))
    context = "\n\n---\n\n".join(d["content"] for d in state["retrieved_docs"])
    verdict = validator.invoke([
        SystemMessage(content=VALIDATOR_SYSTEM_PROMPT),
        HumanMessage(content=f"Pregunta: {question}\n\nFragmentos recuperados:\n{context}\n\n"
                             f"Respuesta del agente: {answer_msg.content}"),
    ])
    validations = state.get("validations", []) + [
        {"supported": verdict.supported, "reason": verdict.reason, "answer": answer_msg.content}
    ]
    if verdict.supported:
        return {"validations": validations}

    # La respuesta no respaldada se borra del historial: no debe quedar como "verdad" en la memoria.
    update = {"validations": validations, "messages": [RemoveMessage(id=answer_msg.id)]}
    if len(validations) <= MAX_VALIDATION_RETRIES:
        update["validator_feedback"] = verdict.reason
    else:
        update["messages"].append(AIMessage(content=NOT_FOUND_ANSWER))
    return update


# ---------- Aristas ----------
def route_after_agent(state: AgentState) -> Literal["tools", "validator", "__end__"]:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    # Solo se valida lo que viene del RAG: saludos y definiciones no tienen chunks contra qué comparar.
    if state.get("tool_used"):
        return "validator"
    return END


def route_after_validator(state: AgentState) -> Literal["agent", "__end__"]:
    return "agent" if state.get("validator_feedback") else END


builder = StateGraph(AgentState)
builder.add_node("reset", reset_node)
builder.add_node("agent", agent_node)
builder.add_node("tools", tools_node)
builder.add_node("validator", validator_node)

builder.add_edge(START, "reset")
builder.add_edge("reset", "agent")
builder.add_conditional_edges("agent", route_after_agent,
                              {"tools": "tools", "validator": "validator", END: END})
builder.add_edge("tools", "agent")
builder.add_conditional_edges("validator", route_after_validator, {"agent": "agent", END: END})

graph = builder.compile(checkpointer=MemorySaver())
