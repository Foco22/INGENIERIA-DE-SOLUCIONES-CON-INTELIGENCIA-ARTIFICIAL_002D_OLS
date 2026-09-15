"""Conexion a SQLite e inicializacion del schema."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from src.utils.config import SCHEMA_PATH, settings


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Abre la conexion a SQLite. WAL para que la UI pueda leer mientras se escribe."""
    path = db_path or settings.db_path
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path | None = None) -> None:
    """Crea las tablas si no existen y aplica migraciones pendientes. Idempotente."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_connection(db_path) as conn:
        conn.executescript(schema)
        _migrate(conn)


def _migrate(conn: sqlite3.Connection) -> None:
    """Columnas agregadas despues del primer schema (CREATE IF NOT EXISTS no las crea)."""
    columns = {row[1] for row in conn.execute("PRAGMA table_info(jobs)")}
    if "search_query" not in columns:
        conn.execute("ALTER TABLE jobs ADD COLUMN search_query TEXT")
