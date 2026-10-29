"""Smoke tests: run the real Streamlit script headlessly and interact with its widgets."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parents[1] / "app.py")
NUMERIC = ["age", "fnlwgt", "education-num", "capital-gain", "capital-loss", "hours-per-week"]


@pytest.fixture
def app():
    return AppTest.from_file(APP_PATH, default_timeout=120).run()


def test_app_starts_without_errors(app):
    assert not app.exception
    assert len(app.tabs) == 4


@pytest.mark.parametrize("variable", NUMERIC)
def test_every_numeric_variable_renders(app, variable):
    app.selectbox(key="univariate_variable").select(variable).run()
    assert not app.exception


def test_univariate_metrics_match_pandas(app, df):
    app.selectbox(key="univariate_variable").select("age").run()
    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Média"] == "38,65"
    assert metrics["Mediana"] == "37,00"
    assert metrics["Total de outliers"] == "215"


def test_iqr_zero_shows_warning_message(app):
    app.selectbox(key="univariate_variable").select("capital-gain").run()
    assert any("IQR = 0" in info.value for info in app.info)


def test_bivariate_correlation_values(app):
    app.selectbox(key="bivariate_x").select("education-num").run()
    app.selectbox(key="bivariate_y").select("hours-per-week").run()
    app.checkbox(key="color_by_income").check().run()
    metrics = {m.label: m.value for m in app.metric}
    assert not app.exception
    assert metrics["r de Pearson"] == "0,144"
    assert metrics["ρ de Spearman"] == "0,165"
    assert metrics["Classificação (|r|)"] == "fraca/nula"


def test_same_variable_on_both_axes_is_handled(app):
    app.selectbox(key="bivariate_y").select("age").run()
    assert not app.exception
    assert any("diferentes" in info.value for info in app.info)


def test_spearman_matrix_option(app):
    app.radio(key="corr_method").set_value("spearman").run()
    assert not app.exception


def test_income_filter_updates_counter(app):
    app.multiselect(key="income_filter").set_value([">50K"]).run()
    assert not app.exception
    assert any("11.681 de 48.790" in md.value for md in app.sidebar.markdown)


def test_empty_filter_shows_warning_instead_of_failing(app):
    app.multiselect(key="income_filter").set_value([]).run()
    assert not app.exception
    assert any("Nenhum registro" in w.value for w in app.warning)


def test_constant_variable_is_reported(app):
    app.slider(key="age_filter").set_range(90, 90).run()
    assert not app.exception
    assert any("constante" in info.value for info in app.info)
