@echo off
echo ========================================
echo   AI Quant Research Platform - Auto Start
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Starting backend service...
echo.

:: Start backend (background)
start /B "" C:\Python314\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8003

:: Wait for backend to start
echo Waiting for backend service to start...
timeout /t 5 /nobreak >nul

:: Check whether backend started successfully
curl -s http://127.0.0.1:8003/health >nul 2>&1
if errorlevel 1 (
    echo [WARN] Backend may need more time to start...
    timeout /t 3 /nobreak >nul
)

echo [OK] Backend service started: http://127.0.0.1:8003
echo.

echo [2/3] Starting frontend service...
cd frontend

:: Check whether dependencies are installed
if not exist "node_modules" (
    echo [INFO] First run detected, installing dependencies...
    call pnpm install
)

echo.
echo [3/3] Starting frontend service...
echo.
echo ========================================
echo   Service URLs:
echo   - Frontend: http://localhost:3000
echo   - Backend:  http://127.0.0.1:8003
echo ========================================
echo.

:: Start frontend
call pnpm dev

pause
