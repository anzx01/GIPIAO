@echo off
echo ========================================
echo   Requesting admin rights to start backend
echo ========================================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Already running with admin rights
    goto :start
) else (
    echo [WARN] Admin rights required
    echo Requesting admin rights...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:start
cd /d "%~dp0"

echo.
echo [1/3] Checking Python environment...
C:\Python314\python.exe --version
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

echo.
echo [2/3] Checking port 8001...
netstat -ano | findstr :8001 >nul
if not errorlevel 1 (
    echo [WARN] Port 8001 is in use, cleaning up...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 >nul
)

echo.
echo [3/3] Starting backend service...
echo Service URL: http://127.0.0.1:8001
echo Health check: http://127.0.0.1:8001/health
echo.
echo Press Ctrl+C to stop the service
echo ========================================
echo.

C:\Python314\python.exe -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8001

pause
