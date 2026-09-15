"""Carga el perfil desde data/. Si falta algo, falla explicito: nunca inventa datos."""

from __future__ import annotations

import hashlib
import json

from src.utils.config import CV_PATH, PROFILE_PATH
from src.utils.models import CandidateProfile


def load_profile() -> CandidateProfile:
    """Lee profile.json + cv.md y los une en un CandidateProfile."""
    if not PROFILE_PATH.exists():
        raise FileNotFoundError(
            f"Falta {PROFILE_PATH}. Copia data/profile.example.json a data/profile.json "
            "y reemplaza los valores con tus datos reales."
        )
    if not CV_PATH.exists():
        raise FileNotFoundError(
            f"Falta {CV_PATH}. Copia data/cv.template.md a data/cv.md y escribe tu CV."
        )

    data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    profile = CandidateProfile(**data)
    profile.cv_markdown = CV_PATH.read_text(encoding="utf-8")
    return profile


def profile_hash(profile: CandidateProfile) -> str:
    """Huella del perfil: permite saber si una corrida vieja uso otro perfil."""
    payload = profile.model_dump_json()
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]
