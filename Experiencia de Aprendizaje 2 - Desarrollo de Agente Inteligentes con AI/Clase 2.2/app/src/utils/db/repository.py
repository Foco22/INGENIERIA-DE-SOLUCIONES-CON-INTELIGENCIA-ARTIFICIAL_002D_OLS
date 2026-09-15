"""Todo el SQL del proyecto vive aca. Nadie mas ejecuta queries."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd

from src.utils.config import BAND_LABELS
from src.utils.db.database import get_connection
from src.utils.models import Evaluation, JobOffer

# --------------------------------------------------------------------------- #
# Jobs
# --------------------------------------------------------------------------- #
UPSERT_JOB = """
INSERT INTO jobs (id, site, title, company, location, date_posted, job_url,
                  description, is_remote, min_amount, max_amount, currency, raw_json,
                  search_query)
VALUES (:id, :site, :title, :company, :location, :date_posted, :job_url,
        :description, :is_remote, :min_amount, :max_amount, :currency, :raw_json,
        :search_query)
ON CONFLICT(job_url) DO UPDATE SET
    title       = excluded.title,
    company     = excluded.company,
    location    = excluded.location,
    date_posted = excluded.date_posted,
    description = excluded.description,
    is_remote   = excluded.is_remote,
    min_amount  = excluded.min_amount,
    max_amount  = excluded.max_amount,
    currency    = excluded.currency,
    raw_json    = excluded.raw_json,
    -- una oferta puede aparecer en varias busquedas: se acumulan, sin repetir
    search_query = CASE
        WHEN excluded.search_query IS NULL THEN jobs.search_query
        WHEN jobs.search_query IS NULL THEN excluded.search_query
        WHEN instr(jobs.search_query, excluded.search_query) > 0 THEN jobs.search_query
        ELSE jobs.search_query || ', ' || excluded.search_query
    END
"""


def upsert_jobs(offers: list[JobOffer]) -> int:
    """Inserta o actualiza ofertas por job_url. Re-ingestar no duplica."""
    rows = []
    for offer in offers:
        row = offer.model_dump()
        row["is_remote"] = None if offer.is_remote is None else int(offer.is_remote)
        rows.append(row)
    with get_connection() as conn:
        conn.executemany(UPSERT_JOB, rows)
    return len(rows)


def get_pending_jobs(limit: int | None = None) -> list[JobOffer]:
    """Ofertas que todavia no se evaluan, de la mas reciente a la mas antigua."""
    sql = "SELECT * FROM jobs WHERE status = 'pending' ORDER BY date_posted DESC"
    if limit:
        sql += f" LIMIT {int(limit)}"
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()
    return [_row_to_offer(row) for row in rows]


def get_job(job_id: str) -> JobOffer | None:
    """Una oferta por id."""
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return _row_to_offer(row) if row else None


def set_job_status(job_id: str, status: str) -> None:
    """Marca la oferta como evaluated o error."""
    with get_connection() as conn:
        conn.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))


def _row_to_offer(row) -> JobOffer:
    data = dict(row)
    data.pop("status", None)
    data.pop("ingested_at", None)
    if data.get("is_remote") is not None:
        data["is_remote"] = bool(data["is_remote"])
    return JobOffer(**data)


# --------------------------------------------------------------------------- #
# Evaluaciones
# --------------------------------------------------------------------------- #
SAVE_EVALUATION = """
INSERT INTO evaluations (job_id, run_id, score, band, review, strengths_json,
                         gaps_json, deal_breaker, model, prompt_version, tokens)
VALUES (:job_id, :run_id, :score, :band, :review, :strengths_json,
        :gaps_json, :deal_breaker, :model, :prompt_version, :tokens)
ON CONFLICT(job_id, run_id) DO UPDATE SET
    score          = excluded.score,
    band           = excluded.band,
    review         = excluded.review,
    strengths_json = excluded.strengths_json,
    gaps_json      = excluded.gaps_json,
    deal_breaker   = excluded.deal_breaker,
    model          = excluded.model,
    prompt_version = excluded.prompt_version,
    tokens         = excluded.tokens
"""


def save_evaluation(evaluation: Evaluation) -> None:
    """Guarda la evaluacion y marca la oferta como evaluada."""
    params = {
        "job_id": evaluation.job_id,
        "run_id": evaluation.run_id,
        "score": evaluation.score,
        "band": evaluation.band,
        "review": evaluation.review,
        "strengths_json": json.dumps(evaluation.strengths, ensure_ascii=False),
        "gaps_json": json.dumps(evaluation.gaps, ensure_ascii=False),
        "deal_breaker": evaluation.deal_breaker,
        "model": evaluation.model,
        "prompt_version": evaluation.prompt_version,
        "tokens": evaluation.tokens,
    }
    with get_connection() as conn:
        conn.execute(SAVE_EVALUATION, params)
        conn.execute("UPDATE jobs SET status = 'evaluated' WHERE id = ?", (evaluation.job_id,))


def is_evaluated(job_id: str, run_id: str) -> bool:
    """True si esta oferta ya se evaluo en esta corrida."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM evaluations WHERE job_id = ? AND run_id = ?", (job_id, run_id)
        ).fetchone()
    return row is not None


# --------------------------------------------------------------------------- #
# Runs
# --------------------------------------------------------------------------- #
def start_run(run_id: str, profile_hash: str, prompt_version: str) -> None:
    """Abre la corrida."""
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO runs (run_id, started_at, profile_hash, prompt_version)"
            " VALUES (?, ?, ?, ?)",
            (run_id, _now(), profile_hash, prompt_version),
        )


def finish_run(run_id: str, n_jobs: int) -> None:
    """Cierra la corrida."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE runs SET finished_at = ?, n_jobs = ? WHERE run_id = ?",
            (_now(), n_jobs, run_id),
        )


def get_runs() -> list[str]:
    """Run ids de la mas reciente a la mas antigua."""
    with get_connection() as conn:
        rows = conn.execute("SELECT run_id FROM runs ORDER BY started_at DESC").fetchall()
    return [row["run_id"] for row in rows]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# Lectura para la UI
# --------------------------------------------------------------------------- #
EVALUATIONS_DF = """
SELECT e.score, e.band, j.title, j.company, j.location, j.date_posted,
       j.site, j.is_remote, j.job_url, j.min_amount, j.max_amount, j.currency,
       e.review, e.strengths_json, e.gaps_json, e.deal_breaker,
       e.run_id, e.model, e.prompt_version, e.created_at, j.id AS job_id,
       j.description, j.search_query
FROM evaluations e
JOIN jobs j ON j.id = e.job_id
"""


def get_evaluations_df(run_id: str | None = None) -> pd.DataFrame:
    """Jobs + evaluations en un DataFrame plano, listo para la tabla de Streamlit."""
    sql = EVALUATIONS_DF
    params: tuple = ()
    if run_id:
        sql += " WHERE e.run_id = ?"
        params = (run_id,)
    # La fecha manda: lo primero que quiero ver es lo recien publicado.
    sql += " ORDER BY j.date_posted DESC, e.score DESC"

    with get_connection() as conn:
        df = pd.read_sql_query(sql, conn, params=params)

    if df.empty:
        return df

    df["strengths"] = df["strengths_json"].apply(_load_list)
    df["gaps"] = df["gaps_json"].apply(_load_list)
    df = df.drop(columns=["strengths_json", "gaps_json"])
    df["band_label"] = df["band"].map(BAND_LABELS).fillna(df["band"])
    df["is_remote"] = df["is_remote"].astype("boolean")
    df["date_posted"] = pd.to_datetime(df["date_posted"], errors="coerce")
    return df


def _load_list(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return []
