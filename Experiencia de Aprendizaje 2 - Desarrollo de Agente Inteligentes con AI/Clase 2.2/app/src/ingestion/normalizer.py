"""DataFrame de JobSpy -> list[JobOffer]. Limpieza y dedupe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from src.models import JobOffer

COLUMNS = [
    "site", "title", "company", "location", "date_posted", "job_url",
    "description", "is_remote", "min_amount", "max_amount", "currency",
]


def job_id_for(job_url: str) -> str:
    """Id estable derivado de la URL: re-ingestar la misma oferta da el mismo id."""
    return hashlib.sha1(job_url.strip().encode("utf-8")).hexdigest()[:16]


def dataframe_to_offers(df: pd.DataFrame) -> list[JobOffer]:
    """Normaliza el DataFrame de JobSpy y descarta filas sin URL o sin titulo."""
    offers: list[JobOffer] = []
    seen: set[str] = set()

    for _, row in df.iterrows():
        url = _clean(row.get("job_url"))
        title = _clean(row.get("title"))
        if not url or not title:
            continue

        job_id = job_id_for(url)
        if job_id in seen:
            continue
        seen.add(job_id)

        offers.append(
            JobOffer(
                id=job_id,
                site=_clean(row.get("site")),
                title=title,
                company=_clean(row.get("company")),
                location=_clean(row.get("location")),
                date_posted=_clean(row.get("date_posted")),
                job_url=url,
                description=_clean(row.get("description")),
                is_remote=_to_bool(row.get("is_remote")),
                min_amount=_to_float(row.get("min_amount")),
                max_amount=_to_float(row.get("max_amount")),
                currency=_clean(row.get("currency")),
                raw_json=_row_json(row),
            )
        )
    return offers


def csv_to_offers(path: Path) -> list[JobOffer]:
    """Lee un CSV de JobSpy ya guardado y lo normaliza."""
    df = pd.read_csv(path, encoding="utf-8")
    return dataframe_to_offers(df)


def _clean(value) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text or None


def _to_bool(value) -> bool | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "si"}


def _to_float(value) -> float | None:
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _row_json(row: pd.Series) -> str:
    """Guarda la fila original completa, por si despues sirve un campo que hoy se ignora."""
    return json.dumps(
        {k: (None if pd.isna(v) else str(v)) for k, v in row.items()},
        ensure_ascii=False,
    )
