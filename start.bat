@echo off
setlocal enabledelayedexpansion
echo ========================================
echo    Project Heimdall Server Start Script
echo ========================================
echo.

:: Check for existing processes on port 8003
echo Checking for existing processes on port 8003...
netstat -ano | findstr ":8003" >nul
if %errorlevel% equ 0 (
    echo Found processes using port 8003, stopping them...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8003"') do (
        set "pid=%%a"
        if not "!pid!"=="" (
            echo Stopping process: !pid!
            taskkill /F /PID !pid! >nul 2>&1
        )
    )
    timeout /t 2 >nul
)

:: Activate virtual environment
echo Activating virtual environment...
cd /d "%~dp0"
call conda deactivate >nul 2>&1
if exist .venv\Scripts\activate (
    call .venv\Scripts\activate
    echo Virtual environment activated successfully
) else (
    echo Virtual environment not found, using system Python
)

:: Set environment variables
echo Setting environment variables...
set PYTHONPATH=src

:: Check if .env file exists
if exist .env (
    echo Loading environment variables from .env file...
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        set "%%a=%%b"
    )
)

:: Create logs directory if it doesn't exist
if not exist logs (
    echo Creating logs directory...
    mkdir logs
)

:: Start server
echo ========================================
echo    Starting Project Heimdall Server
echo ========================================
echo Server URL: http://127.0.0.1:8003
echo Enterprise Interface: http://127.0.0.1:8003/enterprise
echo API Docs: http://127.0.0.1:8003/docs
echo Health Check: http://127.0.0.1:8003/health
echo.
echo Features:
echo - [OK] AI Intent Analysis (Qwen Turbo)
echo - [OK] Hybrid Recommendation Engine
echo - [OK] Database Session Storage
echo - [OK] Enterprise Monitoring Dashboard
echo - [OK] Structured Logging
echo - [OK] Request ID Tracking
echo - [OK] User Behavior Analysis
echo.
echo Press Ctrl+C to stop server
echo ========================================

python run_server.py

echo.
echo Server stopped
pause