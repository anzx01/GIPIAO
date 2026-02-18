@echo off
echo ========================================
echo   AI Quant Research Hub - 后端启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.10+
    pause
    exit /b 1
)
python --version

echo.
echo [2/4] 检查依赖包...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [警告] FastAPI未安装，正在安装依赖...
    pip install -r requirements.txt
)

echo.
echo [3/4] 检查配置文件...
if not exist ".env" (
    echo [警告] .env文件不存在，从.env.example复制...
    copy .env.example .env
)

echo.
echo [4/4] 启动后端服务...
echo 服务地址: http://127.0.0.1:8001
echo API文档: http://127.0.0.1:8001/docs
echo 健康检查: http://127.0.0.1:8001/health
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8001
