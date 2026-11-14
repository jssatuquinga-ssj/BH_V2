from __future__ import annotations

import pandas as pd
import streamlit as st

from src.chart_builder import line_chart, observed_vs_simulated
from src.data_loader import (
    config,
    content,
    geojson,
    hourly_flows,
    hourly_precipitation,
    hourly_volumes,
    model_parameters,
    morphometry,
    observed_simulated,
    summary_subbasins,
    validation_metrics,
)
from src.formatting import metric_card, number, volume
from src.map_builder import VARIABLES, build_subbasin_map
from src.ui import page_header


@st.dialog("Criterio metodológico")
def methodology_dialog() -> None:
    st.markdown(content("metodologia.md"))


page_header(
    "Exploración espacial",
    "Visor interactivo de subcuencas",
    "Pasa el cursor sobre cada polígono para consultar sus indicadores. Selecciona una subcuenca en el mapa o mediante el control para actualizar los resultados.",
)

summary = summary_subbasins()
settings = config("subcuencas.json")
if "selected_subbasin" not in st.session_state:
    st.session_state.selected_subbasin = 1
pending = st.session_state.pop("pending_subbasin", None)
if pending is not None:
    st.session_state.selected_subbasin = int(pending)
    st.session_state.subbasin_selector = int(pending)

control_col, info_col = st.columns([4, 1])
with control_col:
    c1, c2 = st.columns(2)
    with c1:
        variable = st.selectbox("Variable representada", list(VARIABLES), index=2)
    with c2:
        selected_id = st.selectbox(
            "Subcuenca seleccionada",
            options=list(range(1, 9)),
            format_func=lambda value: f"Subcuenca {value}",
            index=int(st.session_state.selected_subbasin) - 1,
            key="subbasin_selector",
        )
        st.session_state.selected_subbasin = int(selected_id)
with info_col:
    st.write("")
    st.write("")
    if st.button("ⓘ Metodología"):
        methodology_dialog()

figure = build_subbasin_map(
    summary,
    geojson("subcuencas.geojson"),
    geojson("rios.geojson"),
    geojson("estaciones.geojson"),
    geojson("embalse.geojson"),
    variable,
    int(st.session_state.selected_subbasin),
)
map_event = st.plotly_chart(
    figure,
    on_select="rerun",
    selection_mode="points",
    key="subbasin_map",
)

try:
    points = map_event.selection.points
    if points:
        point = points[0]
        clicked = point.get("location")
        if clicked is None and point.get("customdata"):
            clicked = point["customdata"][0]
        if clicked is not None and int(clicked) != int(st.session_state.selected_subbasin):
            st.session_state.pending_subbasin = int(clicked)
            st.rerun()
except (AttributeError, KeyError, TypeError, ValueError):
    pass

sid = int(st.session_state.selected_subbasin)
row = summary.loc[summary["subcuenca_id"] == sid].iloc[0]
meta = settings[str(sid)]

badge_class = "method-badge" if meta["tipo_parametros"] == "Calibración independiente" else "method-badge transferred"
st.markdown(
    f'<span class="{badge_class}">{meta["tipo_parametros"]} · origen: {meta["origen_parametros"]}</span>',
    unsafe_allow_html=True,
)
if not meta["red_rios"]:
    st.caption("Esta subcuenca no dispone de una capa de ríos en los archivos fuente; no se añadieron elementos artificiales.")

metric_cols = st.columns(5)
items = [
    ("Área", f"{number(row['Area_km2'], 3)} km²", "Área del modelo"),
    ("Precipitación", f"{number(row['Precipitacion_total_mm'], 2)} mm", "Acumulada"),
    ("Caudal medio", f"{number(row['Q_medio_m3s'], 4)} m³/s", "Serie horaria"),
    ("Caudal máximo", f"{number(row['Q_max_m3s'], 4)} m³/s", "Máximo simulado"),
    ("Volumen", volume(row["Volumen_total_m3"]), "Acumulado"),
]
for column, item in zip(metric_cols, items):
    with column:
        st.markdown(metric_card(*item), unsafe_allow_html=True)

flows = hourly_flows()
precip = hourly_precipitation()
volumes = hourly_volumes()
params = model_parameters()
morph = morphometry()
metrics = validation_metrics()

min_date = flows["Fecha"].min().date()
max_date = flows["Fecha"].max().date()
date_range = st.date_input(
    "Periodo mostrado",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
else:
    start, end = pd.Timestamp(min_date), pd.Timestamp(max_date) + pd.Timedelta(days=1)

flow_filter = flows[(flows["Fecha"] >= start) & (flows["Fecha"] < end)]
precip_filter = precip[(precip["Fecha"] >= start) & (precip["Fecha"] < end)]
volume_filter = volumes[(volumes["Fecha"] >= start) & (volumes["Fecha"] < end)]

tab1, tab2, tab3, tab4 = st.tabs(["Series horarias", "Validación", "Parámetros", "Morfometría"])
with tab1:
    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.plotly_chart(line_chart(flow_filter, "Fecha", f"Q_Subcuenca_{sid}_m3s", f"Caudal · Subcuenca {sid}", "m³/s"))
    with chart_cols[1]:
        st.plotly_chart(line_chart(precip_filter, "Fecha", f"P_Subcuenca_{sid}_mm", f"Precipitación · Subcuenca {sid}", "mm/h"))
    st.plotly_chart(line_chart(volume_filter, "Fecha", f"Vol_Subcuenca_{sid}_m3", f"Volumen horario · Subcuenca {sid}", "m³"))

with tab2:
    if meta["caudal_observado"]:
        obs = observed_simulated()
        obs = obs[(obs["Fecha"] >= start) & (obs["Fecha"] < end)]
        st.plotly_chart(observed_vs_simulated(obs, sid))
        metric_row = metrics.loc[metrics["Subcuenca"] == f"Subcuenca_{sid}"].iloc[0]
        metric_columns = st.columns(5)
        for column, name in zip(metric_columns, ["NSE", "NSE_log", "KGE", "R2", "PBIAS_%"]):
            with column:
                st.metric(name, number(metric_row[name], 3))
    else:
        st.info("No existe una serie de caudal observado en los archivos entregados para esta subcuenca. El visor muestra resultados simulados con parámetros transferidos.")

with tab3:
    data = params[params["Subcuenca"] == f"Subcuenca_{sid}"][["Parametro", "Valor", "Tipo_parametros", "Origen_parametros"]]
    st.dataframe(data, hide_index=True)

with tab4:
    data = morph[morph["Subcuenca"] == f"Subcuenca_{sid}"][["Parametro", "Valor", "Unidad", "Interpretacion"]]
    st.dataframe(data, hide_index=True, use_container_width=True, height=520)
