from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SOURCE_DIR = DATA_DIR / "source_original"
PROCESSED_DIR = DATA_DIR / "processed"
GIS_DIR = PROCESSED_DIR / "gis"
TIME_SERIES_DIR = PROCESSED_DIR / "time_series"
SUMMARY_DIR = PROCESSED_DIR / "summaries"
RESERVOIR_DIR = PROCESSED_DIR / "reservoir"
ASSETS_DIR = PROJECT_ROOT / "assets"
CONTENT_DIR = PROJECT_ROOT / "content"
CONFIG_DIR = PROJECT_ROOT / "config"
