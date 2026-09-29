import os
import uuid
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Debe ir antes de importar el agente: ChatOpenAI lee OPENAI_API_KEY al crearse.
load_dotenv()

from agent_app.agent import graph
from agent_app.tools import get_latest_report


def show_report(html: str, file_name: str, key: str) -> None:
    components.html(html, height=900, scrolling=True)
    st.download_button("⬇️ Descargar HTML", html, file_name=file_name,
                       mime="text/html", key=key)


st.set_page_config(page_title="Asistente Multi-Agente")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "history" not in st.session_state:
    st.session_state.history = []

# Nuevo thread = nueva memoria en LangGraph y nuevo thread en LangSmith.
title_col, button_col = st.columns([3, 1], vertical_alignment="center")
title_col.title("Asistente Multi-Agente")
if button_col.button("🔄 Nuevo thread", use_container_width=True):
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.history = []
    st.rerun()
st.caption(f"Thread: `{st.session_state.thread_id}`")


for i, msg in enumerate(st.session_state.history):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("report_html"):
            show_report(msg["report_html"], msg["report_name"], key=f"dl_{i}")


if prompt := st.chat_input("¿Qué quieres saber sobre las ventas?"):
    st.session_state.history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Procesando..."):
            report_before = get_latest_report()
            # LangSmith: un trace por pregunta, agrupados en un thread por conversación.
            config = {
                "configurable": {"thread_id": st.session_state.thread_id},
                "metadata": {"thread_id": st.session_state.thread_id},
                "run_name": "chat_turn",
                "recursion_limit": 15,
            }
            result = graph.invoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config,
            )

        last_content = result["messages"][-1].content
        if isinstance(last_content, list):
            last_content = " ".join(
                c.get("text", "") if isinstance(c, dict) else str(c)
                for c in last_content
            )

        st.write(last_content)
        entry = {"role": "assistant", "content": last_content}

        # Si el report_agent escribió un HTML nuevo en reports/, se muestra bajo la respuesta.
        report_after = get_latest_report()
        if report_after and report_after != report_before:
            with open(report_after[0], encoding="utf-8") as f:
                entry["report_html"] = f.read()
            entry["report_name"] = os.path.basename(report_after[0])
            show_report(entry["report_html"], entry["report_name"],
                        key=f"dl_{len(st.session_state.history)}")

        st.session_state.history.append(entry)
