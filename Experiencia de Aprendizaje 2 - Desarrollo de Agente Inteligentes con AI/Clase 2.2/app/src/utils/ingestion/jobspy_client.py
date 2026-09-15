"""Cliente de JobSpy. Esta capa no sabe nada del LLM."""

from __future__ import annotations

import pandas as pd
from jobspy import scrape_jobs

# Glassdoor no soporta Chile y Google suele devolver 0 resultados.
DEFAULT_SITES = ["indeed", "linkedin"]


def fetch_jobs(
    query: str,
    location: str = "Santiago, Chile",
    results_wanted: int = 30,
    hours_old: int = 24 * 30,
    sites: list[str] | None = None,
) -> pd.DataFrame:
    """Busca ofertas en los portales y devuelve el DataFrame crudo de JobSpy."""
    return scrape_jobs(
        site_name=sites or DEFAULT_SITES,
        search_term=query,
        location=location,
        results_wanted=results_wanted,
        hours_old=hours_old,
        country_indeed="chile",
        linkedin_fetch_description=True,
        verbose=1,
    )
