"""Streamlit entrypoint: exploratory dashboard for the UCI Adult (Census Income) dataset.

Run with::

    streamlit run app.py
"""

from pathlib import Path

import streamlit as st

from adult_dashboard import views
from adult_dashboard.data import load_dataset
from adult_dashboard.formatting import format_int

DATA_PATH = Path(__file__).parent / "data" / "adult.csv"

st.set_page_config(page_title="Adult Census Income | Dashboard", page_icon="📊", layout="wide")


@st.cache_data(show_spinner=False)
def load_data():
    """Read and clean the CSV once; Streamlit reruns the script on every interaction."""
    return load_dataset(DATA_PATH)


st.title("Adult Census Income: análise exploratória")
st.write(
    "Dashboard interativo de estatística descritiva sobre o conjunto de dados Adult "
    "(Census Income) do repositório UCI: distribuições, outliers e correlações."
)

try:
    df, report = load_data()
except FileNotFoundError:
    st.error(
        f"Arquivo {DATA_PATH.name} não encontrado em data/. Gere-o com "
        "`python scripts/build_dataset.py --train adult.data --test adult.test` (veja o README)."
    )
    st.stop()

numeric_columns = df.select_dtypes(include="number").columns.tolist()
filtered = views.render_sidebar(df, report)

if filtered.empty:
    st.warning("Nenhum registro corresponde aos filtros selecionados!")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Registros originais", format_int(report.raw_rows))
col2.metric("Variáveis", report.columns)
col3.metric("Valores ausentes tratados", format_int(report.missing_cells))

tab_data, tab_univariate, tab_bivariate, tab_findings = st.tabs(
    ["Dados", "Univariada", "Bivariada", "Achados"]
)
with tab_data:
    views.render_data_tab(df, filtered, report)
with tab_univariate:
    views.render_univariate_tab(filtered, numeric_columns)
with tab_bivariate:
    views.render_bivariate_tab(filtered, numeric_columns)
with tab_findings:
    views.render_findings_tab(filtered)
