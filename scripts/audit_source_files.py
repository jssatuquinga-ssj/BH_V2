"""Audita la carpeta de archivos originales sin modificarla."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source_original"
OUTPUT = ROOT / "data" / "source_audit.json"

files = [path for path in SOURCE.rglob("*") if path.is_file()]
extensions = Counter(path.suffix.lower() or "[sin extensión]" for path in files)

shapefile_issues: list[str] = []
for shp in SOURCE.rglob("*.shp"):
    for extension in [".shx", ".dbf", ".prj"]:
        if not shp.with_suffix(extension).exists():
            shapefile_issues.append(str(shp.relative_to(SOURCE)) + f" sin {extension}")

report = {
    "total_archivos": len(files),
    "tamano_bytes": sum(path.stat().st_size for path in files),
    "extensiones": dict(sorted(extensions.items())),
    "problemas_shapefile": shapefile_issues,
}
OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
