@echo off
setlocal

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Run setup.bat after installing Python.
    pause
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo npm was not found. Run setup.bat after installing Node.js.
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo Frontend dependencies are missing. Run setup.bat first.
    pause
    exit /b 1
)

echo Starting Terrasset backend...
start "Terrasset Backend" cmd /k "cd /d ""%~dp0"" && python -m uvicorn Backend_code.adapters.api:app --reload --port 8001"

echo Starting Terrasset frontend...
start "Terrasset Frontend" cmd /k "cd /d ""%~dp0frontend"" && npm run dev"

echo Waiting for the frontend to become available...
for /l %%i in (1,1,20) do (
    powershell -NoProfile -Command "try { $response = Invoke-WebRequest -UseBasicParsing 'http://localhost:5174' -TimeoutSec 1; if ($response.StatusCode -eq 200) { exit 0 } } catch { exit 1 }"
    if not errorlevel 1 goto open_browser
    timeout /t 1 /nobreak >nul
)

:open_browser
echo Opening Terrasset in your browser...
start "" "http://localhost:5174"

echo Terrasset is starting.
echo Close the backend and frontend terminal windows to stop the app.
endlocal
