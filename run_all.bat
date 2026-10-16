@echo off
echo ========================================================
echo Launching GitMatch Fullstack System...
echo ========================================================

set PYTHON_CMD=python
if exist "%~dp0venv\Scripts\python.exe" (
    set PYTHON_CMD="%~dp0venv\Scripts\python.exe"
)

start "GitMatch Backend API" cmd /k "cd /d "%~dp0" && if exist "%~dp0venv\Scripts\activate.bat" (call "%~dp0venv\Scripts\activate.bat") && %PYTHON_CMD% -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul
start "GitMatch Frontend UI" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================================
echo Services started!
echo Frontend UI: http://localhost:5173
echo Backend API Docs: http://localhost:8000/docs
echo ========================================================
