"""Streamlit views: sidebar and one render function per tab."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from . import plots
from .data import QualityReport
from .dictionary import build_dictionary
from .findings import FINDINGS_MD
from .formatting import format_br, format_int
from .stats import correlation_strength, find_outliers, skew_direction, tukey_limits

STRENGTH_PT = {"strong": "forte", "moderate": "moderada", "weak": "fraca/nula"}
SCATTER_SAMPLE_SIZE = 2000


def render_sidebar(df: pd.DataFrame, report: QualityReport) -> pd.DataFrame:
    """Draw the sidebar (project info and filters) and return the filtered DataFrame."""
    with st.sidebar:
        st.header("Sobre o projeto")
        st.markdown(
            "**Conjunto de dados:** Adult (Census Income)  \n"
            "**Fonte:** [UCI Machine Learning Repository]"
            "(https://archive.ics.uci.edu/dataset/2/adult)  \n"
            f"**Registros originais:** {format_int(report.raw_rows)}  \n"
            f"**Variáveis:** {report.columns}  \n"
            "**Autor:** Felipe Kauã de Sousa Costa"
        )
        st.caption(
            "Objetivo: analisar o perfil de adultos (idade, escolaridade, horas trabalhadas, "
            "ganhos) e sua relação com a faixa de renda. Referência: Becker e Kohavi (1996)."
        )
        st.divider()

        st.header("Filtros")
        incomes = sorted(df["income"].unique().tolist())
        selected_incomes = st.multiselect(
            "Faixa de renda:", options=incomes, default=incomes, key="income_filter"
        )
        age_min, age_max = int(df["age"].min()), int(df["age"].max())
        selected_ages = st.slider(
            "Faixa etária:", age_min, age_max, (age_min, age_max), key="age_filter"
        )

        filtered = df[df["income"].isin(selected_incomes) & df["age"].between(*selected_ages)]
        share = 100 * len(filtered) / len(df)
        st.write(
            f"Exibindo {format_int(len(filtered))} de {format_int(len(df))} "
            f"registros ({format_br(share, 1)}%)"
        )
    return filtered


def render_data_tab(df: pd.DataFrame, filtered: pd.DataFrame, report: QualityReport) -> None:
    st.header("Dados e qualidade")

    st.subheader("Dicionário de dados")
    st.dataframe(build_dictionary(df), hide_index=True, height=565)
    st.caption(
        "Atenção: fnlwgt é um peso estatístico do censo, não uma característica da pessoa. "
        "education-num é ordinal (níveis de 1 a 16)."
    )

    st.subheader("Relatório de qualidade")
    col1, col2, col3 = st.columns(3)
    col1.metric("Valores ausentes tratados", format_int(report.missing_cells))
    col2.metric("Linhas duplicadas removidas", format_int(report.duplicate_rows))
    col3.metric("Linhas após a limpeza", format_int(report.clean_rows))
    st.caption(
        "Tratamento: linhas duplicadas removidas; valores ausentes de workclass, occupation e "
        "native-country (colunas de texto) preenchidos com 'Desconhecido', para não inventar "
        "uma categoria e preservar as linhas (cerca de 7% da base tem algum ausente). "
        "As colunas de texto foram convertidas para o tipo category."
    )

    st.subheader("Amostra dos dados")
    st.write(f"Registros nos filtros atuais: {format_int(len(filtered))}")
    n_rows = st.slider("Quantas linhas exibir?", 3, 50, 10, key="sample_rows")
    st.dataframe(filtered.head(n_rows))


def render_univariate_tab(filtered: pd.DataFrame, numeric_columns: list[str]) -> None:
    st.header("Análise univariada")
    variable = st.selectbox("Variável:", numeric_columns, key="univariate_variable")
    series = filtered[variable]

    if len(series) < 3 or series.nunique() < 2:
        st.info("Dados insuficientes ou variável constante nos filtros atuais. Amplie os filtros.")
        return

    mean, median, std = series.mean(), series.median(), series.std()
    limits = tukey_limits(series)
    g1 = series.skew()  # Fisher-Pearson skewness coefficient (sample-adjusted)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Média", format_br(mean))
    col2.metric("Mediana", format_br(median))
    col3.metric("Desvio padrão", format_br(std))
    col4.metric("IQR (Q3 − Q1)", format_br(limits.iqr))

    st.subheader("Resumo estatístico (describe)")
    st.dataframe(series.describe().to_frame().T)

    st.subheader("Diagnóstico de assimetria")
    st.write(f"Coeficiente de assimetria (g1): **{format_br(g1)}**")
    direction = skew_direction(g1)
    if direction == "symmetric":
        st.success(
            f"Distribuição aproximadamente simétrica (|g1| ≤ 0,5): média ({format_br(mean)}) "
            f"≈ mediana ({format_br(median)}). A **média** é adequada como medida central."
        )
    elif direction == "positive":
        st.warning(
            f"Assimetria positiva (cauda à direita, g1 > 0,5): média ({format_br(mean)}) "
            f"> mediana ({format_br(median)}). Valores altos puxam a média para cima, então a "
            "**mediana** é a medida central mais recomendada."
        )
    else:
        st.warning(
            f"Assimetria negativa (cauda à esquerda, g1 < −0,5): média ({format_br(mean)}) "
            f"< mediana ({format_br(median)}). Valores baixos puxam a média para baixo, então a "
            "**mediana** é a medida central mais recomendada."
        )
    st.caption(
        "A assimetria indica cauda longa, mas sozinha não prova que existam outliers: "
        "confira o boxplot e os limites de Tukey abaixo."
    )

    col_hist, col_box = st.columns(2)
    with col_hist:
        st.subheader("Histograma")
        bins = st.slider("Número de faixas (bins):", 5, 100, 20, key="histogram_bins")
        st.pyplot(plots.histogram(series, bins))
    with col_box:
        st.subheader("Boxplot")
        st.pyplot(plots.boxplot(series))

    st.subheader("Outliers (critério de Tukey: 1,5 × IQR)")
    outliers = find_outliers(series, limits)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Limite inferior (Q1 − 1,5·IQR)", format_br(limits.lower))
    col2.metric("Limite superior (Q3 + 1,5·IQR)", format_br(limits.upper))
    col3.metric("Total de outliers", format_int(len(outliers)))
    col4.metric("% de outliers", f"{format_br(100 * len(outliers) / len(series), 1)}%")

    if limits.iqr == 0:
        st.info(
            "IQR = 0: mais da metade dos valores é igual, então qualquer valor diferente "
            "é marcado como outlier. Nesse caso o critério de Tukey não é adequado."
        )
    st.caption(
        "Limitações: o critério de Tukey assume uma distribuição aproximadamente simétrica; "
        "em variáveis assimétricas ou muito concentradas ele marca muitos falsos positivos. "
        "Um outlier não é necessariamente um erro: pode ser um valor legítimo e raro."
    )


def render_bivariate_tab(filtered: pd.DataFrame, numeric_columns: list[str]) -> None:
    st.header("Análise bivariada")

    col_x, col_y = st.columns(2)
    x = col_x.selectbox("Eixo X:", numeric_columns, index=0, key="bivariate_x")
    y = col_y.selectbox(
        "Eixo Y:", numeric_columns, index=len(numeric_columns) - 1, key="bivariate_y"
    )
    color_by_income = st.checkbox(
        "Colorir os pontos pela faixa de renda (income)", key="color_by_income"
    )

    sample = filtered.sample(min(SCATTER_SAMPLE_SIZE, len(filtered)), random_state=1)
    st.caption(
        f"O gráfico mostra uma amostra de {format_int(len(sample))} pontos; "
        "os coeficientes usam todos os dados filtrados."
    )
    st.pyplot(plots.scatter(sample, x, y, "income" if color_by_income else None))

    if x == y:
        st.info("Escolha variáveis diferentes para X e Y.")
    elif len(filtered) < 3 or filtered[x].nunique() < 2 or filtered[y].nunique() < 2:
        st.info(
            "Não é possível calcular a correlação: há poucos registros ou uma das "
            "variáveis é constante."
        )
    else:
        r = filtered[x].corr(filtered[y])
        rho = filtered[x].corr(filtered[y], method="spearman")
        strength = STRENGTH_PT[correlation_strength(r)]
        direction = "positiva" if r > 0 else "negativa"

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("r de Pearson", format_br(r, 3))
        col2.metric("Classificação (|r|)", strength)
        col3.metric("r² (variação compartilhada)", f"{format_br(100 * r**2, 1)}%")
        col4.metric("ρ de Spearman", format_br(rho, 3))
        st.write(
            f"**Interpretação:** r = {format_br(r, 3)} indica uma correlação linear "
            f"**{strength} e {direction}** entre *{x}* e *{y}*. Apenas "
            f"{format_br(100 * r**2, 1)}% da variação de uma variável é compartilhada com a outra."
        )
        st.caption(
            "Pearson mede a associação linear e é sensível a outliers. Spearman usa postos "
            "(ordens), mede associação monotônica e é mais robusto: com dados assimétricos ou "
            "com outliers, dê mais atenção a ele. Ambos variam de −1 a +1."
        )

    st.warning(
        "⚠️ Correlação não implica causalidade! Um r alto só indica que as variáveis variam "
        "juntas, não que uma causa a outra (pode haver variáveis de confusão)."
    )

    st.subheader("Matriz de correlação das variáveis numéricas")
    method = st.radio("Método:", ["pearson", "spearman"], horizontal=True, key="corr_method")
    matrix = filtered[numeric_columns].corr(method=method)
    st.dataframe(
        matrix.style.format("{:.2f}").background_gradient(cmap="coolwarm", vmin=-1, vmax=1)
    )


def render_findings_tab(filtered: pd.DataFrame) -> None:
    st.header("Principais achados")
    st.caption(
        "Texto escrito sobre a base completa (48.790 registros após a limpeza, sem filtros). "
        "A tabela ao final usa os filtros atuais."
    )
    st.markdown(FINDINGS_MD)

    st.subheader("Perfil por faixa de renda nos dados filtrados (mediana)")
    grouped = filtered.groupby("income", observed=True)
    profile = grouped[["age", "education-num", "hours-per-week"]].median()
    profile.insert(0, "registros", grouped.size())
    st.dataframe(profile)
