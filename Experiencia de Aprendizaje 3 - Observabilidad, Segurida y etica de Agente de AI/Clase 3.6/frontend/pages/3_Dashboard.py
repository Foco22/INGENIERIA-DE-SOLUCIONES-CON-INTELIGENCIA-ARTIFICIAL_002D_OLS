import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api import api

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Dashboard Semanal")

try:
    data = api.get_weekly()
    tasks = api.get_tasks()
except Exception as e:
    st.error(f"No se pudo conectar al backend: {e}")
    st.stop()

period = data.get("period", {})
st.caption(f"Período: {period.get('start', '')} → {period.get('end', '')}")

# --- Metrics ---
m1, m2, m3 = st.columns(3)
m1.metric("Total de tareas", data.get("total", 0))
m2.metric("Completadas", data.get("completed", 0))
completion_rate = data.get("completion_rate", 0)
m3.metric("Tasa de cumplimiento", f"{completion_rate * 100:.1f}%")

st.divider()

# --- Bar chart: by category ---
by_category = data.get("by_category", {})
if by_category:
    cat_rows = [
        {"Categoría": cat, "Total": vals["total"], "Completadas": vals["completed"]}
        for cat, vals in by_category.items()
    ]
    df_cat = pd.DataFrame(cat_rows)
    df_melted = df_cat.melt(id_vars="Categoría", var_name="Tipo", value_name="Cantidad")
    fig_bar = px.bar(
        df_melted,
        x="Categoría",
        y="Cantidad",
        color="Tipo",
        barmode="group",
        title="Tareas por categoría",
        color_discrete_map={"Total": "#6366f1", "Completadas": "#22c55e"},
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("Sin datos por categoría.")

# --- Line chart: total tasks created per day ---
if tasks:
    df_tasks = pd.DataFrame(tasks)
    df_tasks["date"] = pd.to_datetime(df_tasks["created_at"]).dt.date
    df_daily = df_tasks.groupby("date").size().reset_index(name="count")
    df_daily["date"] = pd.to_datetime(df_daily["date"])
    fig_line = px.line(
        df_daily,
        x="date",
        y="count",
        markers=True,
        title="Total de tareas creadas por día",
        labels={"date": "Fecha", "count": "Tareas"},
        color_discrete_sequence=["#6366f1"],
    )
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("Sin datos diarios.")
