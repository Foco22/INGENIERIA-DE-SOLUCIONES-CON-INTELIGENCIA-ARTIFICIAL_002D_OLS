import sqlite3
import os
import json
import plotly.graph_objects as go
from langchain_core.tools import tool

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "database.db")


@tool
def get_schema() -> str:
    """Returns the schema of all tables in the database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cur.fetchall()
    conn.close()
    return "\n\n".join(t[0] for t in tables if t[0])


@tool
def execute_query(query: str) -> str:
    """Executes a SQL query against the database and returns the results."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        conn.close()
        return json.dumps({"columns": columns, "rows": rows})
    except Exception as e:
        conn.close()
        return f"Error ejecutando query: {e}"


sql_tools = [get_schema, execute_query]

# Almacena el último gráfico generado para que app.py lo recupere
_last_chart: list[str | None] = [None]


def get_last_chart() -> str | None:
    return _last_chart[0]


def clear_last_chart() -> None:
    _last_chart[0] = None


@tool
def transform_data_to_visualization(data: str, chart_type: str, title: str) -> str:
    """
    Creates a Plotly chart from query result data and stores it for display.

    Args:
        data: JSON string with 'columns' and 'rows' keys (output of execute_query).
        chart_type: Type of chart — 'bar', 'line', or 'pie'.
        title: Chart title.

    Returns:
        Confirmation message.
    """
    parsed = json.loads(data)
    columns = parsed["columns"]
    rows = parsed["rows"]

    x = [row[0] for row in rows]
    y = [row[1] for row in rows]

    x_label = columns[0]
    y_label = columns[1] if len(columns) > 1 else ""

    if chart_type == "bar":
        fig = go.Figure(go.Bar(x=x, y=y, name=y_label))
    elif chart_type == "line":
        fig = go.Figure(go.Scatter(x=x, y=y, mode="lines+markers", name=y_label))
    elif chart_type == "pie":
        fig = go.Figure(go.Pie(labels=x, values=y))
    else:
        fig = go.Figure(go.Bar(x=x, y=y, name=y_label))

    fig.update_layout(
        title={"text": title, "x": 0.5, "xanchor": "center"},
        xaxis_title=x_label,
        yaxis_title=y_label,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    _last_chart[0] = fig.to_json()
    return f"Gráfico '{title}' generado correctamente con {len(rows)} puntos de datos."


python_tools = [transform_data_to_visualization]
