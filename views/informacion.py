from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.data_loader import content
from src.paths import ASSETS_DIR, SOURCE_DIR
from src.ui import page_header

page_header(
    "Documentación del proyecto",
    "Información técnica y galería",
    "Revisa los antecedentes, el alcance metodológico, las limitaciones de interpretación y los recursos gráficos incluidos en el archivo fuente.",
)

info_tab, method_tab, gallery_tab, details_tab, sources_tab = st.tabs([
    "Embalse", "Metodología", "Galería", "Detalles técnicos", "Fuentes"
])

with info_tab:
    st.markdown(content("informacion_embalse.md"))
    st.image(str(ASSETS_DIR / "technical_details/sistemas_abastecimiento_dmq.png"))

with method_tab:
    st.markdown(content("metodologia.md"))
    st.markdown(content("limitaciones.md"))

with gallery_tab:
    gallery = sorted((ASSETS_DIR / "thumbnails/gallery").glob("*.webp"))
    captions = {
        "01": "Vista inicial del sitio de la presa",
        "02": "Construcción del muro pantalla",
        "03": "Relleno del cuerpo de la presa",
        "04": "Estructura deslizante",
        "05": "Paramento aguas abajo durante la construcción",
        "06": "Vista panorámica desde la margen izquierda",
        "07": "Presa terminada",
        "08": "Embalse lleno desde la margen izquierda",
        "09": "Embalse lleno desde la margen derecha",
        "10": "Vertedero de excesos",
        "11": "Boya de monitoreo",
        "12": "Detalles de la presa",
        "13": "Estado actual de la zona de la presa",
    }
    for start in range(0, len(gallery), 3):
        columns = st.columns(3)
        for column, image in zip(columns, gallery[start:start + 3]):
            key = image.stem[:2]
            with column:
                st.image(str(image))
                st.markdown(f'<div class="gallery-caption">{captions.get(key, image.stem)}</div>', unsafe_allow_html=True)

with details_tab:
    details = sorted((ASSETS_DIR / "thumbnails/technical_details").glob("*.webp"))
    details = [item for item in details if item.name != "sistemas_abastecimiento_dmq.webp"]
    for image in details:
        with st.expander(image.stem.replace("_", " ").title()):
            st.image(str(image))

with sources_tab:
    st.markdown(content("fuentes.md"))
    document = SOURCE_DIR / "INFORMACION/PRESA SALVE FACCHA.docx"
    st.download_button(
        "Descargar documento informativo original",
        data=document.read_bytes(),
        file_name=document.name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
