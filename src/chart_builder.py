from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def line_chart(df: pd.DataFrame, x: str, y: str | Sequence[str], title: str, y_title: str) -> go.Figure:
    figure = px.line(df, x=x, y=y, title=title)
    figure.update_layout(
        height=390,
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
        hovermode="x unified",
        legend_title_text="",
        yaxis_title=y_title,
        xaxis_title="Fecha",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(241,247,249,0.45)",
    )
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(gridcolor="rgba(120,150,160,0.22)")
    return figure


def comparison_bar(df: pd.DataFrame, x: str, y: str, title: str, y_title: str) -> go.Figure:
    figure = px.bar(df, x=x, y=y, text_auto=".3s", title=title)
    figure.update_layout(
        height=390,
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
        xaxis_title="",
        yaxis_title=y_title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(241,247,249,0.45)",
    )
    figure.update_traces(marker_color="#168aad")
    return figure


def observed_vs_simulated(df: pd.DataFrame, subbasin_id: int) -> go.Figure:
    sim = f"Qsim_Subcuenca_{subbasin_id}_m3s"
    obs = f"Qobs_Subcuenca_{subbasin_id}_m3s"
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=df["Fecha"], y=df[obs], name="Observado", mode="lines", line={"width": 1.6}))
    figure.add_trace(go.Scatter(x=df["Fecha"], y=df[sim], name="Simulado", mode="lines", line={"width": 1.6}))
    figure.update_layout(
        title=f"Caudal observado y simulado · Subcuenca {subbasin_id}",
        height=420,
        hovermode="x unified",
        yaxis_title="Caudal (m³/s)",
        xaxis_title="Fecha",
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(241,247,249,0.45)",
    )
    return figure
