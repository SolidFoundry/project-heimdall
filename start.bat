@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo ========================================
echo    Starting Project Heimdall Server
echo ========================================
echo.

cd /d "%~dp0"

if exist .venv\Scripts\python.exe (
    call .venv\Scripts\activate
    set PYTHON=.venv\Scripts\python.exe
    echo Virtual environment activated
) else (
    echo Virtual environment not found, creating...
    python -m venv .venv
    call .venv\Scripts\activate
    set PYTHON=.venv\Scripts\python.exe
    echo Virtual environment created and activated
)

set PYTHONPATH=src

if not exist logs mkdir logs

echo Checking dependencies...
%PYTHON% -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    %PYTHON% -m pip install fastapi uvicorn sqlalchemy asyncpg pydantic python-dotenv openai >nul 2>&1
)

echo ========================================
echo Starting server on http://localhost:8003
echo ========================================
echo Press Ctrl+C to stop
echo ========================================

%PYTHON% run_server.py

echo.
echo Server stopped
pause