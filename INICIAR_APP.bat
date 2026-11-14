@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no se encuentra en PATH.
    echo Instala Python 3.12 o una version compatible y vuelve a intentarlo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    python -m venv .venv
    if errorlevel 1 goto :error
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 goto :error
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

".venv\Scripts\python.exe" -m streamlit run app.py
exit /b 0

:error
echo.
echo No fue posible iniciar la aplicacion. Revisa el mensaje anterior.
pause
exit /b 1
