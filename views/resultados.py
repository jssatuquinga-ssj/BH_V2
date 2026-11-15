from __future__ import annotations

import streamlit as st

from src.chart_builder import comparison_bar, line_chart, observed_vs_simulated
from src.labels import column_config
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
        st.plotly_chart(comparison_bar(summary, "Nombre", "Q_medio_m3s", "Caudal medio por subcuenca", "Caudal (m³/s)", value_decimals=4, value_label="Caudal medio (m³/s)"))
    with col2:
        st.plotly_chart(comparison_bar(summary, "Nombre", "Precipitacion_total_mm", "Precipitación acumulada", "Precipitación (mm)", value_decimals=2, value_label="Precipitación acumulada (mm)"))
    col3, col4 = st.columns([1.45, 1])
    with col3:
        st.plotly_chart(comparison_bar(summary, "Nombre", "Volumen_total_m3", "Volumen acumulado", "Volumen (m³)", value_decimals=0, value_label="Volumen acumulado (m³)", text_size=11))
    with col4:
        st.plotly_chart(comparison_bar(summary, "Nombre", "Area_km2", "Área modelada", "Área (km²)", value_decimals=3, value_label="Área (km²)"))
    st.caption("S1 a S8 = subcuencas 1 a 8. Los valores sobre cada barra son los resultados del modelo, sin redondeos abreviados.")

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
        st.plotly_chart(line_chart(flows, "Fecha", [f"Q_Subcuenca_{sid}_m3s" for sid in selected], "Caudales horarios", "Caudal (m³/s)", names={f"Q_Subcuenca_{sid}_m3s": f"Subcuenca {sid}" for sid in selected}))
        st.plotly_chart(line_chart(precip, "Fecha", [f"P_Subcuenca_{sid}_mm" for sid in selected], "Precipitación horaria", "Precipitación (mm/h)", names={f"P_Subcuenca_{sid}_mm": f"Subcuenca {sid}" for sid in selected}))
        st.plotly_chart(line_chart(volumes, "Fecha", [f"Vol_Subcuenca_{sid}_m3" for sid in selected], "Volúmenes horarios", "Volumen (m³)", names={f"Vol_Subcuenca_{sid}_m3": f"Subcuenca {sid}" for sid in selected}))
    else:
        flows = daily_flows()
        precip = daily_precipitation()
        volumes = daily_volumes()
        st.plotly_chart(line_chart(flows, "Fecha", [f"Q_Subcuenca_{sid}_m3s" for sid in selected], "Caudales diarios", "Caudal (m³/s)", names={f"Q_Subcuenca_{sid}_m3s": f"Subcuenca {sid}" for sid in selected}))
        st.plotly_chart(line_chart(precip, "Fecha", [f"P_Subcuenca_{sid}_mm" for sid in selected], "Precipitación diaria", "Precipitación (mm/día)", names={f"P_Subcuenca_{sid}_mm": f"Subcuenca {sid}" for sid in selected}))
        st.plotly_chart(line_chart(volumes, "Fecha", [f"Vol_Subcuenca_{sid}_m3" for sid in selected], "Volúmenes diarios", "Volumen (m³/día)", names={f"Vol_Subcuenca_{sid}_m3": f"Subcuenca {sid}" for sid in selected}))

with tab3:
    obs = observed_simulated()
    choice = st.radio("Calibración", [1, 6], horizontal=True, format_func=lambda value: f"Subcuenca {value}")
    st.plotly_chart(observed_vs_simulated(obs, choice))
    metrics = validation_metrics()
    st.dataframe(metrics, hide_index=True, width="stretch", column_config=column_config(metrics, 4))
    st.caption("Las métricas se presentan únicamente para las subcuencas que disponen de caudal observado en los archivos suministrados.")

with tab4:
    st.subheader("Resumen de resultados")
    table = summary.drop(columns=["Nombre", "subcuenca_id"], errors="ignore")
    st.dataframe(table, hide_index=True, width="stretch", height=360, column_config=column_config(table, 4))
    st.download_button(
        "Descargar resumen procesado (CSV)",
        data=(TIME_SERIES_DIR.parent / "summaries/resumen_subcuencas.csv").read_bytes(),
        file_name="resumen_subcuencas.csv",
        mime="text/csv",
        width="stretch",
    )
    original = SOURCE_DIR / "RESULTADOS/Resumen_General_Modelo_Mejorado_8Subcuencas.xlsx"
    st.download_button(
        "Descargar Excel original consolidado",
        data=original.read_bytes(),
        file_name=original.name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )
