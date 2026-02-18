@echo off
cd /d "%~dp0"

echo Starting backend...
start /B "" C:\Python314\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8003

timeout /t 5 /nobreak >nul

echo Backend started at http://127.0.0.1:8003
echo.
echo Starting frontend...

cd frontend
call pnpm dev

pause
