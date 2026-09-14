"""
Busqueda de ofertas de "Data Scientist" en Chile usando JobSpy.
https://github.com/speedyapply/JobSpy

Instalacion:  pip install -U python-jobspy
Uso:          python test.py
"""

import csv

import pandas as pd
from jobspy import scrape_jobs

SEARCH_TERM = "data scientist"
LOCATION = "Santiago, Chile"
RESULTS_WANTED = 30      # por sitio
HOURS_OLD = 24 * 30      # publicados en los ultimos 30 dias
CSV_OUT = "jobs_chile_data_scientist.csv"


def main() -> None:
    jobs = scrape_jobs(
        site_name=["linkedin"],  # Glassdoor no soporta Chile
        search_term=SEARCH_TERM,
        google_search_term=f"ofertas de trabajo {SEARCH_TERM} en Santiago Chile",
        location=LOCATION,
        results_wanted=RESULTS_WANTED,
        hours_old=HOURS_OLD,
        country_indeed="chile",            # requerido por Indeed
        linkedin_fetch_description=False,  # True = mas lento, pero trae descripcion
        verbose=1,
    )

    if jobs is None or jobs.empty:
        print("No se encontraron ofertas. Prueba subiendo HOURS_OLD o cambiando el termino.")
        return

    print(f"\nTotal de ofertas encontradas: {len(jobs)}\n")

    # Resumen por portal
    print("Ofertas por sitio:")
    print(jobs["site"].value_counts().to_string(), "\n")

    # Tabla resumida en consola
    cols = [c for c in ["site", "title", "company", "location", "date_posted", "job_url"]
            if c in jobs.columns]
    pd.set_option("display.max_colwidth", 45)
    pd.set_option("display.width", 200)
    print(jobs[cols].to_string(index=False))

    jobs.to_csv(CSV_OUT, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    print(f"\nGuardado en: {CSV_OUT}")

    print(jobs.columns)
if __name__ == "__main__":
    main()
