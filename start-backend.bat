@echo off
echo ========================================
echo   AI Quant Research Hub - Backend Startup
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+ first.
    pause
    exit /b 1
)
python --version

echo.
echo [2/4] Checking dependencies...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [WARN] FastAPI not installed, installing dependencies...
    pip install -r requirements.txt
)

echo.
echo [3/4] Checking configuration file...
if not exist ".env" (
    echo [WARN] .env file not found, copying from .env.example...
    copy .env.example .env
)

echo.
echo [4/4] Starting backend service...
echo Service URL: http://127.0.0.1:8001
echo API docs: http://127.0.0.1:8001/docs
echo Health check: http://127.0.0.1:8001/health
echo.
echo Press Ctrl+C to stop the service
echo ========================================
echo.

python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8001
