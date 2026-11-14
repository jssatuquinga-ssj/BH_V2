from __future__ import annotations

import streamlit.components.v1 as components

from src.paths import ASSETS_DIR


def show_reservoir_animation(height: int = 430) -> None:
    svg = (ASSETS_DIR / "svg" / "embalse_animado.svg").read_text(encoding="utf-8")
    html = f"""
    <div style="background:linear-gradient(180deg,#092c3b,#0d4b5f);border-radius:22px;padding:14px;box-shadow:0 18px 45px rgba(4,30,40,.25);">
      {svg}
      <div style="font-family:Arial,sans-serif;text-align:center;color:#d9f7ff;font-size:13px;margin-top:-10px;">
        Silueta real del embalse · animación visual preliminar
      </div>
    </div>
    """
    components.html(html, height=height, scrolling=False)
