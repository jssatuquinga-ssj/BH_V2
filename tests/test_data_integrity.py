import json

import pandas as pd

from src.paths import GIS_DIR, RESERVOIR_DIR, SUMMARY_DIR, TIME_SERIES_DIR


def test_subbasin_summary() -> None:
    df = pd.read_csv(SUMMARY_DIR / "resumen_subcuencas.csv")
    assert len(df) == 8
    assert set(df["Subcuenca"]) == {f"Subcuenca_{i}" for i in range(1, 9)}
    assert set(df.loc[df["Tipo_parametros"] == "Calibración independiente", "Subcuenca"]) == {
        "Subcuenca_1",
        "Subcuenca_6",
    }


def test_hourly_series_have_expected_length() -> None:
    for filename in ["caudales_horarios.csv", "precipitacion_horaria.csv", "volumenes_horarios.csv"]:
        df = pd.read_csv(TIME_SERIES_DIR / filename)
        assert len(df) == 2963


def test_geographic_layers() -> None:
    subbasins = json.loads((GIS_DIR / "subcuencas.geojson").read_text(encoding="utf-8"))
    rivers = json.loads((GIS_DIR / "rios.geojson").read_text(encoding="utf-8"))
    assert len(subbasins["features"]) == 8
    river_ids = {int(feature["properties"]["subcuenca_id"]) for feature in rivers["features"]}
    assert river_ids == {1, 2, 3, 4, 5, 6}


def test_reservoir_series() -> None:
    levels = pd.read_csv(RESERVOIR_DIR / "niveles_embalse.csv")
    assert len(levels) == 124
    assert levels["Cota_msnm"].notna().all()
