"""Orquesta la ingesta: busca (o lee un CSV), normaliza y persiste."""

from __future__ import annotations

from pathlib import Path

from src.utils.db.database import init_db
from src.utils.db.repository import upsert_jobs
from src.utils.ingestion.jobspy_client import fetch_jobs
from src.utils.ingestion.normalizer import csv_to_offers, dataframe_to_offers


def ingest_from_search(
    query: str,
    location: str = "Santiago, Chile",
    results_wanted: int = 30,
    hours_old: int = 24 * 30,
) -> int:
    """Scrapea los portales y guarda las ofertas. Devuelve cuantas se persistieron."""
    init_db()
    df = fetch_jobs(query, location, results_wanted, hours_old)
    if df is None or df.empty:
        return 0
    return upsert_jobs(dataframe_to_offers(df, search_query=query))


def ingest_from_searches(
    queries: list[str],
    location: str = "Santiago, Chile",
    results_wanted: int = 30,
    hours_old: int = 24 * 30,
) -> dict[str, int]:
    """Corre varias busquedas y devuelve cuantas ofertas trajo cada una.

    El upsert es por job_url: una oferta que aparece en dos busquedas no se duplica.
    """
    return {
        query: ingest_from_search(query, location, results_wanted, hours_old)
        for query in queries
    }


def ingest_from_csv(path: Path) -> int:
    """Carga un CSV de JobSpy ya descargado."""
    init_db()
    if not path.exists():
        raise FileNotFoundError(f"No existe el CSV: {path}")
    return upsert_jobs(csv_to_offers(path))
