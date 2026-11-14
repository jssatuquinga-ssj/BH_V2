from __future__ import annotations

import streamlit as st

from src.chart_builder import comparison_bar, line_chart, observed_vs_simulated
from src.data_loader import (
    daily_flows,
    daily_precipitation,
    daily_volumes,
    hourly_flows,
    hourly_precipitation,
    hourly_volumes,
    observed_simulated,
    summary_subbasins,
    validation_metrics,
)
from src.paths import SOURCE_DIR, TIME_SERIES_DIR
from src.ui import page_header

page_header(
    "Análisis temporal",
    "Resultados consolidados",
    "Compara las ocho subcuencas, revisa las series horarias y diarias y consulta las métricas disponibles para las calibraciones independientes.",
)

summary = summary_subbasins().sort_values("subcuenca_id")
summary["Nombre"] = summary["subcuenca_id"].map(lambda value: f"S{value}")

tab1, tab2, tab3, tab4 = st.tabs(["Comparación", "Series temporales", "Validación", "Tablas y descargas"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(comparison_bar(summary, "Nombre", "Q_medio_m3s", "Caudal medio por subcuenca", "m³/s"))
    with col2:
        st.plotly_chart(comparison_bar(summary, "Nombre", "Precipitacion_total_mm", "Precipitación acumulada", "mm"))
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(comparison_bar(summary, "Nombre", "Volumen_total_m3", "Volumen acumulado", "m³"))
    with col4:
        st.plotly_chart(comparison_bar(summary, "Nombre", "Area_km2", "Área modelada", "km²"))

with tab2:
    resolution = st.radio("Resolución", ["Horaria", "Diaria"], horizontal=True)
    selected = st.multiselect(
        "Subcuencas",
        options=list(range(1, 9)),
        default=[1, 6],
        format_func=lambda value: f"Subcuenca {value}",
    )
    if not selected:
        st.warning("Selecciona al menos una subcuenca.")
    elif resolution == "Horaria":
        flows = hourly_flows()
        precip = hourly_precipitation()
        volumes = hourly_volumes()
        st.plotly_chart(line_chart(flows, "Fecha", [f"Q_Subcuenca_{sid}_m3s" for sid in selected], "Caudales horarios", "m³/s"))
        st.plotly_chart(line_chart(precip, "Fecha", [f"P_Subcuenca_{sid}_mm" for sid in selected], "Precipitación horaria", "mm/h"))
        st.plotly_chart(line_chart(volumes, "Fecha", [f"Vol_Subcuenca_{sid}_m3" for sid in selected], "Volúmenes horarios", "m³"))
    else:
        flows = daily_flows()
        precip = daily_precipitation()
        volumes = daily_volumes()
        st.plotly_chart(line_chart(flows, "Fecha", [f"Q_Subcuenca_{sid}_m3s" for sid in selected], "Caudales diarios", "m³/s"))
        st.plotly_chart(line_chart(precip, "Fecha", [f"P_Subcuenca_{sid}_mm" for sid in selected], "Precipitación diaria", "mm/día"))
        st.plotly_chart(line_chart(volumes, "Fecha", [f"Vol_Subcuenca_{sid}_m3" for sid in selected], "Volúmenes diarios", "m³/día"))

with tab3:
    obs = observed_simulated()
    choice = st.radio("Calibración", [1, 6], horizontal=True, format_func=lambda value: f"Subcuenca {value}")
    st.plotly_chart(observed_vs_simulated(obs, choice))
    metrics = validation_metrics()
    st.dataframe(metrics, hide_index=True)
    st.caption("Las métricas se presentan únicamente para las subcuencas que disponen de caudal observado en los archivos suministrados.")

with tab4:
    st.subheader("Resumen de resultados")
    st.dataframe(summary.drop(columns="Nombre"), hide_index=True, use_container_width=True, height=360)
    st.download_button(
        "Descargar resumen procesado (CSV)",
        data=(TIME_SERIES_DIR.parent / "summaries/resumen_subcuencas.csv").read_bytes(),
        file_name="resumen_subcuencas.csv",
        mime="text/csv",
        use_container_width=True,
    )
    original = SOURCE_DIR / "RESULTADOS/Resumen_General_Modelo_Mejorado_8Subcuencas.xlsx"
    st.download_button(
        "Descargar Excel original consolidado",
        data=original.read_bytes(),
        file_name=original.name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
