@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo ========================================
echo    Stopping Project Heimdall Server
echo ========================================
echo.

echo Stopping Python processes...
taskkill /F /IM python.exe >nul 2>&1

echo Checking ports 8001, 8002, 8003...
for %%p in (8001 8002 8003) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p"') do (
        set pid=%%a
        if not "!pid!"=="" (
            echo Stopping process !pid! on port %%p
            taskkill /F /PID !pid! >nul 2>&1
        )
    )
)

timeout /t 2 >nul

echo.
echo ========================================
echo Server stopped successfully
echo ========================================
echo.
pause