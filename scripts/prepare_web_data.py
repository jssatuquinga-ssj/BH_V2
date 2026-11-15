"""Regenera los archivos web a partir de los documentos originales.

Este script NO ejecuta el modelo hidrológico. Únicamente convierte resultados ya
calculados (Excel y shapefiles) a CSV y GeoJSON. La aplicación funciona con los
archivos procesados incluidos, por lo que solo es necesario ejecutarlo cuando se
reemplacen las fuentes originales.
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import make_valid

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source_original"
PROCESSED = ROOT / "data" / "processed"
SUMMARY = PROCESSED / "summaries"
TIME = PROCESSED / "time_series"
RESERVOIR = PROCESSED / "reservoir"
GIS = PROCESSED / "gis"
for folder in [SUMMARY, TIME, RESERVOIR, GIS]:
    folder.mkdir(parents=True, exist_ok=True)


def save_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, encoding="utf-8-sig")


# Consolidated hourly results.
consolidated = SOURCE / "RESULTADOS/Resumen_General_Modelo_Mejorado_8Subcuencas.xlsx"
summary = pd.read_excel(consolidated, sheet_name="Resumen_Subcuencas")
summary["subcuenca_id"] = summary["Subcuenca"].str.extract(r"(\d+)").astype(int)
summary["Tipo_parametros"] = summary["subcuenca_id"].map(
    lambda value: "Calibración independiente" if value in (1, 6) else "Parámetros transferidos"
)
summary["Origen_parametros"] = summary["subcuenca_id"].map(
    lambda value: f"Subcuenca {value}" if value in (1, 6) else "Subcuenca 1"
)
summary["Validacion"] = summary["subcuenca_id"].map(
    lambda value: "Con caudal observado" if value in (1, 6) else "Sin caudal observado"
)
save_csv(summary.drop(columns="subcuenca_id"), SUMMARY / "resumen_subcuencas.csv")
save_csv(pd.read_excel(consolidated, sheet_name="Resumen_Sistema"), SUMMARY / "resumen_sistema.csv")

for sheet, filename in [
    ("Caudales_Horarios", "caudales_horarios.csv"),
    ("Volumenes_Horarios", "volumenes_horarios.csv"),
    ("Precipitacion_Horaria", "precipitacion_horaria.csv"),
]:
    save_csv(pd.read_excel(consolidated, sheet_name=sheet), TIME / filename)

control = pd.read_excel(consolidated, sheet_name="Control_Insumos")
route_columns = [column for column in control.columns if str(column).startswith("Ruta_")]
save_csv(control.drop(columns=route_columns), SUMMARY / "control_insumos.csv")

# Calibration parameters and observed series.
model_files = {
    1: SOURCE / "CUENCA SALVE FACCHA/Subcuenca_1/Resultado_Mod_Subcuenca_1/Resultados_Modelo_Mejorado_Subcuenca_1.xlsx",
    6: SOURCE / "CUENCA SALVE FACCHA/Subcuenca_6/Resultado_Mod_Subcuenca_6/Resultados_Modelo_Mejorado_Subcuenca_6.xlsx",
}
base_parameters = {
    sid: pd.read_excel(path, sheet_name="Parametros").set_index("Parametro")["Valor"].to_dict()
    for sid, path in model_files.items()
}
parameter_rows = []
for sid in range(1, 9):
    origin = 6 if sid == 6 else 1
    for parameter, value in base_parameters[origin].items():
        parameter_rows.append({
            "Subcuenca": f"Subcuenca_{sid}",
            "Parametro": parameter,
            "Valor": value,
            "Tipo_parametros": "Calibración independiente" if sid in (1, 6) else "Parámetros transferidos",
            "Origen_parametros": f"Subcuenca {origin}",
        })
save_csv(pd.DataFrame(parameter_rows), SUMMARY / "parametros_modelo.csv")

metric_frames = []
series_frames = {}
for sid, path in model_files.items():
    metric = pd.read_excel(path, sheet_name="Metricas_Validacion")
    metric.insert(0, "Subcuenca", f"Subcuenca_{sid}")
    metric_frames.append(metric)
    series_frames[sid] = pd.read_excel(path, sheet_name="Serie_Horaria")[["Fecha", "Qsim_m3s", "Qobs_m3s"]]
save_csv(pd.concat(metric_frames, ignore_index=True), SUMMARY / "metricas_validacion.csv")
observed = series_frames[1].rename(columns={"Qsim_m3s": "Qsim_Subcuenca_1_m3s", "Qobs_m3s": "Qobs_Subcuenca_1_m3s"})
observed = observed.merge(
    series_frames[6].rename(columns={"Qsim_m3s": "Qsim_Subcuenca_6_m3s", "Qobs_m3s": "Qobs_Subcuenca_6_m3s"}),
    on="Fecha",
)
save_csv(observed, TIME / "caudales_observados_simulados.csv")

# Daily results and reservoir balance.
daily = SOURCE / "RESULTADOS/Resumen_General_Modelo_Diario_BH.xlsx"
for sheet, filename in [
    ("Precipitacion_Diaria", "precipitacion_diaria.csv"),
    ("Caudales_Diarios", "caudales_diarios.csv"),
    ("Volumen_Diario", "volumen_diario.csv"),
]:
    save_csv(pd.read_excel(daily, sheet_name=sheet), TIME / filename)
balance = pd.read_excel(daily, sheet_name="Balance_Hídrico", header=1)
# La columna 16 (volumen de precipitación sobre el embalse) repite el nombre
# "Vol_Embalse_m3" en el Excel; se renombra para que la web la reconozca.
balance_columns = list(balance.columns)
balance_columns[15] = "Vol_P_Embalse_m3"
balance.columns = balance_columns
save_csv(balance, TIME / "balance_hidrico_diario.csv")
save_csv(
    pd.read_excel(SOURCE / "RESULTADOS/Parametros_climatologicos_diarios.xlsx", sheet_name="Parametros_diarios", skiprows=[1]),
    TIME / "parametros_climatologicos_diarios.csv",
)

# Reservoir curves and series.
save_csv(
    pd.read_excel(SOURCE / "CUENCA SALVE FACCHA/Embalse/Curva A-C-V/Curva_ACV_Embalse_Grafica.xlsx", sheet_name="Curva_ACV_Embalse_Grafica"),
    RESERVOIR / "curva_area_cota_volumen.csv",
)
save_csv(
    pd.read_excel(SOURCE / "RESULTADOS/Curva_Descarga_Vertedero_Lateral.xlsx", sheet_name="Curva_descarga"),
    RESERVOIR / "curva_descarga_vertedero.csv",
)
save_csv(
    pd.read_excel(SOURCE / "CUENCA SALVE FACCHA/Embalse/Evaporacion/Datos_Evaporacion_Embalse_Linacre_KFN.xlsx"),
    RESERVOIR / "evaporacion_diaria.csv",
)
save_csv(
    pd.read_excel(SOURCE / "CUENCA SALVE FACCHA/Embalse/Precipitacion/Embalse_Precipitacion_mm.xlsx"),
    RESERVOIR / "precipitacion_embalse_horaria.csv",
)

levels = pd.read_excel(SOURCE / "CUENCA SALVE FACCHA/Embalse/Niveles de Embalse/Nivel_Embalse_124_dias.xlsx")
month_numbers = {"DICIEMBRE": 12, "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4}
levels["Mes"] = levels["Mes"].ffill().str.upper().map(month_numbers)
levels["Año"] = levels["Mes"].map(lambda value: 2018 if value == 12 else 2019)
levels["Fecha"] = pd.to_datetime(dict(year=levels["Año"], month=levels["Mes"], day=levels["Día"]))
levels = levels.rename(columns={"Cota\nmsnm": "Cota_msnm", "Volúmen\nm3": "Volumen_m3"})
save_csv(levels[["Fecha", "Cota_msnm", "Volumen_m3"]], RESERVOIR / "niveles_embalse.csv")

# Resultados detallados del modelo por subcuenca (hojas Serie_Horaria y Resumen).
SUBBASIN_RESULTS = PROCESSED / "subcuencas"
SUBBASIN_RESULTS.mkdir(parents=True, exist_ok=True)
model_summaries = []
for sid in range(1, 9):
    path = SOURCE / f"CUENCA SALVE FACCHA/Subcuenca_{sid}/Resultado_Mod_Subcuenca_{sid}/Resultados_Modelo_Mejorado_Subcuenca_{sid}.xlsx"
    save_csv(pd.read_excel(path, sheet_name="Serie_Horaria"), SUBBASIN_RESULTS / f"serie_horaria_subcuenca_{sid}.csv")
    model_summaries.append(pd.read_excel(path, sheet_name="Resumen"))
save_csv(pd.concat(model_summaries, ignore_index=True), SUBBASIN_RESULTS / "resumen_modelo_subcuencas.csv")

# Morphometry.
morphometry = []
for sid in range(1, 9):
    path = SOURCE / f"CUENCA SALVE FACCHA/Subcuenca_{sid}/Morfometria_Subcuenca_{sid}/Morfometria_Subcuenca_{sid}.xlsx"
    frame = pd.read_excel(path)
    frame.insert(0, "Subcuenca", f"Subcuenca_{sid}")
    frame.columns = ["Subcuenca", "Parametro", "Valor", "Unidad", "Interpretacion"]
    morphometry.append(frame)
save_csv(pd.concat(morphometry, ignore_index=True), SUMMARY / "morfometria_subcuencas.csv")

# Web geographic layers. Original shapefiles remain unchanged.
gis_source = SOURCE / "CUENCA SALVE FACCHA"
subbasins = []
for sid in range(1, 9):
    frame = gpd.read_file(gis_source / f"Subcuenca_{sid}/Shape_Subcuenca_{sid}/Subcuenca_{sid}.shp")
    frame["geometry"] = frame.geometry.apply(make_valid).simplify(1.5, preserve_topology=True)
    record = summary.loc[summary["subcuenca_id"] == sid].iloc[0]
    frame["subcuenca_id"] = sid
    frame["nombre"] = f"Subcuenca {sid}"
    for column in ["Area_km2", "Precipitacion_total_mm", "Q_medio_m3s", "Q_max_m3s", "Volumen_total_m3", "Tipo_parametros", "Origen_parametros", "Validacion"]:
        frame[column] = record[column]
    frame["red_rios"] = sid <= 6
    subbasins.append(frame)
subbasins = gpd.GeoDataFrame(pd.concat(subbasins, ignore_index=True), crs=subbasins[0].crs).to_crs(4326)
centroids = subbasins.to_crs(32717).geometry.centroid.to_crs(4326)
subbasins["centroid_lon"] = centroids.x
subbasins["centroid_lat"] = centroids.y
GIS.joinpath("subcuencas.geojson").write_text(subbasins.to_json(drop_id=True, ensure_ascii=False), encoding="utf-8")

reservoir = gpd.read_file(gis_source / "Embalse/Shape_Embalse/Embalse.shp")
reservoir["geometry"] = reservoir.geometry.apply(make_valid).simplify(1.0, preserve_topology=True)
GIS.joinpath("embalse.geojson").write_text(reservoir.to_crs(4326).to_json(drop_id=True, ensure_ascii=False), encoding="utf-8")

rivers = []
for sid in range(1, 7):
    frame = gpd.read_file(gis_source / f"Subcuenca_{sid}/Shape_Subcuenca_{sid}/Rio_Subcuenca_{sid}.shp")
    frame["subcuenca_id"] = sid
    frame["geometry"] = frame.geometry.simplify(2.0, preserve_topology=True)
    rivers.append(frame)
rivers = gpd.GeoDataFrame(pd.concat(rivers, ignore_index=True), crs=rivers[0].crs).to_crs(4326)
GIS.joinpath("rios.geojson").write_text(rivers.to_json(drop_id=True, ensure_ascii=False), encoding="utf-8")

stations = []
for filename, category in [
    ("Estaciones_Climatologicas.shp", "Climatológica"),
    ("Estaciones_Hidrometricas.shp", "Hidrométrica"),
    ("Estaciones_Pluviometricas.shp", "Pluviométrica"),
]:
    frame = gpd.read_file(gis_source / "Estaciones" / filename)
    frame["categoria"] = category
    stations.append(frame)
stations = gpd.GeoDataFrame(pd.concat(stations, ignore_index=True), crs=stations[0].crs).to_crs(4326)
GIS.joinpath("estaciones.geojson").write_text(stations.to_json(drop_id=True, ensure_ascii=False), encoding="utf-8")

bathymetry = gpd.read_file(gis_source / "Embalse/Shape_Embalse/Batimetria.shp")
bathymetry["geometry"] = bathymetry.geometry.simplify(3.0, preserve_topology=True)
GIS.joinpath("batimetria.geojson").write_text(bathymetry.to_crs(4326).to_json(drop_id=True, ensure_ascii=False), encoding="utf-8")

print("Archivos procesados actualizados correctamente.")
