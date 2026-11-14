from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


VARIABLES = {
    "Área de la subcuenca": ("Area_km2", "km²"),
    "Precipitación total": ("Precipitacion_total_mm", "mm"),
    "Caudal medio": ("Q_medio_m3s", "m³/s"),
    "Caudal máximo": ("Q_max_m3s", "m³/s"),
    "Volumen total": ("Volumen_total_m3", "m³"),
}


def _line_coordinates(geometry: dict[str, Any]) -> tuple[list[float | None], list[float | None]]:
    lons: list[float | None] = []
    lats: list[float | None] = []
    kind = geometry.get("type")
    coords = geometry.get("coordinates", [])
    if kind == "LineString":
        for lon, lat, *_ in coords:
            lons.append(lon)
            lats.append(lat)
        lons.append(None)
        lats.append(None)
    elif kind == "MultiLineString":
        for line in coords:
            a, b = _line_coordinates({"type": "LineString", "coordinates": line})
            lons.extend(a)
            lats.extend(b)
    return lons, lats


def _polygon_coordinates(geometry: dict[str, Any]) -> tuple[list[float | None], list[float | None]]:
    lons: list[float | None] = []
    lats: list[float | None] = []
    kind = geometry.get("type")
    coords = geometry.get("coordinates", [])
    polygons = [coords] if kind == "Polygon" else coords if kind == "MultiPolygon" else []
    for polygon in polygons:
        if not polygon:
            continue
        for lon, lat, *_ in polygon[0]:
            lons.append(lon)
            lats.append(lat)
        lons.append(None)
        lats.append(None)
    return lons, lats


def build_subbasin_map(
    summary: pd.DataFrame,
    subbasins_geojson: dict[str, Any],
    rivers_geojson: dict[str, Any],
    stations_geojson: dict[str, Any],
    reservoir_geojson: dict[str, Any],
    variable_label: str,
    selected_id: int,
) -> go.Figure:
    field, unit = VARIABLES[variable_label]
    data = summary.copy()

    hover_data = {
        "subcuenca_id": False,
        "Area_km2": ":.3f",
        "Precipitacion_total_mm": ":.2f",
        "Q_medio_m3s": ":.4f",
        "Q_max_m3s": ":.4f",
        "Volumen_total_m3": ":,.0f",
        "Tipo_parametros": True,
        "Origen_parametros": True,
    }

    fig = px.choropleth_map(
        data,
        geojson=subbasins_geojson,
        locations="subcuenca_id",
        featureidkey="properties.subcuenca_id",
        color=field,
        hover_name="Subcuenca",
        hover_data=hover_data,
        custom_data=["subcuenca_id"],
        labels={
            field: f"{variable_label} ({unit})",
            "Area_km2": "Área (km²)",
            "Precipitacion_total_mm": "Precipitación total (mm)",
            "Q_medio_m3s": "Caudal medio (m³/s)",
            "Q_max_m3s": "Caudal máximo (m³/s)",
            "Volumen_total_m3": "Volumen total (m³)",
            "Tipo_parametros": "Parámetros",
            "Origen_parametros": "Origen",
        },
        color_continuous_scale="Tealgrn",
        opacity=0.68,
        map_style="open-street-map",
        zoom=10.2,
        center={"lat": float(data["subcuenca_id"].map({
            int(f["properties"]["subcuenca_id"]): f["properties"].get("centroid_lat", 0)
            for f in subbasins_geojson["features"]
        }).mean()), "lon": float(data["subcuenca_id"].map({
            int(f["properties"]["subcuenca_id"]): f["properties"].get("centroid_lon", 0)
            for f in subbasins_geojson["features"]
        }).mean())},
        height=650,
    )

    if fig.data:
        fig.data[0].marker.line.width = 1.5
        fig.data[0].marker.line.color = "rgba(255,255,255,0.9)"

    # River network: only source layers 1 to 6 are present.
    river_lons: list[float | None] = []
    river_lats: list[float | None] = []
    for feature in rivers_geojson.get("features", []):
        a, b = _line_coordinates(feature["geometry"])
        river_lons.extend(a)
        river_lats.extend(b)
    fig.add_trace(go.Scattermap(
        lon=river_lons,
        lat=river_lats,
        mode="lines",
        line={"width": 1.4, "color": "#1d78a8"},
        name="Red de drenaje",
        hoverinfo="skip",
    ))

    # Reservoir polygon.
    for feature in reservoir_geojson.get("features", []):
        lons, lats = _polygon_coordinates(feature["geometry"])
        fig.add_trace(go.Scattermap(
            lon=lons,
            lat=lats,
            mode="lines",
            fill="toself",
            fillcolor="rgba(35, 176, 222, 0.60)",
            line={"width": 2.2, "color": "#e5fbff"},
            name="Embalse",
            hovertemplate="Embalse Salve Faccha<extra></extra>",
        ))

    # Monitoring stations.
    station_features = stations_geojson.get("features", [])
    fig.add_trace(go.Scattermap(
        lon=[f["geometry"]["coordinates"][0] for f in station_features],
        lat=[f["geometry"]["coordinates"][1] for f in station_features],
        mode="markers",
        marker={"size": 9, "color": "#f59e0b"},
        text=[f'{f["properties"].get("codigo", "")} · {f["properties"].get("nombre", "")}' for f in station_features],
        customdata=[f["properties"].get("categoria", "") for f in station_features],
        hovertemplate="<b>%{text}</b><br>%{customdata}<extra></extra>",
        name="Estaciones",
    ))

    # Selected subbasin outline.
    selected = next(
        (f for f in subbasins_geojson.get("features", []) if int(f["properties"]["subcuenca_id"]) == int(selected_id)),
        None,
    )
    if selected:
        lons, lats = _polygon_coordinates(selected["geometry"])
        fig.add_trace(go.Scattermap(
            lon=lons,
            lat=lats,
            mode="lines",
            line={"width": 5, "color": "#ffcf33"},
            hoverinfo="skip",
            name=f"Subcuenca {selected_id} seleccionada",
        ))

    fig.update_layout(
        margin={"l": 0, "r": 0, "t": 15, "b": 0},
        coloraxis_colorbar={"title": unit, "thickness": 13, "len": 0.55},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 0.01,
            "xanchor": "left",
            "x": 0.01,
            "bgcolor": "rgba(255,255,255,0.80)",
        },
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
