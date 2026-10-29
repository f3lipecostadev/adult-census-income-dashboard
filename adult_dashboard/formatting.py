"""Number formatting helpers (Brazilian Portuguese conventions)."""

from __future__ import annotations

import pandas as pd


def format_br(value: float, decimals: int = 2) -> str:
    """Format a number as ``1.234,56``. Missing values are shown as an em dash."""
    if pd.isna(value):
        return "—"
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def format_int(value: float) -> str:
    """Format an integer with thousands separators: ``48.842``."""
    return format_br(value, 0)
