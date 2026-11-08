@echo off
title LibraSync - Automated Launcher
echo ===================================================
echo           LibraSync Platform Launcher
echo   Intelligent RFID-Enabled Library Management
echo ===================================================
echo.

cd /d "%~dp0"

echo [1/2] Starting FastAPI Backend on http://localhost:8000 ...
start "LibraSync Backend (FastAPI)" cmd /k "cd backend && .\venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Starting React Vite Frontend on http://localhost:5173 ...
start "LibraSync Frontend (Vite)" cmd /k "cd frontend && npm run dev"

timeout /t 4 /nobreak >nul

echo.
echo ===================================================
echo LibraSync is now running!
echo Frontend:      http://localhost:5173
echo Backend Docs:  http://localhost:8000/docs
echo Presentation:  "%~dp0presentation\index.html"
echo ===================================================
echo.
pause

