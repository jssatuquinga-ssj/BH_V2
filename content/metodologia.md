# Metodología y alcance del visor

La aplicación presenta resultados previamente calculados. No ejecuta nuevamente el modelo lluvia-escorrentía ni modifica los archivos Excel originales.

## Parámetros del modelo

- **Subcuenca 1:** calibración independiente.
- **Subcuencas 2, 3, 4 y 5:** parámetros transferidos desde la subcuenca 1.
- **Subcuenca 6:** calibración independiente.
- **Subcuencas 7 y 8:** parámetros transferidos desde la subcuenca 1.

## Validación

Las subcuencas 1 y 6 disponen de caudales observados y métricas de validación en los archivos suministrados. Las demás subcuencas se muestran como resultados simulados con parámetros transferidos y no deben interpretarse como calibraciones independientes.

## Información geográfica

La fuente original utiliza **WGS 84 / UTM zona 17 Sur (EPSG:32717)**. Para la representación cartográfica en el navegador se generaron copias en **WGS 84 geográfico (EPSG:4326)**. Los shapefiles originales permanecen sin modificaciones.

Las subcuencas 7 y 8 no poseen capas de ríos en el material entregado. El visor no crea redes de drenaje artificiales para esas zonas.
