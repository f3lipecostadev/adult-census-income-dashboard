"""Data dictionary of the Adult dataset (meaning, unit and type of each column)."""

from __future__ import annotations

import pandas as pd

# (column, meaning, unit, kind)
DATA_DICTIONARY: list[tuple[str, str, str, str]] = [
    ("age", "Idade da pessoa", "anos", "numérico (int)"),
    ("workclass", "Tipo de vínculo de trabalho (privado, governo, autônomo...)", "-", "categórico"),
    (
        "fnlwgt",
        "Peso amostral do censo (nº de pessoas que o registro representa)",
        "pessoas",
        "numérico (int)",
    ),
    ("education", "Maior nível de escolaridade", "-", "categórico"),
    ("education-num", "Escolaridade em formato numérico (1 a 16)", "nível", "numérico (int)"),
    ("marital-status", "Estado civil", "-", "categórico"),
    ("occupation", "Ocupação / profissão", "-", "categórico"),
    ("relationship", "Papel na família (marido, esposa, filho...)", "-", "categórico"),
    ("race", "Raça declarada", "-", "categórico"),
    ("sex", "Sexo", "-", "categórico"),
    ("capital-gain", "Ganho de capital (investimentos, vendas de bens)", "US$", "numérico (int)"),
    ("capital-loss", "Perda de capital", "US$", "numérico (int)"),
    ("hours-per-week", "Horas trabalhadas por semana", "horas/semana", "numérico (int)"),
    ("native-country", "País de origem", "-", "categórico"),
    ("income", "Faixa de renda anual (<=50K ou >50K)", "US$/ano", "categórico"),
]


def build_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    """Return the dictionary as a table, adding the dtype pandas inferred for each column."""
    table = pd.DataFrame(DATA_DICTIONARY, columns=["Coluna", "Significado", "Unidade", "Tipo"])
    table["Tipo no pandas"] = table["Coluna"].map(df.dtypes.astype(str))
    return table
