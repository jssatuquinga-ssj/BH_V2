from __future__ import annotations

import streamlit as st

from src.ui import load_css, show_sidebar_brand

st.set_page_config(
    page_title="Embalse Salve Faccha",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

pages = {
    "Visor": [
        st.Page("views/home.py", title="Inicio", icon="🏔️", default=True),
        st.Page("views/subcuencas.py", title="Subcuencas", icon="🗺️"),
        st.Page("views/resultados.py", title="Resultados", icon="📈"),
        st.Page("views/embalse.py", title="Embalse", icon="💧"),
    ],
    "Documentación": [
        st.Page("views/informacion.py", title="Información técnica", icon="📚"),
    ],
}

with st.sidebar:
    show_sidebar_brand()
    st.divider()

navigation = st.navigation(pages)
navigation.run()
