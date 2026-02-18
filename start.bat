@echo off
chcp 65001 >nul
echo ========================================
echo   AI量化研究平台 - 自动启动
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 启动后端服务...
echo.

:: 启动后端（后台运行）
start /B "" C:\Python314\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8003

:: 等待后端启动
echo 等待后端服务启动...
timeout /t 5 /nobreak >nul

:: 检查后端是否启动成功
curl -s http://127.0.0.1:8003/health >nul 2>&1
if errorlevel 1 (
    echo [警告] 后端启动可能需要更多时间...
    timeout /t 3 /nobreak >nul
)

echo [OK] 后端服务已启动: http://127.0.0.1:8003
echo.

echo [2/3] 启动前端服务...
cd frontend

:: 检查是否安装了依赖
if not exist "node_modules" (
    echo [提示] 首次运行，正在安装依赖...
    call pnpm install
)

echo.
echo [3/3] 前端服务启动中...
echo.
echo ========================================
echo   服务地址:
echo   - 前端: http://localhost:3000
echo   - 后端: http://127.0.0.1:8003
echo ========================================
echo.

:: 启动前端
call pnpm dev

pause
