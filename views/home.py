from __future__ import annotations

import streamlit as st

from src.data_loader import content, summary_subbasins, summary_system
from src.formatting import metric_card, number, volume
from src.paths import ASSETS_DIR
from src.reservoir_animation import show_reservoir_animation


@st.dialog("Información general del embalse")
def information_dialog() -> None:
    st.markdown(content("informacion_embalse.md"))


system = summary_system().iloc[0]
subbasins = summary_subbasins()

left, right = st.columns([1.05, 1.35], gap="large")
with left:
    st.markdown(
        """
        <section class="hero-panel">
          <div class="page-kicker">Sistema Papallacta · Ecuador</div>
          <h2>Embalse Salve Faccha</h2>
          <p>Visor interactivo de resultados hidrológicos, balance hídrico, comportamiento del embalse y caracterización de ocho subcuencas.</p>
          <div>
            <span class="hero-chip">8 subcuencas</span>
            <span class="hero-chip">Series horarias</span>
            <span class="hero-chip">Balance diario</span>
            <span class="hero-chip">Información GIS</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    btn_info, btn_tesis = st.columns(2)
    with btn_info:
        if st.button("ⓘ Sobre el embalse", use_container_width=True, type="primary"):
            information_dialog()
    with btn_tesis:
        if st.button("📘 Ver la tesis", use_container_width=True):
            st.switch_page("views/tesis.py")
    st.markdown(
        """
        <div class="info-strip">
        Esta versión consulta resultados previamente calculados. No vuelve a ejecutar el modelo hidrológico ni modifica los archivos Excel originales.
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    show_reservoir_animation(height=445)

st.subheader("Resumen del sistema")
cols = st.columns(4)
metrics = [
    ("Área total", f"{number(system['Area_total_km2'], 2)} km²", "Ocho subcuencas"),
    ("Caudal medio total", f"{number(system['Q_total_medio_m3s'], 3)} m³/s", "Serie horaria consolidada"),
    ("Caudal máximo total", f"{number(system['Q_total_max_m3s'], 3)} m³/s", "Máximo del periodo"),
    ("Volumen generado", volume(system['Volumen_total_8_subcuencas_m3']), "Periodo analizado"),
]
for column, item in zip(cols, metrics):
    with column:
        st.markdown(metric_card(*item), unsafe_allow_html=True)

st.write("")
col_a, col_b = st.columns([1.1, 1], gap="large")
with col_a:
    st.subheader("Criterio de calibración")
    st.markdown(
        """
        - **Subcuenca 1:** calibración independiente.
        - **Subcuencas 2, 3, 4 y 5:** parámetros transferidos desde la subcuenca 1.
        - **Subcuenca 6:** calibración independiente.
        - **Subcuencas 7 y 8:** parámetros transferidos desde la subcuenca 1.

        Los resultados de las subcuencas 1 y 6 incluyen caudales observados y métricas de validación. Las demás se identifican en el visor como simulaciones con parámetros transferidos.
        """
    )
with col_b:
    st.subheader("Vista preliminar del proyecto")
    images = [
        ASSETS_DIR / "thumbnails/gallery/08_presa_margen_izquierda_embalse_lleno.webp",
        ASSETS_DIR / "thumbnails/gallery/10_vertedero_excesos.webp",
    ]
    image_cols = st.columns(2)
    for column, image in zip(image_cols, images):
        with column:
            st.image(str(image))
    st.caption("Utiliza el menú lateral para abrir el mapa, explorar resultados o revisar la documentación técnica.")
