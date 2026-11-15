"""Nombres legibles y formatos de las variables.

Solo cambia cómo se MUESTRAN las columnas en tablas, leyendas y gráficos.
Los archivos CSV y Excel conservan sus nombres originales.
"""
from __future__ import annotations

import re

# Nombre visible y número de decimales para cada columna conocida.
_FIXED: dict[str, tuple[str, int]] = {
    "Fecha": ("Fecha", 0),
    # Balance hídrico diario
    "Vol_Total_8_Subcuencas_m3": ("Total 8 subcuencas (m³)", 2),
    "Cota_msnm": ("Cota (m s. n. m.)", 2),
    "Vol_Embalse_m3": ("Volumen del embalse (m³)", 2),
    "Volumen_m3": ("Volumen almacenado (m³)", 2),
    "Dif_Vol_m3": ("Diferencia de volumen (m³)", 2),
    "P_Embalse_mm": ("Precipitación sobre el embalse (mm)", 2),
    "Area_Embalse_m2": ("Área del embalse (m²)", 2),
    "Vol_P_Embalse_m3": ("Volumen de precipitación sobre el embalse (m³)", 2),
    "Ev_Embalse_mm": ("Evaporación del embalse (mm)", 2),
    "Vol_Ev_Embalse_m3": ("Volumen evaporado (m³)", 2),
    "Vol_Demanda_m3": ("Volumen de demanda (m³)", 2),
    "Q_Demanda_m3/s": ("Caudal de demanda (m³/s)", 4),
    "Q_Total_8_Subcuencas_m3s": ("Total 8 subcuencas (m³/s)", 4),
    "Q_Embalse_m3s": ("Aporte directo al embalse (m³/s)", 4),
    "Q_Total_8_Subcuencas_Embalse_m3s": ("Total subcuencas + embalse (m³/s)", 4),
    # Evaporación y curvas del embalse
    "Ev_Linacre": ("Evaporación Linacre (mm/día)", 2),
    "Ev_KFN": ("Evaporación KFN (mm/día)", 2),
    "Cota_Embalse_m": ("Cota del embalse (m s. n. m.)", 2),
    "Q_Vertedero_m3s": ("Caudal del vertedero (m³/s)", 3),
    "Carga_H_m": ("Carga hidráulica H (m)", 3),
    "Diferencia_KFN_Linacre": ("Diferencia KFN − Linacre (mm/día)", 2),
    "Embalse_Precipitacion_mm": ("Precipitación sobre el embalse (mm/h)", 2),
    "N": ("N.º", 0),
    "Parametro": ("Parámetro", 0),
    "Valor": ("Valor", 4),
    "Unidad": ("Unidad", 0),
    "Interpretacion": ("Interpretación", 0),
    "Origen": ("Origen", 0),
    # Serie horaria de cada subcuenca (hoja Serie_Horaria)
    "P_mm": ("Precipitación (mm/h)", 2),
    "ET0_mm_h": ("Evapotranspiración de referencia ET₀ (mm/h)", 4),
    "ET_real_mm_h": ("Evapotranspiración real (mm/h)", 4),
    "ET_real_acumulada_mm": ("Evapotranspiración real acumulada (mm)", 2),
    "Area_m2": ("Área (m²)", 2),
    "Qsim_m3s": ("Caudal simulado (m³/s)", 4),
    "Qobs_m3s": ("Caudal observado (m³/s)", 4),
    "Vol_sim_m3": ("Volumen simulado (m³)", 2),
    "Vol_obs_m3": ("Volumen observado (m³)", 2),
    "Vol_sim_acumulado_m3": ("Volumen simulado acumulado (m³)", 2),
    "Vol_obs_acumulado_m3": ("Volumen observado acumulado (m³)", 2),
    "Flujo_rapido_mm_h": ("Flujo rápido (mm/h)", 4),
    "Flujo_lento_base_mm_h": ("Flujo lento o base (mm/h)", 4),
    "Escorrentia_total_mm_h": ("Escorrentía total (mm/h)", 4),
    "Percolacion_mm_h": ("Percolación (mm/h)", 4),
    "Humedad_suelo_mm": ("Humedad del suelo (mm)", 2),
    "Almacenamiento_rapido_mm": ("Almacenamiento rápido (mm)", 2),
    "Almacenamiento_lento_mm": ("Almacenamiento lento (mm)", 2),
    "Runoff_factor": ("Factor de escorrentía (–)", 4),
    "Lluvia_rapida_mm_h": ("Lluvia a flujo rápido (mm/h)", 4),
    "Lluvia_suelo_mm_h": ("Lluvia infiltrada al suelo (mm/h)", 4),
    "Exceso_saturacion_mm_h": ("Exceso por saturación (mm/h)", 4),
    "Error_Q_m3s": ("Error de caudal (m³/s)", 4),
    "Error_Vol_m3": ("Error de volumen (m³)", 2),
    "Error_Vol_acumulado_m3": ("Error de volumen acumulado (m³)", 2),
    # Resumen del modelo (hoja Resumen)
    "Subcuenca": ("Subcuenca", 0),
    "Fecha_inicio": ("Fecha de inicio", 0),
    "Fecha_fin": ("Fecha de fin", 0),
    "Registros_horarios": ("Registros horarios", 0),
    "Area_km2": ("Área (km²)", 3),
    "Precipitacion_total_mm": ("Precipitación total (mm)", 2),
    "ET0_total_mm": ("ET₀ total (mm)", 2),
    "ET_real_total_mm": ("Evapotranspiración real total (mm)", 2),
    "Escorrentia_total_mm": ("Escorrentía total (mm)", 2),
    "Q_medio_m3s": ("Caudal medio (m³/s)", 4),
    "Q_max_m3s": ("Caudal máximo (m³/s)", 4),
    "Fecha_Q_max": ("Fecha del caudal máximo", 0),
    "Q_p95_m3s": ("Caudal percentil 95 (m³/s)", 4),
    "Q_min_m3s": ("Caudal mínimo (m³/s)", 4),
    "Volumen_total_m3": ("Volumen total (m³)", 2),
    "NSE": ("NSE (–)", 3),
    "NSE_log": ("NSE logarítmico (–)", 3),
    "KGE": ("KGE (–)", 3),
    "R2": ("R² (–)", 3),
    "PBIAS_%": ("PBIAS (%)", 3),
    "RMSE_m3s": ("RMSE (m³/s)", 4),
    "MAE_m3s": ("MAE (m³/s)", 4),
    "Tipo_parametros": ("Tipo de parámetros", 0),
    "Origen_parametros": ("Origen de parámetros", 0),
    "Validacion": ("Validación", 0),
}

_PATTERNS: list[tuple[str, str, int]] = [
    (r"^Q_Subcuenca_(\d+)_m3s$", "Subcuenca {0} (m³/s)", 4),
    (r"^P_Subcuenca_(\d+)_mm$", "Subcuenca {0} (mm)", 2),
    (r"^Vol_Subcuenca_(\d+)_m3$", "Subcuenca {0} (m³)", 2),
    (r"^Qsim_Subcuenca_(\d+)_m3s$", "Simulado · Subcuenca {0} (m³/s)", 4),
    (r"^Qobs_Subcuenca_(\d+)_m3s$", "Observado · Subcuenca {0} (m³/s)", 4),
]


def _lookup(column: str) -> tuple[str, int] | None:
    if column in _FIXED:
        return _FIXED[column]
    for pattern, template, decimals in _PATTERNS:
        match = re.match(pattern, column)
        if match:
            return template.format(*match.groups()), decimals
    return None


def label(column: str) -> str:
    """Nombre legible de una columna (si no se conoce, se devuelve tal cual)."""
    found = _lookup(column)
    return found[0] if found else column


def decimals(column: str, default: int = 2) -> int:
    found = _lookup(column)
    return found[1] if found else default


def subbasin_id(column: str) -> int | None:
    """Número de subcuenca contenido en el nombre de la columna, si lo hay."""
    match = re.search(r"Subcuenca_(\d+)", column)
    return int(match.group(1)) if match else None


def column_config(df, default_decimals: int = 2) -> dict:
    """Configuración de st.dataframe con nombres legibles y decimales fijos."""
    import pandas as pd
    import streamlit as st

    config: dict = {}
    for column in df.columns:
        name = label(str(column))
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            config[column] = st.column_config.DatetimeColumn(name, format="DD/MM/YYYY HH:mm")
        elif pd.api.types.is_numeric_dtype(df[column]):
            places = decimals(str(column), default_decimals)
            config[column] = st.column_config.NumberColumn(name, format=f"%.{places}f")
        else:
            config[column] = st.column_config.TextColumn(name)
    return config
