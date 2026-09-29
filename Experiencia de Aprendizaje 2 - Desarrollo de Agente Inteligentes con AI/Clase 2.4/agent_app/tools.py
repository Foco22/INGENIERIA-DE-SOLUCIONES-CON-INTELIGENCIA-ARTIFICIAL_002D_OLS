import sqlite3
import os
import re
import json
import html
import difflib
import unicodedata
from langchain_core.tools import tool

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "database.db")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")


def get_schema() -> str:
    """Returns the schema of all tables in the database (injected into the SQL agent prompt)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cur.fetchall()
    # Valores posibles de columnas categóricas, para no filtrar con 'cancelados' en vez de 'cancelado'.
    values = [
        f"- {table}.{column}: " + ", ".join(
            f"'{v}'" for (v,) in cur.execute(f"SELECT DISTINCT {column} FROM {table} ORDER BY 1")
        )
        for table, column in [("pedidos", "estado"), ("productos", "categoria"), ("clientes", "ciudad")]
    ]
    conn.close()
    return "\n\n".join(t[0] for t in tables if t[0]) + "\n\nValores posibles:\n" + "\n".join(values)


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


# Columnas de texto donde el usuario suele mencionar valores por nombre.
SEARCHABLE_COLUMNS = [
    ("clientes", "nombre"), ("clientes", "ciudad"),
    ("productos", "nombre"), ("productos", "categoria"),
    ("pedidos", "estado"),
]


def _normalize(text: str) -> str:
    """Minúsculas y sin tildes: 'García' -> 'garcia'."""
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c)).strip()


@tool
def find_value(text: str) -> str:
    """
    Finds how a name is spelled exactly in the database (customers, cities, products,
    categories or order statuses). Tolerates accents, casing, partial names and typos.
    Use it BEFORE filtering by a name in a query.

    Args:
        text: the name as the user wrote it, e.g. "ana garcia" or "laptop".
    """
    query = _normalize(text)
    conn = sqlite3.connect(DB_PATH)
    matches = []
    for table, column in SEARCHABLE_COLUMNS:
        for (value,) in conn.execute(f"SELECT DISTINCT {column} FROM {table}"):
            candidate = _normalize(str(value))
            score = difflib.SequenceMatcher(None, query, candidate).ratio()
            if query in candidate:
                score = max(score, 0.9)
            if score >= 0.6:
                matches.append((round(score, 2), f"{table}.{column}", value))
    conn.close()
    matches.sort(reverse=True)
    if not matches:
        return f"No value similar to '{text}' was found."
    return json.dumps(
        [{"column": col, "exact_value": val, "similarity": sc} for sc, col, val in matches[:5]],
        ensure_ascii=False,
    )


sql_tools = [find_value, execute_query]

# ---------------------------------------------------------------------------
# Tools del agente de reportes. Son genéricas: las queries específicas y la
# plantilla HTML viven en la skill "reporte-ventas" (skills/reporte-ventas/).
# ---------------------------------------------------------------------------

def _resolve(virtual_path: str) -> str:
    """Convierte una ruta virtual ("/skills/...") en una ruta real dentro del proyecto."""
    real = os.path.abspath(os.path.join(PROJECT_ROOT, virtual_path.lstrip("/")))
    if not real.startswith(PROJECT_ROOT + os.sep):
        raise ValueError(f"Ruta fuera del proyecto: {virtual_path}")
    return real


def _run_named_queries(sql_path: str, desde: str, hasta: str, params: dict | None = None) -> dict:
    """Ejecuta cada bloque '-- name: ...' del archivo y combina sus columnas en un dict."""
    bindings = {"desde": desde, "hasta": hasta, **(params or {})}
    with open(_resolve(sql_path), encoding="utf-8") as f:
        blocks = re.split(r"^-- name: .*$", f.read(), flags=re.M)[1:]
    values: dict = {}
    conn = sqlite3.connect(DB_PATH)
    try:
        for block in blocks:
            cur = conn.execute(block.strip().rstrip(";"), bindings)
            row = cur.fetchone() or ()
            values.update({d[0]: v for d, v in zip(cur.description, row)})
    finally:
        conn.close()
    return values


def _html_rows_to_text(rows_html: str | None) -> str:
    text = re.sub(r"</tr>", "\n", rows_html or "")
    text = re.sub(r"</td>\s*<td[^>]*>", " | ", text)
    return re.sub(r"<[^>]+>", "", text).strip()


@tool
def run_sql_file(sql_path: str, desde: str, hasta: str, params: dict | None = None) -> str:
    """
    Ejecuta las queries nombradas ('-- name: ...') de un archivo .sql de una skill
    con los parámetros :desde y :hasta, y devuelve los resultados combinados.

    Args:
        sql_path: ruta virtual del archivo, ej. "/skills/reporte-ventas/references/queries.sql".
        desde: fecha inicial YYYY-MM-DD.
        hasta: fecha final YYYY-MM-DD.
        params: parámetros extra que use el .sql, ej. {"cliente": "Ana García"} para :cliente.
    """
    try:
        values = _run_named_queries(sql_path, desde, hasta, params)
    except Exception as e:
        return f"Error ejecutando {sql_path}: {e}"
    readable = {
        k: _html_rows_to_text(v) if k.startswith("FILAS_") else v
        for k, v in values.items()
    }
    return json.dumps(readable, ensure_ascii=False, indent=1)


@tool
def render_report(sql_path: str, template_path: str, output_path: str,
                  desde: str, hasta: str, periodo: str, resumen: str,
                  params: dict | None = None) -> str:
    """
    Genera un reporte HTML: ejecuta las queries del archivo .sql, reemplaza los marcadores
    {{ALIAS}} de la plantilla con los resultados (más PERIODO, DESDE, HASTA y RESUMEN)
    y escribe el archivo final.

    Args:
        sql_path: ruta virtual del .sql de la skill.
        template_path: ruta virtual de la plantilla HTML de la skill.
        output_path: ruta virtual del HTML a generar, ej. "/reports/reporte_ventas.html".
        desde: fecha inicial YYYY-MM-DD.
        hasta: fecha final YYYY-MM-DD.
        periodo: texto legible del período, ej. "Q1 2025 (Ene – Mar)".
        resumen: análisis escrito de 3 a 5 oraciones.
        params: parámetros extra que use el .sql, ej. {"cliente": "Ana García"} para :cliente.
    """
    try:
        values = _run_named_queries(sql_path, desde, hasta, params)
        with open(_resolve(template_path), encoding="utf-8") as f:
            template = f.read()
    except Exception as e:
        return f"Error preparando el reporte: {e}"

    if all(v is None for v in values.values()):
        return f"Las queries no devolvieron datos entre {desde} y {hasta}. Revisa el período o los filtros."

    values.update({
        "PERIODO": html.escape(periodo), "DESDE": desde, "HASTA": hasta,
        "RESUMEN": html.escape(resumen),
    })
    rendered = re.sub(
        r"\{\{(\w+)\}\}",
        lambda m: "" if values.get(m.group(1)) is None else str(values[m.group(1)]),
        template,
    )
    missing = sorted(set(re.findall(r"\{\{(\w+)\}\}", template)) - values.keys())
    if missing:
        return f"Error: la plantilla usa marcadores sin valor: {missing}"

    out = _resolve(output_path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(rendered)
    return f"Reporte generado en {output_path} ({len(rendered):,} caracteres)."


report_tools = [run_sql_file, render_report]


def get_latest_report() -> tuple[str, float] | None:
    """Devuelve (ruta, mtime) del HTML más reciente en reports/, o None si no hay ninguno."""
    if not os.path.isdir(REPORTS_DIR):
        return None
    paths = [os.path.join(REPORTS_DIR, f) for f in os.listdir(REPORTS_DIR) if f.endswith(".html")]
    if not paths:
        return None
    latest = max(paths, key=os.path.getmtime)
    return latest, os.path.getmtime(latest)
