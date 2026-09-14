"""UI de revision: tabla filtrable sobre la DB.

Solo lectura: no llama al LLM ni scrapea. El grafo escribe, la UI lee.

    streamlit run streamlit_app.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import BAND_LABELS
from src.db import repository
from src.db.database import init_db

BAND_ORDER = ["optimistic", "neutral", "pessimistic"]
BAND_COLORS = {"optimistic": "#1a7f37", "neutral": "#9a6700", "pessimistic": "#b42318"}

st.set_page_config(page_title="Job Match", layout="wide")


@st.cache_data(ttl=60)
def load_evaluations(run_id: str | None) -> pd.DataFrame:
    """Trae jobs + evaluations. Cacheado para que los filtros sean instantaneos."""
    init_db()
    return repository.get_evaluations_df(run_id)


@st.cache_data(ttl=60)
def load_runs() -> list[str]:
    init_db()
    return repository.get_runs()


def main() -> None:
    st.title("Job Match — ofertas evaluadas")

    runs = load_runs()
    if not runs:
        st.info(
            "Todavia no hay corridas. Corre primero:\n\n"
            "```\npython main.py ingest --from-csv\npython main.py evaluate\n```"
        )
        return

    # ---------------------------------------------------------------- sidebar
    with st.sidebar:
        st.header("Filtros")
        run_id = st.selectbox("Corrida", runs, index=0)
        if st.button("Recargar datos", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    df = load_evaluations(run_id)
    if df.empty:
        st.warning("Esta corrida no tiene evaluaciones.")
        return

    with st.sidebar:
        score_min, score_max = st.slider("Score", 1, 10, (1, 10))
        bands = st.multiselect(
            "Banda",
            options=[b for b in BAND_ORDER if b in set(df["band"])],
            default=[b for b in BAND_ORDER if b in set(df["band"])],
            format_func=lambda b: BAND_LABELS.get(b, b),
        )
        sites = st.multiselect("Portal", sorted(df["site"].dropna().unique()))
        title_query = st.text_input("Titulo contiene")
        company_query = st.text_input("Empresa contiene")
        remote_only = st.checkbox("Solo remotas")
        hide_discarded = st.checkbox("Ocultar descartadas (deal breaker)")

        fechas = df["date_posted"].dropna()
        date_range = None
        if not fechas.empty:
            date_range = st.date_input(
                "Publicada entre",
                value=(fechas.min().date(), fechas.max().date()),
                min_value=fechas.min().date(),
                max_value=fechas.max().date(),
            )

    view = apply_filters(
        df, score_min, score_max, bands, sites, title_query,
        company_query, remote_only, hide_discarded, date_range,
    )

    # --------------------------------------------------------------- metricas
    show_metrics(df, view)
    st.divider()

    # ----------------------------------------------------------------- tabla
    st.subheader(f"{len(view)} ofertas · de la mas reciente a la mas antigua")
    if view.empty:
        st.warning("Ningun resultado con estos filtros.")
        return

    hoy = pd.Timestamp.now().normalize()
    table = view.assign(
        publicada=view["date_posted"].dt.date,
        dias=(hoy - view["date_posted"]).dt.days,
        banda=view["band"].map(BAND_LABELS),
        gaps_texto=view["gaps"].apply(lambda g: " · ".join(g) if g else "—"),
    )[
        ["publicada", "dias", "score", "banda", "title", "company",
         "gaps_texto", "review", "site", "job_url"]
    ]

    selection = st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        row_height=110,  # el comentario del LLM necesita varias lineas
        column_config={
            "publicada": st.column_config.DateColumn("Publicada", format="DD MMM", width="small"),
            "dias": st.column_config.NumberColumn("Dias", format="%d d", width="small"),
            "score": st.column_config.NumberColumn("Score", format="%d", width="small"),
            "banda": st.column_config.TextColumn("Banda", width="small"),
            "title": st.column_config.TextColumn("Cargo", width="medium"),
            "company": st.column_config.TextColumn("Empresa", width="small"),
            "gaps_texto": st.column_config.TextColumn("Gaps", width="large"),
            "review": st.column_config.TextColumn("Por que ese score", width="large"),
            "site": st.column_config.TextColumn("Portal", width="small"),
            "job_url": st.column_config.LinkColumn("Link", display_text="abrir", width="small"),
        },
    )

    rows = selection.selection["rows"] if selection and selection.selection else []
    if rows:
        show_detail(view.iloc[rows[0]])
    else:
        st.caption("Selecciona una fila para ver el comentario completo.")


def apply_filters(df, score_min, score_max, bands, sites, title_query,
                  company_query, remote_only, hide_discarded, date_range):
    """Filtra en memoria: la query a la DB es una sola."""
    view = df[df["score"].between(score_min, score_max)]
    if bands:
        view = view[view["band"].isin(bands)]
    if sites:
        view = view[view["site"].isin(sites)]
    if title_query:
        view = view[view["title"].str.contains(title_query, case=False, na=False)]
    if company_query:
        view = view[view["company"].str.contains(company_query, case=False, na=False)]
    if remote_only:
        view = view[view["is_remote"] == True]  # noqa: E712 - columna boolean de pandas
    if hide_discarded:
        view = view[view["deal_breaker"].isna() | (view["deal_breaker"] == "")]
    if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = (pd.Timestamp(d) for d in date_range)
        view = view[view["date_posted"].between(start, end + pd.Timedelta(days=1))]
    return view


def show_metrics(df: pd.DataFrame, view: pd.DataFrame) -> None:
    """Metricas de la corrida completa, no del filtro: sirven para calibrar el prompt."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Evaluadas", len(df))
    optimistas = int((df["band"] == "optimistic").sum())
    col2.metric("Optimistas", optimistas, help="Un 9-10 es 'postularia esta semana'")
    col3.metric("Score promedio", f"{df['score'].mean():.1f}")
    col4.metric("En pantalla", len(view))

    share = optimistas / len(df) if len(df) else 0
    if share > 1 / 3:
        st.warning(
            f"{share:.0%} de las ofertas salio optimista. El prompt esta blando: "
            "aprieta la rubrica en src/prompts.py y sube PROMPT_VERSION."
        )




def show_detail(row: pd.Series) -> None:
    """Detalle de la oferta seleccionada."""
    st.divider()
    color = BAND_COLORS.get(row["band"], "#333")
    st.markdown(
        f"### {row['title']}\n"
        f"**{row['company'] or 'sin empresa'}** · {row['location'] or 'sin ubicacion'} · "
        f"<span style='color:{color}'><b>{row['score']}/10 — "
        f"{BAND_LABELS.get(row['band'], row['band'])}</b></span>",
        unsafe_allow_html=True,
    )

    if row["deal_breaker"]:
        st.error(f"Deal breaker: {row['deal_breaker']}")

    st.markdown("**Por que ese score**")
    st.write(row["review"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**A favor**")
        for item in row["strengths"] or ["—"]:
            st.markdown(f"- {item}")
    with col2:
        st.markdown("**Gaps**")
        for item in row["gaps"] or ["—"]:
            st.markdown(f"- {item}")

    st.link_button("Ver oferta en el portal", row["job_url"])

    with st.expander("Descripcion original de la oferta"):
        st.text(row["description"] or "La oferta no incluye descripcion.")

    st.caption(
        f"run: {row['run_id']} · modelo: {row['model']} · prompt: {row['prompt_version']}"
    )


main()
