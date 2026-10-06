from typing import Annotated, Literal
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from agent_app.tools import tools
from agent_app.prompts import AGENT_SYSTEM_PROMPT


# ---------- State ----------
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]   # historial: Human / AI (con tool_calls) / Tool
    tool_used: bool                           # ¿se invocó la tool en este turno?
    tool_calls: list[dict]                    # [{"name", "args": {"query", "year"}}]
    retrieved_docs: list[dict]                # [{"year", "page", "content"}] devueltos por el RAG


# ---------- Tools ----------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}


# ---------- Nodos ----------
def reset_node(state: AgentState) -> dict:
    # Los campos de trazabilidad son por turno: sin esto arrastrarían datos de la pregunta anterior.
    return {"tool_used": False, "tool_calls": [], "retrieved_docs": []}


def agent_node(state: AgentState) -> dict:
    messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


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


# ---------- Aristas ----------
def route_after_agent(state: AgentState) -> Literal["tools", "__end__"]:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


builder = StateGraph(AgentState)
builder.add_node("reset", reset_node)
builder.add_node("agent", agent_node)
builder.add_node("tools", tools_node)

builder.add_edge(START, "reset")
builder.add_edge("reset", "agent")
builder.add_conditional_edges("agent", route_after_agent, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")

graph = builder.compile(checkpointer=MemorySaver())
