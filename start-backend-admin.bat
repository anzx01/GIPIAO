@echo off
echo ========================================
echo   请求管理员权限启动后端服务
echo ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] 已获得管理员权限
    goto :start
) else (
    echo [警告] 需要管理员权限
    echo 正在请求管理员权限...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:start
cd /d "%~dp0"

echo.
echo [1/3] 检查Python环境...
C:\Python314\python.exe --version
if errorlevel 1 (
    echo [错误] Python未找到
    pause
    exit /b 1
)

echo.
echo [2/3] 检查端口8001...
netstat -ano | findstr :8001 >nul
if not errorlevel 1 (
    echo [警告] 端口8001被占用，正在清理...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 >nul
)

echo.
echo [3/3] 启动后端服务...
echo 服务地址: http://127.0.0.1:8001
echo 健康检查: http://127.0.0.1:8001/health
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

C:\Python314\python.exe -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8001

pause
