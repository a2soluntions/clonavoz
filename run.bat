@echo off
title VoxStudio AI - Gerador de Voz Neural (Offline)
echo ======================================================
echo    VoxStudio AI - Sintese de Voz Neural Offline
echo ======================================================
echo.
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERRO] Ambiente virtual nao encontrado!
    pause
    exit /b
)

echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo Abrindo aplicacao web em http://localhost:8000 ...
start http://localhost:8000
python -m uvicorn server:app --host 0.0.0.0 --port 8000

pause
