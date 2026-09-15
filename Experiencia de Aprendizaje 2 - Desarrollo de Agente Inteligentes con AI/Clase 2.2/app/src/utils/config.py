"""Configuracion central: rutas, settings del .env y las bandas de score."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parent.parent.parent  # src/utils/config.py -> app/
DATA_DIR = APP_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
DB_DIR = APP_DIR / "db"
SCHEMA_PATH = DB_DIR / "schema.sql"

CV_PATH = DATA_DIR / "cv.md"
PROFILE_PATH = DATA_DIR / "profile.json"

# Sube cuando cambie EVALUATOR_SYSTEM_PROMPT: permite comparar corridas.
PROMPT_VERSION = "v7"

# Cuanto de la descripcion de la oferta entra al prompt.
MAX_DESC_CHARS = 6000

# Bandas del score. El codigo las deriva, nunca el LLM.
SCORE_BANDS = (
    (1, 6, "pessimistic"),
    (7, 8, "neutral"),
    (9, 10, "optimistic"),
)

BAND_LABELS = {
    "pessimistic": "pesimista",
    "neutral": "neutral",
    "optimistic": "optimista",
}


class Settings(BaseSettings):
    """Settings leidos desde app/.env."""

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    db_path: Path = DB_DIR / "jobs.db"

    model_config = SettingsConfigDict(
        env_file=APP_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


def band_for(score: int) -> str:
    """Devuelve la banda que corresponde a un score de 1 a 10."""
    for low, high, band in SCORE_BANDS:
        if low <= score <= high:
            return band
    raise ValueError(f"Score fuera de rango 1-10: {score}")
