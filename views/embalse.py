from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src.chart_builder import line_chart
from src.data_loader import reservoir_acv, reservoir_evaporation, reservoir_levels, spillway_curve, water_balance
from src.formatting import metric_card, number, volume
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
        number={"suffix": " m"},
        gauge={
            "axis": {"range": [min_level, max_level]},
            "bar": {"color": "#118ab2"},
            "steps": [{"range": [min_level, max_level], "color": "#dff4f8"}],
        },
        title={"text": "Posición dentro del periodo"},
    ))
    gauge.update_layout(height=230, margin={"l": 25, "r": 25, "t": 55, "b": 15}, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(gauge)

st.plotly_chart(line_chart(levels, "Fecha", "Cota_msnm", "Evolución de la cota del embalse", "m s. n. m."))

acv = reservoir_acv()
spillway = spillway_curve()
balance = water_balance()
evaporation = reservoir_evaporation()

tab1, tab2, tab3 = st.tabs(["Curvas del embalse", "Balance hídrico", "Evaporación"])
with tab1:
    acv_fig = go.Figure()
    acv_fig.add_trace(go.Scatter(x=acv["Cota [m s.n.m.]"], y=acv["Área [m²]"], name="Área", yaxis="y", mode="lines"))
    acv_fig.add_trace(go.Scatter(x=acv["Cota [m s.n.m.]"], y=acv["Volumen acumulado [m³]"], name="Volumen acumulado", yaxis="y2", mode="lines"))
    acv_fig.update_layout(
        title="Curva área-cota-volumen",
        xaxis_title="Cota (m s. n. m.)",
        yaxis={"title": "Área (m²)"},
        yaxis2={"title": "Volumen (m³)", "overlaying": "y", "side": "right"},
        height=430,
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(acv_fig)
    st.plotly_chart(line_chart(spillway, "Cota_Embalse_m", "Q_Vertedero_m3s", "Curva de descarga del vertedero lateral", "m³/s"))

with tab2:
    st.plotly_chart(line_chart(balance, "Fecha", ["Vol_Total_8_Subcuencas_m3", "Vol_P_Embalse_m3"], "Aportes diarios al embalse", "m³/día"))
    st.plotly_chart(line_chart(balance, "Fecha", ["Vol_Ev_Embalse_m3", "Vol_Demanda_m3"], "Salidas diarias registradas", "m³/día"))
    st.dataframe(balance, hide_index=True, use_container_width=True, height=360)

with tab3:
    st.plotly_chart(line_chart(evaporation, "Fecha", ["Ev_Linacre", "Ev_KFN"], "Estimaciones diarias de evaporación", "mm/día"))
