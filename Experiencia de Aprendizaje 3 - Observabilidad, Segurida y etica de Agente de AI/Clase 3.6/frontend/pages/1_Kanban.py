import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api import api, CATEGORIES, IMPORTANCES, CATEGORY_EMOJI

st.set_page_config(page_title="Kanban", page_icon="📋", layout="wide")
st.title("📋 Kanban Board")

# --- Sidebar filters ---
st.sidebar.header("Filtros")
filter_category = st.sidebar.selectbox("Categoría", ["Todas"] + CATEGORIES)
filter_importance = st.sidebar.selectbox("Importancia", ["Todas", "high", "low"])

category_param = filter_category if filter_category != "Todas" else None
importance_param = filter_importance if filter_importance != "Todas" else None

# --- Load tasks ---
try:
    tasks = api.get_tasks(category=category_param, importance=importance_param)
except Exception as e:
    st.error(f"No se pudo conectar al backend: {e}")
    st.stop()

todo = [t for t in tasks if t["status"] == "todo"]
doing = [t for t in tasks if t["status"] == "doing"]
done = [t for t in tasks if t["status"] == "done"]


def format_deadline(deadline):
    if not deadline:
        return "Sin fecha"
    return deadline[:10]


def task_card(task, col_key):
    emoji = CATEGORY_EMOJI.get(task["category"], "")
    importance_badge = "🔴 Alta" if task["importance"] == "high" else "⚪ Baja"
    with st.container(border=True):
        st.markdown(f"**{task['title']}**")
        st.caption(f"{emoji} {task['category']} · {importance_badge} · 📅 {format_deadline(task['deadline'])}")

        btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 1])

        with btn_col1:
            if task["status"] != "todo" and st.button("⬅ Retroceder", key=f"back_{col_key}_{task['id']}"):
                new_status = "todo" if task["status"] == "doing" else "doing"
                api.patch_status(task["id"], new_status)
                st.rerun()

        with btn_col2:
            if task["status"] != "done" and st.button("Avanzar ➡", key=f"fwd_{col_key}_{task['id']}"):
                new_status = "doing" if task["status"] == "todo" else "done"
                api.patch_status(task["id"], new_status)
                st.rerun()

        with btn_col3:
            if st.button("🗑", key=f"del_{col_key}_{task['id']}"):
                api.delete_task(task["id"])
                st.rerun()

        with st.expander("Editar"):
            with st.form(key=f"edit_{task['id']}"):
                new_title = st.text_input("Título", value=task["title"])
                new_desc = st.text_area("Descripción", value=task["description"] or "")
                new_importance = st.selectbox(
                    "Importancia",
                    IMPORTANCES,
                    index=IMPORTANCES.index(task["importance"])
                )
                new_category = st.selectbox(
                    "Categoría",
                    CATEGORIES,
                    index=CATEGORIES.index(task["category"])
                )
                new_deadline = st.text_input(
                    "Deadline (YYYY-MM-DDTHH:MM:SSZ)",
                    value=task["deadline"] or ""
                )
                if st.form_submit_button("Guardar"):
                    api.update_task(task["id"], {
                        "title": new_title,
                        "description": new_desc or None,
                        "importance": new_importance,
                        "category": new_category,
                        "deadline": new_deadline or None,
                    })
                    st.rerun()


# --- Columns ---
col_todo, col_doing, col_done = st.columns(3)

with col_todo:
    st.subheader(f"📌 To Do ({len(todo)})")
    for t in todo:
        task_card(t, "todo")

with col_doing:
    st.subheader(f"⚡ Doing ({len(doing)})")
    for t in doing:
        task_card(t, "doing")

with col_done:
    st.subheader(f"✅ Done ({len(done)})")
    for t in done:
        task_card(t, "done")

# --- New task form ---
st.divider()
st.subheader("➕ Nueva tarea")
with st.form("new_task"):
    c1, c2 = st.columns(2)
    with c1:
        title = st.text_input("Título *")
        description = st.text_area("Descripción")
        category = st.selectbox("Categoría *", CATEGORIES)
    with c2:
        status = st.selectbox("Status", ["todo", "doing", "done"])
        importance = st.selectbox("Importancia", ["low", "high"])
        deadline = st.text_input("Deadline (YYYY-MM-DDTHH:MM:SSZ)", placeholder="2026-06-30T23:59:00Z")

    if st.form_submit_button("Crear tarea"):
        if not title:
            st.error("El título es obligatorio.")
        else:
            api.create_task({
                "title": title,
                "description": description or None,
                "category": category,
                "status": status,
                "importance": importance,
                "deadline": deadline or None,
            })
            st.success("Tarea creada.")
            st.rerun()
