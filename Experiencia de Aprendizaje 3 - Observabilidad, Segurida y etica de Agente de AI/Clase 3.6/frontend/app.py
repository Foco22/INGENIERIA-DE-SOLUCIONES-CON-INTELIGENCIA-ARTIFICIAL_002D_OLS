import streamlit as st

st.set_page_config(
    page_title="Productivity App",
    page_icon="✅",
    layout="wide",
)

st.title("✅ Productivity App")
st.markdown("Bienvenido a tu app de productividad personal.")

st.markdown("""
### Módulos disponibles

| Módulo | Descripción |
|--------|-------------|
| 📋 **Kanban** | Gestiona tus tareas en columnas To Do / Doing / Done |
| 🎯 **Matriz** | Prioriza con la Matriz Impacto-Urgencia (Eisenhower) |
| 📊 **Dashboard** | Analiza tu cumplimiento semanal con gráficos |

Usa el menú lateral para navegar entre módulos.
""")
