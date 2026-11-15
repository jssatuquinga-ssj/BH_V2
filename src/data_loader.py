from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src.paths import CONFIG_DIR, CONTENT_DIR, GIS_DIR, PROCESSED_DIR, RESERVOIR_DIR, SOURCE_DIR, SUMMARY_DIR, TIME_SERIES_DIR

PROCESSED_SUBBASINS_DIR = PROCESSED_DIR / "subcuencas"


def _mtime(path: str | Path) -> float:
    """Fecha de modificación del archivo: si el archivo cambia, se vuelve a leer."""
    try:
        return Path(path).stat().st_mtime
    except OSError:
        return 0.0


@st.cache_data(show_spinner=False)
def _load_csv(path: str, mtime: float) -> pd.DataFrame:
    df = pd.read_csv(path)
    for column in df.columns:
        if column.lower().startswith("fecha"):
            df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def _load_json(path: str, mtime: float) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def _load_text(path: str, mtime: float) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_csv(path: str | Path) -> pd.DataFrame:
    return _load_csv(str(path), _mtime(path))


def load_json(path: str | Path) -> dict[str, Any]:
    return _load_json(str(path), _mtime(path))


def load_text(path: str | Path) -> str:
    return _load_text(str(path), _mtime(path))


def summary_subbasins() -> pd.DataFrame:
    df = load_csv(SUMMARY_DIR / "resumen_subcuencas.csv").copy()
    df["subcuenca_id"] = df["Subcuenca"].str.extract(r"(\d+)").astype(int)
    return df


def summary_system() -> pd.DataFrame:
    return load_csv(SUMMARY_DIR / "resumen_sistema.csv")


def hourly_flows() -> pd.DataFrame:
    return load_csv(TIME_SERIES_DIR / "caudales_horarios.csv")


def hourly_precipitation() -> pd.DataFrame:
    return load_csv(TIME_SERIES_DIR / "precipitacion_horaria.csv")


def hourly_volumes() -> pd.DataFrame:
    return load_csv(TIME_SERIES_DIR / "volumenes_horarios.csv")


def observed_simulated() -> pd.DataFrame:
    return load_csv(TIME_SERIES_DIR / "caudales_observados_simulados.csv")


def daily_flows() -> pd.DataFrame:
    return load_csv(TIME_SERIES_DIR / "caudales_diarios.csv")


def daily_precipitation() -> pd.DataFrame:
    return load_csv(TIME_SERIES_DIR / "precipitacion_diaria.csv")


def daily_volumes() -> pd.DataFrame:
    return load_csv(TIME_SERIES_DIR / "volumen_diario.csv")


def water_balance() -> pd.DataFrame:
    return load_csv(TIME_SERIES_DIR / "balance_hidrico_diario.csv")


def validation_metrics() -> pd.DataFrame:
    return load_csv(SUMMARY_DIR / "metricas_validacion.csv")


def model_parameters() -> pd.DataFrame:
    return load_csv(SUMMARY_DIR / "parametros_modelo.csv")


def morphometry() -> pd.DataFrame:
    return load_csv(SUMMARY_DIR / "morfometria_subcuencas.csv")


def reservoir_levels() -> pd.DataFrame:
    return load_csv(RESERVOIR_DIR / "niveles_embalse.csv")


def reservoir_acv() -> pd.DataFrame:
    return load_csv(RESERVOIR_DIR / "curva_area_cota_volumen.csv")


def spillway_curve() -> pd.DataFrame:
    return load_csv(RESERVOIR_DIR / "curva_descarga_vertedero.csv")


def reservoir_evaporation() -> pd.DataFrame:
    return load_csv(RESERVOIR_DIR / "evaporacion_diaria.csv")


def geojson(name: str) -> dict[str, Any]:
    return load_json(GIS_DIR / name)


def config(name: str) -> dict[str, Any]:
    return load_json(CONFIG_DIR / name)


def content(name: str) -> str:
    return load_text(CONTENT_DIR / name)


def subbasin_hourly_results(sid: int) -> pd.DataFrame:
    """Hoja Serie_Horaria del Excel de resultados de la subcuenca."""
    return load_csv(PROCESSED_SUBBASINS_DIR / f"serie_horaria_subcuenca_{int(sid)}.csv")


def subbasin_model_summary() -> pd.DataFrame:
    """Hojas Resumen de los ocho Excel de resultados (una fila por subcuenca)."""
    return load_csv(PROCESSED_SUBBASINS_DIR / "resumen_modelo_subcuencas.csv")


def subbasin_results_excel(sid: int) -> Path:
    """Ruta del Excel original de resultados de la subcuenca."""
    sid = int(sid)
    return (
        SOURCE_DIR
        / "CUENCA SALVE FACCHA"
        / f"Subcuenca_{sid}"
        / f"Resultado_Mod_Subcuenca_{sid}"
        / f"Resultados_Modelo_Mejorado_Subcuenca_{sid}.xlsx"
    )
