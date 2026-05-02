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


@tool
def generate_report() -> dict:
    """
    Genera un reporte ejecutivo de ventas consultando la base de datos.
    Solo considera pedidos con estado 'entregado'.

    Retorna un diccionario con:
    - total_vendido: monto total vendido en el período
    - mejor_mes: mes con mayor venta (mes, total)
    - peor_mes: mes con menor venta (mes, total)
    - clientes_ranking: lista de clientes ordenados de mayor a menor por monto comprado
    - producto_mas_vendido: producto con más unidades vendidas (nombre, unidades)
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Total vendido
    cur.execute("""
        SELECT SUM(dp.cantidad * dp.precio_unitario)
        FROM detalle_pedidos dp
        JOIN pedidos p ON dp.pedido_id = p.id
        WHERE p.estado = 'entregado'
    """)
    total_vendido = cur.fetchone()[0] or 0

    # Ventas por mes
    cur.execute("""
        SELECT strftime('%Y-%m', p.fecha) AS mes,
               SUM(dp.cantidad * dp.precio_unitario) AS total
        FROM detalle_pedidos dp
        JOIN pedidos p ON dp.pedido_id = p.id
        WHERE p.estado = 'entregado'
        GROUP BY mes
        ORDER BY total DESC
    """)
    ventas_por_mes = cur.fetchall()

    mejor_mes = {"mes": ventas_por_mes[0][0], "total": ventas_por_mes[0][1]} if ventas_por_mes else None
    peor_mes  = {"mes": ventas_por_mes[-1][0], "total": ventas_por_mes[-1][1]} if ventas_por_mes else None

    # Clientes ranking de mayor a menor
    cur.execute("""
        SELECT c.nombre, SUM(dp.cantidad * dp.precio_unitario) AS total_compras
        FROM clientes c
        JOIN pedidos p ON c.id = p.cliente_id
        JOIN detalle_pedidos dp ON p.id = dp.pedido_id
        WHERE p.estado = 'entregado'
        GROUP BY c.id, c.nombre
        ORDER BY total_compras DESC
    """)
    clientes_ranking = [{"nombre": row[0], "total": row[1]} for row in cur.fetchall()]

    # Producto más vendido por unidades
    cur.execute("""
        SELECT pr.nombre, SUM(dp.cantidad) AS unidades
        FROM detalle_pedidos dp
        JOIN productos pr ON dp.producto_id = pr.id
        JOIN pedidos p ON dp.pedido_id = p.id
        WHERE p.estado = 'entregado'
        GROUP BY pr.id, pr.nombre
        ORDER BY unidades DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    producto_mas_vendido = {"nombre": row[0], "unidades": row[1]} if row else None

    conn.close()

    return {
        "total_vendido": total_vendido,
        "mejor_mes": mejor_mes,
        "peor_mes": peor_mes,
        "clientes_ranking": clientes_ranking,
        "producto_mas_vendido": producto_mas_vendido,
    }


report_tools = [generate_report]
