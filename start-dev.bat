@echo off
setlocal

set "ROOT=%~dp0"
set "FRONTEND=%ROOT%frontend"
set "BACKEND_URL=http://127.0.0.1:8001"
set "FRONTEND_URL=http://localhost:3000"

cd /d "%ROOT%"

echo ========================================
echo   AI Quant Research Hub - Dev Startup
echo ========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found. Please install Python 3.10+ first.
    pause
    exit /b 1
)

where pnpm >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pnpm was not found. Please install pnpm first.
    echo         Example: npm install -g pnpm
    pause
    exit /b 1
)

if not exist "%ROOT%.env" (
    if exist "%ROOT%.env.example" (
        echo [INFO] Creating .env from .env.example
        copy "%ROOT%.env.example" "%ROOT%.env" >nul
    )
)

if not exist "%FRONTEND%\.env.local" (
    if exist "%FRONTEND%\.env.example" (
        echo [INFO] Creating frontend\.env.local from frontend\.env.example
        copy "%FRONTEND%\.env.example" "%FRONTEND%\.env.local" >nul
    )
)

if not exist "%FRONTEND%\node_modules" (
    echo [INFO] Installing frontend dependencies...
    pushd "%FRONTEND%"
    call pnpm install
    if errorlevel 1 (
        popd
        echo [ERROR] Frontend dependency installation failed.
        pause
        exit /b 1
    )
    popd
)

echo [INFO] Starting backend in a new window...
start "AIQRH Backend" /D "%ROOT%" cmd /k "python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8001"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   Services
echo   Frontend: %FRONTEND_URL%
echo   Backend : %BACKEND_URL%
echo   API docs: %BACKEND_URL%/docs
echo ========================================
echo.
echo [INFO] Starting frontend in this window...
echo [INFO] Press Ctrl+C to stop frontend. Close the backend window to stop backend.
echo.

pushd "%FRONTEND%"
call pnpm dev
set "EXIT_CODE=%ERRORLEVEL%"
popd

exit /b %EXIT_CODE%
