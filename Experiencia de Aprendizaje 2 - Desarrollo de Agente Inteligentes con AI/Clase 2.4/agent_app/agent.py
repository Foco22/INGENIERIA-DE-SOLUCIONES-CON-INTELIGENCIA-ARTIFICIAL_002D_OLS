from typing import Literal, Annotated, Optional
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel

from agent_app.tools import sql_tools, python_tools
from agent_app.prompts import SQL_SYSTEM_PROMPT, PYTHON_SYSTEM_PROMPT, SUPERVISOR_SYSTEM_PROMPT


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    next: str


class Route(BaseModel):
    next: Literal["sql_agent", "python_agent", "sql_then_python", "FINISH"]
    response: Optional[str] = None


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

sql_agent    = create_react_agent(llm, sql_tools,    prompt=SQL_SYSTEM_PROMPT)
python_agent = create_react_agent(llm, python_tools, prompt=PYTHON_SYSTEM_PROMPT)


def summarize_for(messages: list, role: str) -> HumanMessage:
    role_instruction = {
        "sql": (
            "Resume en 2-3 oraciones qué consulta SQL debe realizarse según la conversación. "
            "Incluye filtros, agrupaciones o condiciones relevantes. Solo describe la tarea, no ejecutes nada."
        ),
        "python": (
            "Resume en 2-3 oraciones qué visualización debe generarse y con qué datos. "
            "Incluye los datos numéricos disponibles en la conversación que el agente necesita para graficar. "
            "Solo describe la tarea, no ejecutes nada."
        ),
    }

    response = llm.invoke([
        SystemMessage(content=(
            f"Eres un asistente que resume conversaciones para delegarlas a un agente especializado.\n"
            f"Instrucción: {role_instruction[role]}"
        )),
        *messages,
    ])
    return HumanMessage(content=response.content)


def supervisor_node(state: AgentState) -> dict:
    supervisor_llm = llm.with_structured_output(Route)
    messages = [{"role": "system", "content": SUPERVISOR_SYSTEM_PROMPT}] + state["messages"]
    result = supervisor_llm.invoke(messages)
    updates: dict = {"next": result.next}
    if result.response:
        updates["messages"] = [AIMessage(content=result.response)]
    return updates


def sql_node(state: AgentState, config: RunnableConfig) -> dict:
    summary = summarize_for(state["messages"], "sql")
    result = sql_agent.invoke({"messages": [summary]}, config)
    return {"messages": result["messages"]}


def python_node(state: AgentState, config: RunnableConfig) -> dict:
    summary = summarize_for(state["messages"], "python")
    result = python_agent.invoke({"messages": [summary]}, config)
    return {"messages": result["messages"]}


def supervisor_route(state: AgentState) -> Literal["sql_agent", "python_agent", "__end__"]:
    if state["next"] == "FINISH":
        return END
    if state["next"] == "sql_then_python":
        return "sql_agent"
    return state["next"]


def after_sql_route(state: AgentState) -> Literal["python_agent", "__end__"]:
    if state["next"] == "sql_then_python":
        return "python_agent"
    return END


builder = StateGraph(AgentState)
builder.add_node("supervisor",   supervisor_node)
builder.add_node("sql_agent",    sql_node)
builder.add_node("python_agent", python_node)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", supervisor_route)
builder.add_conditional_edges("sql_agent",  after_sql_route)
builder.add_edge("python_agent", END)

graph = builder.compile(checkpointer=MemorySaver())
