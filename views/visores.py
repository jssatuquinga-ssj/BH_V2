from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from src.data_loader import load_json
from src.paths import CONFIG_DIR
from src.ui import page_header

page_header(
    "Plataforma integrada",
    "Visores enlazados",
    "Accede a otros visores hidrológicos relacionados con el sistema Salve Faccha y sus estaciones.",
)

visores = load_json(CONFIG_DIR / "visores.json").get("visores", [])

if not visores:
    st.info(
        "Todavía no hay visores enlazados. Para agregar uno, añade su nombre y su enlace "
        "en el archivo `config/visores.json`."
    )
    st.stop()

nombres = [f"{v.get('icono', '🔗')} {v['nombre']}" for v in visores]
seleccion = st.radio("Selecciona un visor", nombres, horizontal=True, label_visibility="collapsed")
visor = visores[nombres.index(seleccion)]

col_text, col_btn = st.columns([3, 1], vertical_alignment="center")
with col_text:
    st.markdown(f"### {visor['nombre']}")
    if visor.get("descripcion"):
        st.write(visor["descripcion"])
with col_btn:
    st.link_button("Abrir en otra pestaña ↗", visor["url"], use_container_width=True, type="primary")

if visor.get("incrustar", True):
    url = visor["url"]
    if ".streamlit.app" in url and "embed=" not in url:
        url += ("&" if "?" in url else "?") + "embed=true"
    components.iframe(url, height=visor.get("alto", 850), scrolling=True)
