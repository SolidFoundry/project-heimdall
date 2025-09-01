@echo off
setlocal enabledelayedexpansion
echo ========================================
echo    Project Heimdall Server Menu
echo ========================================
echo.

:: Check if server is already running
echo Checking for existing processes on port 8003...
netstat -ano | findstr ":8003" >nul
if %errorlevel% equ 0 (
    echo Found processes using port 8003:
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8003"') do (
        set "pid=%%a"
        if not "!pid!"=="" (
            echo Process running on port 8003: !pid!
        )
    )
    echo.
    echo Do you want to stop the existing server first?
    set /p choice="Enter Y/N: "
    if /i "!choice!"=="Y" (
        call stop.bat
        timeout /t 2 >nul
    )
)

echo.
echo ========================================
echo    Select Server Type
echo ========================================
echo 1. Simple Server (FastAPI basic server)
echo 2. Main Server (Full enterprise features)
echo 3. Stop All Servers
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto start_simple
if "%choice%"=="2" goto start_main
if "%choice%"=="3" goto stop_all
if "%choice%"=="4" goto exit
echo Invalid choice
goto exit

:start_simple
echo.
echo ========================================
echo    Starting Simple Server
echo ========================================
echo.
cd /d "%~dp0"
set PYTHONPATH=src
python simple_server.py
goto exit

:start_main
echo.
echo ========================================
echo    Starting Main Server
echo ========================================
echo.
cd /d "%~dp0"
set PYTHONPATH=src
python run_server.py
goto exit

:stop_all
echo.
echo ========================================
echo    Stopping All Servers
echo ========================================
echo.
call stop.bat
goto exit

:exit
echo.
echo ========================================
echo    Operation completed
echo ========================================
echo.
pause