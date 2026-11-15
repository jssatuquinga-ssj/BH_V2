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
    subbasin_hourly_results,
    subbasin_model_summary,
    subbasin_results_excel,
    summary_subbasins,
    validation_metrics,
)
from src.labels import column_config, decimals, label
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

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Series horarias", "Validación", "Parámetros", "Morfometría", "Resultados del modelo"])
with tab1:
    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.plotly_chart(line_chart(flow_filter, "Fecha", f"Q_Subcuenca_{sid}_m3s", f"Caudal · Subcuenca {sid}", "Caudal (m³/s)", colors={f"Q_Subcuenca_{sid}_m3s": "#2a78d6"}))
    with chart_cols[1]:
        st.plotly_chart(line_chart(precip_filter, "Fecha", f"P_Subcuenca_{sid}_mm", f"Precipitación · Subcuenca {sid}", "Precipitación (mm/h)", colors={f"P_Subcuenca_{sid}_mm": "#2a78d6"}))
    st.plotly_chart(line_chart(volume_filter, "Fecha", f"Vol_Subcuenca_{sid}_m3", f"Volumen horario · Subcuenca {sid}", "Volumen (m³)", colors={f"Vol_Subcuenca_{sid}_m3": "#2a78d6"}))

with tab2:
    if meta["caudal_observado"]:
        obs = observed_simulated()
        obs = obs[(obs["Fecha"] >= start) & (obs["Fecha"] < end)]
        st.plotly_chart(observed_vs_simulated(obs, sid))
        metric_row = metrics.loc[metrics["Subcuenca"] == f"Subcuenca_{sid}"].iloc[0]
        metric_columns = st.columns(5)
        for column, name in zip(metric_columns, ["NSE", "NSE_log", "KGE", "R2", "PBIAS_%"]):
            with column:
                st.metric(label(name), number(metric_row[name], 3))
    else:
        st.info("No existe una serie de caudal observado en los archivos entregados para esta subcuenca. El visor muestra resultados simulados con parámetros transferidos.")

with tab3:
    data = params[params["Subcuenca"] == f"Subcuenca_{sid}"][["Parametro", "Valor", "Tipo_parametros", "Origen_parametros"]]
    st.dataframe(data, hide_index=True, width="stretch", column_config=column_config(data, 4))

with tab4:
    data = morph[morph["Subcuenca"] == f"Subcuenca_{sid}"][["Parametro", "Valor", "Unidad", "Interpretacion"]]
    st.dataframe(data, hide_index=True, width="stretch", height=520, column_config=column_config(data, 4))

with tab5:
    results = subbasin_hourly_results(sid)
    model_summary = subbasin_model_summary()
    excel_path = subbasin_results_excel(sid)

    st.markdown(
        f'<div class="section-title">Resultados del modelo · Subcuenca {sid}</div>'
        f'<div class="section-note">Contenido del archivo <b>{excel_path.name}</b> '
        "(hojas <i>Resumen</i> y <i>Serie_Horaria</i>), mostrado sin modificar los valores.</div>",
        unsafe_allow_html=True,
    )

    # 1) Resumen del modelo (una fila del Excel, presentada en vertical).
    summary_row = model_summary.loc[model_summary["Subcuenca"] == f"Subcuenca_{sid}"]
    if not summary_row.empty:
        record = summary_row.iloc[0]
        rows = []
        for column, value in record.items():
            if column == "Subcuenca" or pd.isna(value):
                continue
            if isinstance(value, pd.Timestamp):
                text = value.strftime("%d/%m/%Y %H:%M")
            elif isinstance(value, (int, float)):
                text = f"{float(value):,.{decimals(column)}f}"
            else:
                text = str(value)
            rows.append({"Indicador": label(column), "Valor": text})
        st.markdown("**Resumen**")
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=min(38 * (len(rows) + 1), 520))

    # 2) Gráfico de la variable elegida, en el periodo seleccionado arriba.
    period = results[(results["Fecha"] >= start) & (results["Fecha"] < end)]
    numeric_columns = [
        column for column in results.columns
        if column not in ("Fecha", "Area_m2") and pd.api.types.is_numeric_dtype(results[column])
    ]
    st.markdown("**Serie horaria**")
    variable_column = st.selectbox(
        "Variable a graficar",
        numeric_columns,
        index=numeric_columns.index("Qsim_m3s") if "Qsim_m3s" in numeric_columns else 0,
        format_func=label,
        key=f"model_variable_{sid}",
    )
    variable_name = label(variable_column)
    unit = variable_name[variable_name.rfind("(") + 1:-1] if variable_name.endswith(")") else ""
    st.plotly_chart(line_chart(
        period, "Fecha", variable_column,
        f"{variable_name.split(' (')[0]} · Subcuenca {sid}",
        f"{variable_name.split(' (')[0]} ({unit})" if unit else variable_name,
        colors={variable_column: "#2a78d6"},
    ))

    # 3) Tabla completa de la serie horaria (periodo seleccionado).
    st.caption(f"{len(period):,} registros horarios en el periodo seleccionado · {len(results.columns)} columnas.")
    st.dataframe(
        period,
        hide_index=True,
        width="stretch",
        height=460,
        column_config=column_config(period),
    )

    # 4) Descargas.
    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            "Descargar serie horaria del periodo (CSV)",
            period.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"serie_horaria_subcuenca_{sid}.csv",
            mime="text/csv",
            width="stretch",
            key=f"download_csv_{sid}",
        )
    with dl2:
        if excel_path.exists():
            st.download_button(
                "Descargar Excel original de resultados",
                excel_path.read_bytes(),
                file_name=excel_path.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
                key=f"download_xlsx_{sid}",
            )
