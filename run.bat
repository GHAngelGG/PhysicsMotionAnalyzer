@echo off
REM ============================================================
REM  PhysicsMotionAnalyzer - Lanzador para Windows (doble clic).
REM  Intenta usar "py" (Python Launcher) y, si no existe, "python".
REM ============================================================
cd /d "%~dp0"

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3 main.py
) else (
    python main.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] La aplicacion finalizo con errores.
    echo Si faltan dependencias, ejecute:
    echo     pip install -r requirements.txt
    pause
)
