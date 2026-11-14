@echo off
REM ============================================================
REM  SUBIR_CAMBIOS.bat - Sube los cambios de esta carpeta a GitHub (BH_V2)
REM  Uso: doble clic. Equivale a: git add . / git commit / git push
REM ============================================================
cd /d "%~dp0"
echo === Limpiando archivos desktop.ini dentro de .git (los crea la sincronizacion de Windows/Drive) ===
for /r ".git" %%f in (desktop.ini) do if exist "%%f" del /f /q /a "%%f"
set "GIT=git"
where git >/dev/null 2>/dev/null || set "GIT=C:\Program Files\Git\cmd\git.exe"
if not "%GIT%"=="git" if not exist "%GIT%" (
  echo ERROR: no se encontro Git en esta computadora.
  pause
  exit /b 1
)
echo.
echo === Revisando que esta carpeta apunte al repositorio BH_V2 ===
"%GIT%" remote get-url origin
"%GIT%" remote get-url origin | findstr /i "BH_V2" >nul
if errorlevel 1 (
  echo.
  echo ERROR: esta carpeta NO esta enlazada a BH_V2. No se subio nada.
  pause
  exit /b 1
)
set "MSG=%~1"
if "%MSG%"=="" set "MSG=Actualizacion del visor %DATE% %TIME:~0,5%"
echo.
echo === Preparando archivos (git add) ===
"%GIT%" add .
echo.
echo === Guardando cambios (git commit) ===
"%GIT%" commit -m "%MSG%"
echo.
echo === Subiendo a GitHub (git push) ===
"%GIT%" push
if errorlevel 1 (
  echo.
  echo *** HUBO UN ERROR AL SUBIR. Toma una captura de esta ventana. ***
) else (
  echo.
  echo *** LISTO. Los cambios estan en GitHub. Streamlit se actualiza en 1-2 minutos. ***
)
echo.
pause
