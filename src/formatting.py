from __future__ import annotations

import math


def number(value: float | int | None, decimals: int = 2) -> str:
    if value is None:
        return "—"
    try:
        if math.isnan(float(value)):
            return "—"
    except (TypeError, ValueError):
        return str(value)
    return f"{float(value):,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def volume(value: float | int | None) -> str:
    if value is None:
        return "—"
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f} millones m³".replace(".", ",")
    return f"{value:,.0f} m³".replace(",", ".")


def metric_card(label: str, value: str, note: str = "") -> str:
    note_html = f'<div class="metric-note">{note}</div>' if note else ""
    return (
        '<div class="custom-metric">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'{note_html}'
        '</div>'
    )
