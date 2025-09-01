@echo off
setlocal enabledelayedexpansion
echo ========================================
echo    Project Heimdall Server Stop Script
echo ========================================
echo.

echo Stopping Python processes related to Project Heimdall...
:: Stop python processes running run_server.py, simple_server.py, or heimdall
taskkill /F /FI "WINDOWTITLE eq run_server.py*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq simple_server.py*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq heimdall*" >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1

echo Checking port 8003 (main port)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8003"') do (
    set "pid=%%a"
    if not "!pid!"=="" (
        echo Stopping process: !pid!
        taskkill /F /PID !pid! >nul 2>&1
    )
)

echo Checking port 8001 (legacy port)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001"') do (
    set "pid=%%a"
    if not "!pid!"=="" (
        echo Stopping process: !pid!
        taskkill /F /PID !pid! >nul 2>&1
    )
)

echo Checking port 8002 (legacy port)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8002"') do (
    set "pid=%%a"
    if not "!pid!"=="" (
        echo Stopping process: !pid!
        taskkill /F /PID !pid! >nul 2>&1
    )
)

echo Waiting for processes to stop...
timeout /t 3 >nul

echo Checking if ports are free...
netstat -ano | findstr ":8003" >nul
if %errorlevel% equ 0 (
    echo Warning: Port 8003 still in use
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8003"') do (
        set "pid=%%a"
        echo Process still running on port 8003: !pid!
    )
) else (
    echo Port 8003 is free
)

netstat -ano | findstr ":8001" >nul
if %errorlevel% equ 0 (
    echo Warning: Port 8001 still in use
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001"') do (
        set "pid=%%a"
        echo Process still running on port 8001: !pid!
    )
) else (
    echo Port 8001 is free
)

netstat -ano | findstr ":8002" >nul
if %errorlevel% equ 0 (
    echo Warning: Port 8002 still in use
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8002"') do (
        set "pid=%%a"
        echo Process still running on port 8002: !pid!
    )
) else (
    echo Port 8002 is free
)

echo.
echo Cleaning up temporary files...
if exist logs\*.tmp (
    del /q logs\*.tmp
    echo Temporary files cleaned
)

echo.
echo ========================================
echo    Stop operation completed
echo ========================================
echo.
echo Project Heimdall Server has been stopped
echo.
pause