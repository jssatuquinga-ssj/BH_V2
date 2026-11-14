from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.data_loader import content, load_json
from src.paths import ASSETS_DIR, CONFIG_DIR
from src.ui import page_header

TESIS_DIR = ASSETS_DIR / "tesis"


def find_thesis_pdf() -> Path | None:
    """Devuelve el primer PDF que encuentre en assets/tesis (sin importar su nombre)."""
    pdfs = sorted(TESIS_DIR.glob("*.pdf"))
    return pdfs[0] if pdfs else None


@st.cache_data(show_spinner="Cargando la tesis…")
def read_pdf(path: str, modified: float) -> bytes:
    # 'modified' hace que se recargue automáticamente si cambias el PDF.
    return Path(path).read_bytes()


info = load_json(CONFIG_DIR / "tesis.json")
pdf_path = find_thesis_pdf()

page_header(
    "Trabajo de titulación",
    "Tesis completa",
    "Consulta el documento completo del proyecto técnico que respalda los resultados presentados en este visor.",
)

left, right = st.columns([1, 1.25], gap="large")

with left:
    autores = "".join(f"<li>{a}</li>" for a in info.get("autores", []))
    chips = "".join(f'<span class="hero-chip">{k}</span>' for k in info.get("palabras_clave", []))
    st.markdown(
        f"""
        <section class="thesis-card">
          <div class="page-kicker">{info.get("universidad", "")}</div>
          <h3>{info.get("titulo", "")}</h3>
          <p class="thesis-type">{info.get("tipo", "")}</p>
          <div class="thesis-meta">
            <div><span>Autores</span><ul>{autores}</ul></div>
            <div><span>Tutora</span><p>{info.get("tutora", "")}</p></div>
            <div><span>Lugar y año</span><p>{info.get("ciudad_anio", "")}</p></div>
          </div>
          <div>{chips}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    if pdf_path is not None:
        pdf_bytes = read_pdf(str(pdf_path), pdf_path.stat().st_mtime)
        size_mb = len(pdf_bytes) / 1_048_576
        st.download_button(
            f"⬇️ Descargar tesis en PDF ({size_mb:.1f} MB)",
            data=pdf_bytes,
            file_name=pdf_path.name,
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )

with right:
    st.subheader("Resumen")
    with st.container(height=430, border=True):
        st.markdown(content("tesis_resumen.md"))

st.divider()
st.subheader("Documento completo")

if pdf_path is None:
    st.info(
        "Aún no hay un PDF en la carpeta `assets/tesis`. Copia ahí el archivo de la tesis "
        "y súbelo a GitHub para que aparezca en esta sección."
    )
else:
    st.caption("Usa la barra del visor para desplazarte, acercar o alejar el documento.")
    st.pdf(pdf_bytes, height=900)
