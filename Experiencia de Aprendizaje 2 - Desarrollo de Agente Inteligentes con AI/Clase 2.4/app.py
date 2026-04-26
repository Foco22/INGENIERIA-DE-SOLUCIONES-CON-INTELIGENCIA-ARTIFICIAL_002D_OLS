import uuid
import streamlit as st
import plotly.io as pio
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from agent_app.agent import graph
from agent_app.tools import get_last_chart, clear_last_chart

load_dotenv()

st.set_page_config(page_title="Asistente Multi-Agente")
st.title("Asistente Multi-Agente")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.caption(f"Session: `{st.session_state.thread_id[:8]}...`")
    if st.button("🗑️ Nueva conversación", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.history = []
        st.rerun()


for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        if msg.get("is_chart"):
            fig = pio.from_json(msg["content"])
            st.plotly_chart(fig, use_container_width=True)
        if msg.get("text"):
            st.write(msg["text"])
        elif not msg.get("is_chart"):
            st.write(msg["content"])


if prompt := st.chat_input("¿Qué quieres saber sobre las ventas?"):
    st.session_state.history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Procesando..."):
            clear_last_chart()
            config = {
                "configurable": {"thread_id": st.session_state.thread_id},
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

        chart_json = get_last_chart()

        if chart_json:
            fig = pio.from_json(chart_json)
            st.plotly_chart(fig, use_container_width=True)
            st.write(last_content)
            st.session_state.history.append({
                "role": "assistant",
                "content": chart_json,
                "text": last_content,
                "is_chart": True,
            })
        else:
            st.write(last_content)
            st.session_state.history.append({"role": "assistant", "content": last_content})
