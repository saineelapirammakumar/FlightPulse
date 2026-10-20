@echo off
cd /d "%~dp0backend"
if not exist .venv\Scripts\python.exe (
  echo Creating Python virtual environment...
  python -m venv .venv
  if errorlevel 1 goto error
)
echo Installing/checking backend packages...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Initializing demo data if database is empty...
.venv\Scripts\python.exe scripts\seed_demo.py
if errorlevel 1 goto error
echo Training the educational demo model...
.venv\Scripts\python.exe ml\train.py
if errorlevel 1 goto error
echo Starting FlightPulse API at http://127.0.0.1:8000/docs
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
goto end
:error
echo.
echo Setup failed. Check the error above, and confirm Python 3.10+ is installed.
pause
:end
