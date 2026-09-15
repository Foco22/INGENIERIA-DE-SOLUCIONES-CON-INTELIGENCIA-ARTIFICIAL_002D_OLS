"""CLI del Job Match Agent: ingest | evaluate.

El ranking se revisa en la UI:  streamlit run streamlit_app.py
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.utils.config import BAND_LABELS, RAW_DIR
from src.utils.db import repository
from src.utils.db.database import init_db
from src.agents.agent import evaluate_offers, new_run_id
from src.utils.ingestion.loader import ingest_from_csv, ingest_from_searches
from src.utils.profile.loader import load_profile


def cmd_ingest(args: argparse.Namespace) -> int:
    """Busca ofertas (o carga un CSV) y las guarda en la DB."""
    if args.from_csv:
        path = Path(args.from_csv)
        if not path.is_absolute():
            path = Path.cwd() / path
        n = ingest_from_csv(path)
        print(f"Ingestadas {n} ofertas desde {path.name}")
    else:
        por_busqueda = ingest_from_searches(
            queries=args.query,
            location=args.location,
            results_wanted=args.results,
            hours_old=args.hours_old,
        )
        for query, n in por_busqueda.items():
            print(f"  '{query}': {n} ofertas")
        print(f"Total ingestado: {sum(por_busqueda.values())} en {args.location}")

    pending = len(repository.get_pending_jobs())
    print(f"Pendientes de evaluar: {pending}")
    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    """Corre el grafo sobre las ofertas pendientes."""
    init_db()
    jobs = repository.get_pending_jobs(limit=args.limit)
    if not jobs:
        print("No hay ofertas pendientes. Corre primero:  python main.py ingest ...")
        return 0

    profile = load_profile()
    run_id = args.run_id or new_run_id()
    print(f"Evaluando {len(jobs)} ofertas para {profile.name} | run_id={run_id}")

    evaluations, errors = evaluate_offers(jobs, profile, run_id=run_id)

    print(f"\nListo: {len(evaluations)} evaluadas, {len(errors)} con error.")
    if evaluations:
        counts: dict[str, int] = {}
        for ev in evaluations:
            counts[ev.band] = counts.get(ev.band, 0) + 1
        resumen = ", ".join(f"{BAND_LABELS[b]}: {n}" for b, n in counts.items())
        print(f"Distribucion -> {resumen}")
    for err in errors:
        print(f"  error: {err}")

    print("\nRevisa el ranking con:  streamlit run streamlit_app.py")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Job Match Agent")
    parser.add_argument("-v", "--verbose", action="store_true", help="logs del pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="scrapear ofertas o cargar un CSV")
    ingest.add_argument(
        "--query",
        nargs="+",
        default=["data scientist"],
        metavar="TERMINO",
        help='uno o varios terminos: --query "data scientist" "AI engineer"',
    )
    ingest.add_argument("--location", default="Santiago, Chile")
    ingest.add_argument("--results", type=int, default=30, help="resultados por portal")
    ingest.add_argument("--hours-old", type=int, default=24 * 30)
    ingest.add_argument(
        "--from-csv",
        nargs="?",
        const=str(RAW_DIR / "jobs_chile_data_scientist.csv"),
        help="CSV de JobSpy ya descargado",
    )
    ingest.set_defaults(func=cmd_ingest)

    evaluate = sub.add_parser("evaluate", help="evaluar las ofertas pendientes")
    evaluate.add_argument("--limit", type=int, default=None, help="cuantas ofertas evaluar")
    evaluate.add_argument("--run-id", default=None, help="reusar un run_id existente")
    evaluate.set_defaults(func=cmd_evaluate)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(message)s",
    )
    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(f"\n{exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"\n{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
