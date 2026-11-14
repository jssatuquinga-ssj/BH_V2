# Visor hidrológico del embalse Salve Faccha

Aplicación desarrollada en **Streamlit** para visualizar los resultados previamente calculados del embalse Salve Faccha y sus ocho subcuencas. El proyecto incluye mapas interactivos, series horarias y diarias, balance hídrico, curvas del embalse, métricas de validación, información técnica y una galería de imágenes.

## 1. Qué contiene el proyecto

- Los archivos originales del ZIP se conservan en `data/source_original/`.
- La aplicación utiliza archivos optimizados en `data/processed/`.
- Los shapefiles originales permanecen en EPSG:32717.
- Las copias usadas por el mapa están en GeoJSON y EPSG:4326.
- La aplicación no vuelve a ejecutar el modelo hidrológico.
- Las subcuencas 7 y 8 no muestran redes de ríos porque esas capas no fueron incluidas en los archivos fuente.
- Las subcuencas 1 y 6 se identifican como calibraciones independientes.
- Las subcuencas 2, 3, 4, 5, 7 y 8 utilizan parámetros transferidos desde la subcuenca 1.

## 2. Estructura principal

```text
embalse_salve_faccha_streamlit/
├── app.py                         # Punto de entrada de Streamlit
├── requirements.txt               # Dependencias de ejecución
├── .streamlit/config.toml         # Apariencia y configuración
├── views/                          # Páginas de la aplicación
├── src/                            # Carga de datos, mapas, gráficos y utilidades
├── config/                         # Configuración de subcuencas y variables
├── content/                        # Textos informativos en Markdown
├── assets/                         # Logos, imágenes, miniaturas, CSS y SVG
├── data/
│   ├── source_original/            # Archivos originales conservados
│   └── processed/                  # CSV y GeoJSON utilizados por la aplicación
├── scripts/                        # Auditoría y regeneración de datos web
└── tests/                          # Pruebas de integridad
```

## 3. Abrir el proyecto en Visual Studio Code

1. Descomprime el ZIP del repositorio en una ubicación fácil de identificar.
2. Abre Visual Studio Code.
3. Selecciona **Archivo > Abrir carpeta**.
4. Elige la carpeta `embalse_salve_faccha_streamlit`.
5. Abre una terminal integrada mediante **Terminal > Nueva terminal**.

La terminal debe mostrar como ubicación la raíz del proyecto, donde se encuentran `app.py` y `requirements.txt`.

## Inicio rápido opcional en Windows

También puedes hacer doble clic en `INICIAR_APP.bat`. En el primer uso, el archivo crea `.venv`, instala las dependencias y abre Streamlit. En los usos posteriores reutiliza el mismo entorno.

## 4. Crear el entorno virtual en Windows

Ejecuta estos comandos desde la terminal de Visual Studio Code:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Cuando el entorno esté activo, la terminal mostrará `(.venv)` al inicio de la línea.

Si PowerShell impide activar el entorno, ejecuta una sola vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Cierra y abre nuevamente la terminal antes de activar `.venv`.

## 5. Ejecutar la aplicación

```powershell
python -m streamlit run app.py
```

Streamlit abrirá normalmente la dirección:

```text
http://localhost:8501
```

Para detener la aplicación, presiona `Ctrl + C` en la terminal.

Para evitar que Windows utilice otra instalación global de Streamlit, se recomienda ejecutar siempre `python -m streamlit run app.py` con el entorno `(.venv)` activo.

### Error `TypeError: '<=' not supported between instances of 'str' and 'int'`

Este error aparece cuando el código usa la sintaxis moderna `width="stretch"`, pero la aplicación se ejecuta con una versión anterior de Streamlit instalada fuera del entorno virtual. Esta versión del proyecto utiliza una sintaxis compatible y el iniciador de Windows obliga a ejecutar Streamlit desde `.venv`. Si el error reaparece, elimina la carpeta `.venv`, vuelve a ejecutar `INICIAR_APP.bat` o repite la instalación indicada en la sección 4.

## 6. Vistas disponibles

### Inicio

Presenta el resumen del sistema, la animación preliminar de la forma real del embalse y el criterio de calibración.

### Subcuencas

- Mapa con las ocho subcuencas.
- Información emergente al pasar el cursor.
- Selección mediante el mapa o un control desplegable.
- Redes de drenaje para las subcuencas 1 a 6.
- Estaciones climatológicas, hidrométricas y pluviométricas.
- Caudal, precipitación, volumen, parámetros y morfometría.
- Comparación observado-simulado para las subcuencas 1 y 6.

### Resultados

- Comparación entre subcuencas.
- Series horarias y diarias.
- Métricas de validación.
- Tablas y descargas de resultados.

### Embalse

- Cota y volumen diario.
- Curva área-cota-volumen.
- Curva de descarga del vertedero.
- Componentes del balance hídrico.
- Evaporación diaria.

### Información técnica

- Antecedentes y características.
- Metodología y limitaciones.
- Galería fotográfica.
- Detalles técnicos.
- Descarga del documento informativo original.

## 7. Verificar el proyecto

Con el entorno virtual activo, instala `pytest` y ejecuta las pruebas:

```powershell
pip install pytest
pytest -q
```

También puedes realizar una auditoría de los archivos originales:

```powershell
python scripts/audit_source_files.py
```

## 8. Regenerar los archivos procesados

Este paso **no es necesario para ejecutar la aplicación**. Solo debe realizarse cuando se sustituyan los Excel o shapefiles originales.

```powershell
pip install -r scripts/requirements-processing.txt
python scripts/prepare_web_data.py
```

El script convierte formatos, limpia rutas antiguas y prepara los datos web. No recalcula el modelo hidrológico.

## 9. Crear el repositorio en GitHub

Después de revisar la aplicación localmente:

```powershell
git init
git add .
git commit -m "Versión inicial del visor Salve Faccha"
git branch -M main
git remote add origin URL_DE_TU_REPOSITORIO
git push -u origin main
```

Sustituye `URL_DE_TU_REPOSITORIO` por la dirección del repositorio vacío creado en GitHub.

Los archivos individuales del proyecto están por debajo del límite normal de GitHub. No es necesario utilizar Git LFS en esta versión.

## 10. Publicar en Streamlit Community Cloud

1. Ingresa a Streamlit Community Cloud con tu cuenta de GitHub.
2. Crea una nueva aplicación.
3. Selecciona el repositorio y la rama `main`.
4. Define `app.py` como archivo principal.
5. Selecciona Python 3.12 en la configuración avanzada.
6. Ejecuta el despliegue.

Las rutas son relativas a la carpeta del repositorio, por lo que no es necesario modificar rutas al pasar de Visual Studio Code a GitHub o Streamlit Community Cloud.

## 11. Solución de problemas frecuentes

### `python` no se reconoce

Instala Python y marca la opción **Add Python to PATH** durante la instalación.

### `streamlit` no se reconoce

Activa `.venv` e instala nuevamente las dependencias:

```powershell
python -m pip install -r requirements.txt
```

### El mapa no muestra el fondo cartográfico

La capa base de OpenStreetMap requiere conexión a internet. Las subcuencas y demás capas del proyecto permanecen disponibles desde los GeoJSON locales.

### La aplicación no encuentra un archivo

Comprueba que abriste la carpeta raíz completa y que no moviste de forma independiente `app.py`, `data`, `assets`, `src` o `views`.

## 12. Criterio de rutas

Las rutas se construyen con `pathlib` desde la ubicación real del proyecto:

```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
```

Por esta razón, el proyecto es portable y conserva su funcionamiento al copiarlo, clonarlo desde GitHub o desplegarlo en Streamlit.
