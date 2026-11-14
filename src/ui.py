from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.paths import ASSETS_DIR


def load_css() -> None:
    css = (ASSETS_DIR / "css" / "app.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def page_header(kicker: str, title: str, description: str) -> None:
    st.markdown(
        f"""
        <section class="page-header">
          <div class="page-kicker">{kicker}</div>
          <h1>{title}</h1>
          <p>{description}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def show_sidebar_brand() -> None:
    logo_emaap = ASSETS_DIR / "logos" / "emaap.png"
    logo_uce = ASSETS_DIR / "logos" / "uce.png"
    col1, col2 = st.columns([2.2, 1])
    with col1:
        st.image(str(logo_emaap), use_container_width=True)
    with col2:
        st.image(str(logo_uce), use_container_width=True)
    st.markdown("**Visor hidrológico Salve Faccha**")
    st.caption("Aplicación preliminar para consulta de resultados previamente calculados.")
