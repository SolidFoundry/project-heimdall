@echo off
echo ========================================
echo 启动 Project Heimdall 服务器
echo ========================================

echo.
echo 1. 检查端口占用情况...
netstat -ano | findstr ":8001" >nul
if %errorlevel% == 0 (
    echo 发现端口8001被占用，正在停止相关进程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001"') do (
        echo 正在停止进程: %%a
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

echo.
echo 2. 设置环境变量...
set PYTHONPATH=src

echo.
echo 3. 启动服务器...
echo 服务器将在以下地址启动:
echo   - 主页: http://localhost:8001/
echo   - 企业级界面: http://localhost:8001/enterprise
echo   - 测试平台: http://localhost:8001/test
echo   - API文档: http://localhost:8001/docs
echo   - 健康检查: http://localhost:8001/health
echo.

python src/heimdall/main.py

pause