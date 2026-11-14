from src.paths import ASSETS_DIR, GIS_DIR, PROCESSED_DIR, SOURCE_DIR


def test_required_directories_exist() -> None:
    assert SOURCE_DIR.is_dir()
    assert PROCESSED_DIR.is_dir()
    assert GIS_DIR.is_dir()
    assert ASSETS_DIR.is_dir()
