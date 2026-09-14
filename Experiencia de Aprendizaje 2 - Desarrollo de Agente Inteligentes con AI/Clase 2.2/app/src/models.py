"""Contratos de datos del proyecto. Todo lo que cruza una capa pasa por aca."""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, Field

from src.config import MAX_DESC_CHARS

EducationLevel = Literal["technical", "bachelor", "master", "phd"]
WorkMode = Literal["remote", "hybrid", "onsite"]
Band = Literal["pessimistic", "neutral", "optimistic"]


# --------------------------------------------------------------------------- #
# Oferta
# --------------------------------------------------------------------------- #
class JobOffer(BaseModel):
    """Una oferta normalizada, venga de la API de JobSpy o de un CSV."""

    id: str
    site: str | None = None
    title: str
    company: str | None = None
    location: str | None = None
    date_posted: str | None = None
    job_url: str
    description: str | None = None
    is_remote: bool | None = None
    min_amount: float | None = None
    max_amount: float | None = None
    currency: str | None = None
    raw_json: str | None = None

    def salary_text(self) -> str:
        """Sueldo legible, o el aviso de que la oferta no lo informa."""
        if self.min_amount is None and self.max_amount is None:
            return "no informa sueldo"
        cur = self.currency or ""
        low = f"{self.min_amount:,.0f}" if self.min_amount is not None else "?"
        high = f"{self.max_amount:,.0f}" if self.max_amount is not None else "?"
        return f"{low} - {high} {cur}".strip()

    def to_prompt_block(self) -> str:
        """Bloque de texto de la oferta que entra al prompt."""
        desc = (self.description or "").strip()
        if len(desc) > MAX_DESC_CHARS:
            desc = desc[:MAX_DESC_CHARS] + "\n[...descripcion truncada...]"
        remote = {
            True: "el portal la marca como remota",
            False: "el portal NO la marca como remota; puede ser presencial o hibrida, "
                   "el aviso no lo precisa",
            None: "no informa",
        }[self.is_remote]
        return (
            f"Titulo: {self.title}\n"
            f"Empresa: {self.company or 'no informa'}\n"
            f"Ubicacion: {self.location or 'no informa'}\n"
            f"Modalidad: {remote}\n"
            f"Sueldo: {self.salary_text()}\n"
            f"Publicada: {self.date_posted or 'no informa'}\n"
            f"Portal: {self.site or 'no informa'}\n\n"
            f"Descripcion:\n{desc or 'La oferta no incluye descripcion.'}"
        )


# --------------------------------------------------------------------------- #
# Perfil
# --------------------------------------------------------------------------- #
class Experience(BaseModel):
    total_years: float = 0
    years_by_area: dict[str, float] = Field(default_factory=dict)
    years_by_skill: dict[str, float] = Field(default_factory=dict)


class Leadership(BaseModel):
    has_led: bool = False
    max_team_size: int = 0
    years_leading: float = 0


class Education(BaseModel):
    max_level: EducationLevel = "bachelor"
    degrees: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


class Preferences(BaseModel):
    work_mode: list[WorkMode] = Field(default_factory=list)
    location: str | None = None
    min_salary_clp_monthly: int | None = None
    deal_breakers: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    """profile.json + cv.md juntos. Los dos van completos al prompt."""

    name: str
    current_title: str | None = None
    experience: Experience = Field(default_factory=Experience)
    industries: list[str] = Field(default_factory=list)
    leadership: Leadership = Field(default_factory=Leadership)
    education: Education = Field(default_factory=Education)
    languages: dict[str, str] = Field(default_factory=dict)
    preferences: Preferences = Field(default_factory=Preferences)

    # No viene del JSON: lo inyecta el loader desde data/cv.md.
    cv_markdown: str = ""

    def hard_data_json(self) -> str:
        """Los datos duros serializados, sin el CV."""
        return json.dumps(
            self.model_dump(exclude={"cv_markdown"}),
            ensure_ascii=False,
            indent=2,
        )

    def to_prompt_block(self) -> str:
        """Bloque de perfil que entra al prompt: datos duros + CV completo."""
        return (
            "=== DATOS DUROS (profile.json) ===\n"
            f"{self.hard_data_json()}\n\n"
            "=== CV (cv.md) ===\n"
            f"{self.cv_markdown.strip() or 'Sin CV cargado.'}"
        )


# --------------------------------------------------------------------------- #
# Evaluacion
# --------------------------------------------------------------------------- #
class Evaluation(BaseModel):
    """La evaluacion completa que se guarda en la DB."""

    job_id: str
    run_id: str
    score: int = Field(ge=1, le=10)
    band: Band
    review: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    deal_breaker: str | None = None
    model: str | None = None
    prompt_version: str | None = None
    tokens: int | None = None
