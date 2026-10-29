"""Matplotlib figures used by the dashboard (no pyplot state, safe for web servers)."""

from __future__ import annotations

import pandas as pd
from matplotlib.figure import Figure


def histogram(series: pd.Series, bins: int) -> Figure:
    fig = Figure(figsize=(6, 4))
    ax = fig.subplots()
    ax.hist(series, bins=bins, edgecolor="white")
    ax.set_xlabel(str(series.name))
    ax.set_ylabel("Frequência")
    return fig


def boxplot(series: pd.Series) -> Figure:
    fig = Figure(figsize=(6, 4))
    ax = fig.subplots()
    ax.boxplot(series)
    ax.set_ylabel(str(series.name))
    ax.set_xticks([])
    return fig


def scatter(df: pd.DataFrame, x: str, y: str, color_by: str | None = None) -> Figure:
    fig = Figure(figsize=(10, 4))
    ax = fig.subplots()
    if color_by:
        for label, group in df.groupby(color_by, observed=True):
            ax.scatter(group[x], group[y], label=label, alpha=0.4)
        ax.legend(title=color_by)
    else:
        ax.scatter(df[x], df[y], alpha=0.4)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    return fig
