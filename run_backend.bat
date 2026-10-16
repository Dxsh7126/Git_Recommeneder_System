@echo off
echo ========================================================
echo Starting GitMatch FastAPI Backend (Port 8000)...
echo ========================================================
cd /d "%~dp0"
if exist ".\venv\Scripts\activate.bat" (
    call .\venv\Scripts\activate.bat
)
if exist ".\venv\Scripts\python.exe" (
    .\venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
) else (
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
)
pause
