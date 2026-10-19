import streamlit as st
from langchain_core.messages import HumanMessage
from agent_app.agent import app
import uuid

st.title("Agente Matematico")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.markdown(f"**Sesion:** `{st.session_state.thread_id[:8]}...`")
    if st.button("Nueva conversacion", type="primary"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.rerun()

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

config = {"configurable": {"thread_id": st.session_state.thread_id}}

if prompt := st.chat_input("Escribe tu pregunta matematica..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    result = app.invoke({"messages": [HumanMessage(content=prompt)]}, config=config)
    answer = result["messages"][-1].content
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)