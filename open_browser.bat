@echo off
echo Starting Project Heimdall...
echo ================================================
echo.
echo 请选择要访问的页面:
echo 1) 项目首页 (推荐)
echo 2) 企业级推荐系统
echo 3) 测试平台
echo 4) API文档
echo 5) 健康检查
echo.
set /p choice="请输入选项 (1-5): "

if "%choice%"=="1" (
    start http://localhost:8002/
    echo 正在打开项目首页...
) else if "%choice%"=="2" (
    start http://localhost:8002/enterprise
    echo 正在打开企业级推荐系统...
) else if "%choice%"=="3" (
    start http://localhost:8002/test
    echo 正在打开测试平台...
) else if "%choice%"=="4" (
    start http://localhost:8002/docs
    echo 正在打开API文档...
) else if "%choice%"=="5" (
    start http://localhost:8002/health
    echo 正在打开健康检查...
) else (
    echo 无效选项，请重新运行脚本
    pause
    exit /b
)

echo.
echo 服务器地址: http://localhost:8002
echo ================================================
echo.
echo 可用页面:
echo - 项目首页: http://localhost:8002/
echo - 企业级推荐系统: http://localhost:8002/enterprise
echo - 测试平台: http://localhost:8002/test
echo - API文档: http://localhost:8002/docs
echo - 健康检查: http://localhost:8002/health
echo.
pause