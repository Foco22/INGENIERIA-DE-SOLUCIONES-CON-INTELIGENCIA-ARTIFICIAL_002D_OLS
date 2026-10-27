import streamlit as st
from langchain_core.messages import HumanMessage
from langchain_core.callbacks import get_usage_metadata_callback
from agent_app.agent import app
from agent_app.costs import summarize_usage, record_cost, request_failed
from agent_app.telemetry import record_error
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
        if msg.get("caption"):
            st.caption(msg["caption"])

config = {"configurable": {"thread_id": st.session_state.thread_id}}

if prompt := st.chat_input("Escribe tu pregunta matematica..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    failed = False
    with get_usage_metadata_callback() as usage_cb:
        try:
            result = app.invoke({"messages": [HumanMessage(content=prompt)]}, config=config)
            answer = result["messages"][-1].content
            failed = request_failed(result["messages"])
        except Exception as e:
            failed = True
            record_error(st.session_state.thread_id, "app", e)
            answer = "Lo siento, tuve un problema al procesar tu pregunta. Intenta de nuevo."
    cost = summarize_usage(usage_cb.usage_metadata)
    record_cost(st.session_state.thread_id, prompt, cost, failed)
    caption = (
        f"Prompt tokens: {cost['prompt_tokens']} | "
        f"Completion tokens: {cost['completion_tokens']} | "
        f"Costo: ${cost['cost_usd']:.6f} USD"
    )
    st.session_state.chat_history.append(
        {"role": "assistant", "content": answer, "caption": caption}
    )
    with st.chat_message("assistant"):
        st.write(answer)
        st.caption(caption)