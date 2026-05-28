@echo off
REM ============================================================
REM  PhysicsMotionAnalyzer — Lanzador para Windows (doble clic)
REM  Se posiciona automaticamente en la carpeta del proyecto.
REM ============================================================
title PhysicsMotionAnalyzer
cd /d "%~dp0"

echo.
echo ================================================
echo   PhysicsMotionAnalyzer - Iniciando...
echo ================================================
echo   Carpeta: %~dp0
echo.

REM Verificar que las dependencias estan instaladas
python -c "import cv2, numpy, matplotlib, PIL, scipy" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [!] Faltan dependencias. Instalando...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo [ERROR] No se pudieron instalar las dependencias.
        pause
        exit /b 1
    )
)

REM Intentar con "py" primero, sino "python"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3 main.py
) else (
    python main.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] La aplicacion finalizo con errores.
    pause
)
