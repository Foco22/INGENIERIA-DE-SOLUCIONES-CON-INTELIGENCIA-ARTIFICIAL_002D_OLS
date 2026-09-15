"""El modelo. Un solo lugar donde se configura."""

from __future__ import annotations

from functools import lru_cache

from langchain_openai import ChatOpenAI

from src.utils.config import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """El modelo, configurado desde .env. temperature=0 para que el ranking sea comparable."""
    if not settings.openai_api_key:
        raise RuntimeError("Falta OPENAI_API_KEY en app/.env")
    return ChatOpenAI(
        model=settings.openai_model,
        temperature=0,
        api_key=settings.openai_api_key,
    )
