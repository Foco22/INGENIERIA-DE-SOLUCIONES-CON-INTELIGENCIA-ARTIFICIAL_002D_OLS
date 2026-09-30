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
from deepagents import create_deep_agent, FilesystemPermission
from deepagents.backends.filesystem import FilesystemBackend

from agent_app.tools import sql_tools, report_tools, get_schema, PROJECT_ROOT
from agent_app.prompts import SUPERVISOR_SYSTEM_PROMPT, SQL_SYSTEM_PROMPT, REPORT_SYSTEM_PROMPT


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    next: str


class Route(BaseModel):
    next: Literal["sql_agent", "report_agent", "FINISH"]
    response: Optional[str] = None


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def sql_prompt(state: dict) -> list:
    # El esquema se inyecta en cada llamada: el agente nunca escribe una query sin conocerlo.
    system = SystemMessage(content=SQL_SYSTEM_PROMPT.format(schema=get_schema()))
    return [system] + state["messages"]


# Agente SQL: genera y ejecuta queries según el esquema de la base de datos.
sql_agent = create_react_agent(llm, sql_tools, prompt=sql_prompt)

# Agente de reportes: Deep Agent con la skill "reporte-ventas" (skills/reporte-ventas/SKILL.md).
# El backend de filesystem expone la raíz del proyecto como "/": lee /skills/... y escribe /reports/...
report_agent = create_deep_agent(
    model=llm,
    tools=report_tools,
    system_prompt=REPORT_SYSTEM_PROMPT,
    backend=FilesystemBackend(root_dir=PROJECT_ROOT, virtual_mode=True),
    skills=["/skills/"],
    permissions=[
        FilesystemPermission(operations=["write"], paths=["/skills/**"], mode="deny"),
    ],
)


def supervisor_node(state: AgentState) -> dict:
    supervisor_llm = llm.with_structured_output(Route)
    messages = [{"role": "system", "content": SUPERVISOR_SYSTEM_PROMPT}] + state["messages"]
    result = supervisor_llm.invoke(messages)
    updates: dict = {"next": result.next}
    if result.response:
        updates["messages"] = [AIMessage(content=result.response)]
    return updates


def sql_node(state: AgentState, config: RunnableConfig) -> dict:
    # Recibe la conversación completa para entender preguntas de seguimiento ("¿y en marzo?").
    result = sql_agent.invoke({"messages": state["messages"]}, config)
    return {"messages": [result["messages"][-1]]}


def report_node(state: AgentState, config: RunnableConfig) -> dict:
    # Se pasan los últimos mensajes (solo texto) para respetar filtros como "primer trimestre"
    # y entender respuestas a su pregunta de aclaración ("el de pedidos").
    recent = [
        type(m)(content=m.content)
        for m in state["messages"][-4:]
        if isinstance(m, (HumanMessage, AIMessage)) and m.content
    ]
    result = report_agent.invoke(
        {"messages": recent},
        {**config, "recursion_limit": 40},
    )
    return {"messages": [result["messages"][-1]]}


def supervisor_route(state: AgentState) -> Literal["sql_agent", "report_agent", "__end__"]:
    return END if state["next"] == "FINISH" else state["next"]


builder = StateGraph(AgentState)
builder.add_node("supervisor",   supervisor_node)
builder.add_node("sql_agent",    sql_node)
builder.add_node("report_agent", report_node)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", supervisor_route)
builder.add_edge("sql_agent",    END)
builder.add_edge("report_agent", END)

graph = builder.compile(checkpointer=MemorySaver())
