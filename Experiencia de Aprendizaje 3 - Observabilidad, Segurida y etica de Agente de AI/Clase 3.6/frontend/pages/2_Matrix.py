import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api import api, CATEGORY_EMOJI

st.set_page_config(page_title="Matriz", page_icon="🎯", layout="wide")
st.title("🎯 Matriz Impacto-Urgencia")
st.caption("Cuadrante tipo Eisenhower. urgency y quadrant calculados por el backend.")

try:
    matrix = api.get_matrix()
except Exception as e:
    st.error(f"No se pudo conectar al backend: {e}")
    st.stop()


def format_deadline(deadline):
    if not deadline:
        return "Sin fecha"
    return deadline[:10]


def render_quadrant(label, tasks):
    st.markdown(f"### {label}")
    if not tasks:
        st.caption("Sin tareas")
        return
    for t in tasks:
        emoji = CATEGORY_EMOJI.get(t["category"], "")
        with st.container(border=True):
            st.markdown(f"**{t['title']}**")
            st.caption(f"{emoji} {t['category']} · 📅 {format_deadline(t['deadline'])}")


col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("🔴 **Urgente + Importante**")
        render_quadrant("Q1 — Hacer ahora", matrix.get("Q1", []))

with col2:
    with st.container(border=True):
        st.markdown("🔵 **No urgente + Importante**")
        render_quadrant("Q2 — Planificar", matrix.get("Q2", []))

col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.markdown("🟡 **Urgente + No importante**")
        render_quadrant("Q3 — Delegar", matrix.get("Q3", []))

with col4:
    with st.container(border=True):
        st.markdown("⚫ **No urgente + No importante**")
        render_quadrant("Q4 — Eliminar", matrix.get("Q4", []))
