from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src.chart_builder import CATEGORICAL, FONT_FAMILY, GRID, INK, INK_SECONDARY, PRIMARY, line_chart, style_figure
from src.data_loader import reservoir_acv, reservoir_evaporation, reservoir_levels, spillway_curve, water_balance
from src.formatting import metric_card, number, volume
from src.labels import label
from src.reservoir_animation import show_reservoir_animation
from src.ui import page_header

page_header(
    "Comportamiento del almacenamiento",
    "Embalse Salve Faccha",
    "Consulta la variación diaria de la cota y el volumen, la curva área-cota-volumen, la descarga del vertedero y los principales componentes del balance hídrico.",
)

levels = reservoir_levels()
selected_index = st.slider("Día de la serie", 0, len(levels) - 1, 0)
selected = levels.iloc[selected_index]

left, right = st.columns([1.25, 1], gap="large")
with left:
    show_reservoir_animation(height=430)
with right:
    st.subheader(selected["Fecha"].strftime("%d/%m/%Y"))
    st.markdown(metric_card("Cota del embalse", f"{number(selected['Cota_msnm'], 2)} m s. n. m.", "Valor diario"), unsafe_allow_html=True)
    st.write("")
    st.markdown(metric_card("Volumen almacenado", volume(selected["Volumen_m3"]), "Curva área-cota-volumen"), unsafe_allow_html=True)
    min_level = float(levels["Cota_msnm"].min())
    max_level = float(levels["Cota_msnm"].max())
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(selected["Cota_msnm"]),
        number={"suffix": " m s. n. m.", "valueformat": ".2f", "font": {"size": 30, "color": INK, "family": FONT_FAMILY}},
        gauge={
            "axis": {"range": [min_level, max_level], "tickformat": ".1f", "tickcolor": GRID, "tickfont": {"color": INK_SECONDARY}},
            "bar": {"color": PRIMARY, "thickness": 0.32},
            "bgcolor": "#ffffff",
            "borderwidth": 0,
            "steps": [{"range": [min_level, max_level], "color": "#e8f1fb"}],
        },
        title={"text": "Posición de la cota dentro del periodo", "font": {"size": 14, "color": INK_SECONDARY, "family": FONT_FAMILY}},
    ))
    gauge.update_layout(height=240, margin={"l": 25, "r": 25, "t": 55, "b": 10}, paper_bgcolor="rgba(0,0,0,0)", font={"family": FONT_FAMILY})
    st.plotly_chart(gauge)

st.plotly_chart(line_chart(levels, "Fecha", "Cota_msnm", "Evolución de la cota del embalse", "Cota (m s. n. m.)"))

acv = reservoir_acv()
spillway = spillway_curve()
balance = water_balance()
evaporation = reservoir_evaporation()

tab1, tab2, tab3 = st.tabs(["Curvas del embalse", "Balance hídrico", "Evaporación"])
with tab1:
    # Curva área-cota-volumen: se presenta en dos gráficos con un solo eje cada uno
    # (área y volumen tienen escalas muy distintas). Los datos son los mismos.
    cota = "Cota [m s.n.m.]"
    area_col, vol_col = st.columns(2)
    with area_col:
        area_fig = go.Figure(go.Scatter(
            x=acv[cota], y=acv["Área [m²]"], mode="lines", name="Área",
            line={"width": 2, "color": PRIMARY},
            hovertemplate="Cota %{x:.2f} m s. n. m.<br>Área %{y:,.2f} m²<extra></extra>",
        ))
        style_figure(area_fig, "Curva área-cota", "Área (m²)", "Cota (m s. n. m.)", height=400, show_legend=False)
        area_fig.update_layout(hovermode="closest")
        area_fig.update_xaxes(tickformat="~f")
        st.plotly_chart(area_fig)
    with vol_col:
        vol_fig = go.Figure(go.Scatter(
            x=acv[cota], y=acv["Volumen acumulado [m³]"], mode="lines", name="Volumen acumulado",
            line={"width": 2, "color": CATEGORICAL[1]},
            hovertemplate="Cota %{x:.2f} m s. n. m.<br>Volumen %{y:,.2f} m³<extra></extra>",
        ))
        style_figure(vol_fig, "Curva volumen-cota", "Volumen acumulado (m³)", "Cota (m s. n. m.)", height=400, show_legend=False)
        vol_fig.update_layout(hovermode="closest")
        vol_fig.update_xaxes(tickformat="~f")
        st.plotly_chart(vol_fig)
    spill_fig = line_chart(spillway, "Cota_Embalse_m", "Q_Vertedero_m3s", "Curva de descarga del vertedero lateral", "Caudal (m³/s)", x_title="Cota del embalse (m s. n. m.)")
    spill_fig.update_layout(hovermode="closest")
    spill_fig.update_traces(hovertemplate="Cota %{x:.2f} m s. n. m.<br>Caudal %{y:,.3f} m³/s<extra></extra>")
    st.plotly_chart(spill_fig)

with tab2:
    st.plotly_chart(line_chart(
        balance, "Fecha",
        ["Vol_Total_8_Subcuencas_m3", "Vol_P_Embalse_m3"],
        "Aportes diarios al embalse", "Volumen (m³/día)",
    ))
    st.plotly_chart(line_chart(
        balance, "Fecha",
        ["Vol_Ev_Embalse_m3", "Vol_Demanda_m3"],
        "Salidas diarias registradas", "Volumen (m³/día)",
        colors={"Vol_Ev_Embalse_m3": CATEGORICAL[2], "Vol_Demanda_m3": CATEGORICAL[1]},
    ))

    st.markdown('<div class="section-title">Tabla del balance hídrico diario</div>', unsafe_allow_html=True)
    # Todas las columnas con 2 decimales; los nombres se muestran con su unidad.
    column_config = {"Fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY")}
    for column in balance.columns[1:]:
        column_config[column] = st.column_config.NumberColumn(label(column), format="%.2f")
    st.dataframe(
        balance,
        hide_index=True,
        width="stretch",
        height=420,
        column_config=column_config,
    )
    st.download_button(
        "Descargar balance hídrico (CSV)",
        balance.to_csv(index=False).encode("utf-8-sig"),
        file_name="balance_hidrico_diario.csv",
        mime="text/csv",
    )

with tab3:
    st.plotly_chart(line_chart(evaporation, "Fecha", ["Ev_Linacre", "Ev_KFN"], "Estimaciones diarias de evaporación", "Evaporación (mm/día)"))
