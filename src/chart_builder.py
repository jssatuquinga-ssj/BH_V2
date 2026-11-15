"""Gráficos del visor con un estilo único y profesional.

Reglas de estilo (iguales en todos los gráficos):
- Tipografía Inter, textos en tinta neutra (nunca del color de la serie).
- Paleta categórica validada para daltonismo, asignada en orden fijo.
  Cada subcuenca conserva siempre el mismo color en todo el visor.
- Líneas de 2 px, barras con extremo redondeado, cuadrícula tenue.
- Leyenda solo cuando hay dos o más series; tooltip con unidades.
"""
from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
import plotly.graph_objects as go

from src.labels import decimals, label, subbasin_id

FONT_FAMILY = "Inter, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"

INK = "#0b2a36"          # títulos y valores
INK_SECONDARY = "#4a6570"  # ejes y leyendas
INK_MUTED = "#7b9199"
GRID = "#e3eaed"
AXIS = "#c9d5da"
SURFACE = "#ffffff"

# Paleta categórica validada (orden fijo; no se repite ni se genera).
CATEGORICAL = [
    "#2a78d6",  # 1 azul
    "#eb6834",  # 2 naranja
    "#1baf7a",  # 3 aqua
    "#eda100",  # 4 amarillo
    "#e87ba4",  # 5 magenta
    "#008300",  # 6 verde
    "#6250d6",  # 7 violeta
    "#e34948",  # 8 rojo
]
PRIMARY = CATEGORICAL[0]
OBSERVED = "#3d4f56"  # serie observada: tinta neutra oscura frente al simulado en azul

# Rampa secuencial azul (claro → oscuro) para magnitudes en mapas.
SEQUENTIAL_BLUE = [
    "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281", "#0d366b",
]


def subbasin_color(sid: int) -> str:
    """Color fijo de cada subcuenca (1 a 8)."""
    return CATEGORICAL[(int(sid) - 1) % len(CATEGORICAL)]


def _d3_format(places: int, thousands: bool = True) -> str:
    return f"{',' if thousands else ''}.{places}f"


def _is_elevation(column: str) -> bool:
    """Las cotas (m s. n. m.) se muestran sin separador de miles: 3887.96."""
    return "cota" in column.lower()


def style_figure(
    figure: go.Figure,
    title: str | None = None,
    y_title: str | None = None,
    x_title: str | None = None,
    height: int = 400,
    show_legend: bool | None = None,
) -> go.Figure:
    """Aplica el estilo común a cualquier figura de Plotly."""
    figure.update_layout(
        title={
            "text": f"<b>{title}</b>" if title else None,
            "x": 0.0,
            "xref": "container",
            "xanchor": "left",
            "pad": {"l": 16},
            "y": 0.97,
            "font": {"size": 16, "color": INK, "family": FONT_FAMILY},
        },
        font={"family": FONT_FAMILY, "size": 12.5, "color": INK_SECONDARY},
        height=height,
        margin={"l": 16, "r": 20, "t": 56 if title else 24, "b": 12},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=SURFACE,
        hovermode="x unified",
        hoverlabel={
            "bgcolor": "#ffffff",
            "bordercolor": AXIS,
            "font": {"family": FONT_FAMILY, "size": 12.5, "color": INK},
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.0,
            "xanchor": "left",
            "x": 0.0,
            "title_text": "",
            "font": {"size": 12, "color": INK_SECONDARY},
            "bgcolor": "rgba(0,0,0,0)",
        },
        separators=".,",
    )
    if show_legend is not None:
        figure.update_layout(showlegend=show_legend)
    figure.update_xaxes(
        title_text=x_title,
        showgrid=False,
        showline=True,
        linecolor=AXIS,
        linewidth=1,
        ticks="outside",
        tickcolor=AXIS,
        ticklen=4,
        tickfont={"color": INK_SECONDARY},
        title_font={"color": INK_SECONDARY, "size": 12.5},
        zeroline=False,
    )
    figure.update_yaxes(
        title_text=y_title,
        showgrid=True,
        gridcolor=GRID,
        gridwidth=1,
        showline=False,
        zeroline=False,
        tickfont={"color": INK_SECONDARY},
        title_font={"color": INK_SECONDARY, "size": 12.5},
        separatethousands=True,
        tickformat=",~f",  # números completos (1,500,000), nunca 1.5M
        automargin=True,
    )
    figure.update_xaxes(automargin=True)
    return figure


def line_chart(
    df: pd.DataFrame,
    x: str,
    y: str | Sequence[str],
    title: str,
    y_title: str,
    x_title: str = "Fecha",
    names: dict[str, str] | None = None,
    colors: dict[str, str] | None = None,
    height: int = 400,
) -> go.Figure:
    """Serie(s) en línea. Las columnas de subcuencas usan su color fijo."""
    columns = [y] if isinstance(y, str) else list(y)
    names = names or {}
    colors = colors or {}
    figure = go.Figure()
    next_slot = 0
    used = {subbasin_id(c) for c in columns if subbasin_id(c)}
    for column in columns:
        sid = subbasin_id(column)
        if column in colors:
            color = colors[column]
        elif sid and len(used) == len(columns):
            color = subbasin_color(sid)
        else:
            color = CATEGORICAL[next_slot % len(CATEGORICAL)]
            next_slot += 1
        name = names.get(column, label(column))
        places = decimals(column)
        figure.add_trace(go.Scatter(
            x=df[x],
            y=df[column],
            name=name,
            mode="lines",
            line={"width": 2, "color": color, "shape": "linear"},
            hovertemplate=f"%{{y:{_d3_format(places, not _is_elevation(column))}}}",
        ))
    style_figure(figure, title, y_title, x_title, height=height, show_legend=len(columns) > 1)
    if all(_is_elevation(c) for c in columns):
        figure.update_yaxes(tickformat="~f")
    if _is_elevation(x):
        figure.update_xaxes(tickformat="~f")
    if pd.api.types.is_datetime64_any_dtype(df[x]):
        dates = df[x].dropna()
        daily = bool(len(dates)) and bool((dates.dt.normalize() == dates).all())
        figure.update_xaxes(
            hoverformat="%d/%m/%Y" if daily else "%d/%m/%Y %H:%M",
            tickformat="%d/%m\n%Y",
        )
    return figure


def comparison_bar(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    y_title: str,
    value_decimals: int = 2,
    value_label: str | None = None,
    color: str = PRIMARY,
    height: int = 400,
    text_size: float = 12,
) -> go.Figure:
    """Barras con el valor real en la punta (sin abreviaturas como "m" o "k")."""
    fmt = _d3_format(value_decimals)
    value_label = value_label or label(y)
    figure = go.Figure(go.Bar(
        x=df[x],
        y=df[y],
        marker={"color": color, "line": {"width": 0}},
        text=df[y],
        texttemplate=f"%{{text:{fmt}}}",
        textposition="outside",
        textfont={"color": INK, "size": text_size, "family": FONT_FAMILY},
        cliponaxis=False,
        constraintext="none",
        hovertemplate=f"<b>%{{x}}</b><br>{value_label}: %{{y:{fmt}}}<extra></extra>",
    ))
    style_figure(figure, title, y_title, None, height=height, show_legend=False)
    figure.update_layout(hovermode="closest", bargap=0.38, barcornerradius=4)
    figure.update_yaxes(rangemode="tozero")
    # Espacio sobre la barra más alta para que el valor no se corte.
    top = float(pd.to_numeric(df[y], errors="coerce").max() or 0)
    if top > 0:
        figure.update_yaxes(range=[0, top * 1.16])
    return figure


def observed_vs_simulated(df: pd.DataFrame, subbasin_id: int) -> go.Figure:
    sim = f"Qsim_Subcuenca_{subbasin_id}_m3s"
    obs = f"Qobs_Subcuenca_{subbasin_id}_m3s"
    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=df["Fecha"], y=df[obs], name="Observado", mode="lines",
        line={"width": 1.6, "color": OBSERVED},
        hovertemplate="%{y:,.4f} m³/s",
    ))
    figure.add_trace(go.Scatter(
        x=df["Fecha"], y=df[sim], name="Simulado", mode="lines",
        line={"width": 2, "color": PRIMARY},
        hovertemplate="%{y:,.4f} m³/s",
    ))
    style_figure(
        figure,
        f"Caudal observado y simulado · Subcuenca {subbasin_id}",
        "Caudal (m³/s)",
        "Fecha",
        height=430,
        show_legend=True,
    )
    figure.update_xaxes(hoverformat="%d/%m/%Y %H:%M", tickformat="%d/%m\n%Y")
    return figure
