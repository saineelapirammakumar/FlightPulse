@echo off
cd /d "%~dp0frontend"
where npm >nul 2>nul
if errorlevel 1 (
  echo Node.js LTS is not installed or npm is not on PATH.
  echo Install Node.js 20 LTS, then reopen this file.
  pause
  exit /b 1
)
if not exist node_modules (
  echo Installing frontend packages. This needs internet access the first time...
  call npm install
  if errorlevel 1 goto error
)
echo Starting FlightPulse frontend...
call npm run dev
 goto end
:error
echo Frontend setup failed. Check your Node.js installation and internet connection.
pause
:end
