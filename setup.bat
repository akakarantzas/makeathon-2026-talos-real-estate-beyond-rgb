@echo off
setlocal

cd /d "%~dp0"

echo Checking Python...
where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Install Python, then run setup.bat again.
    pause
    exit /b 1
)

echo Checking npm...
where npm >nul 2>nul
if errorlevel 1 (
    echo npm was not found. Install Node.js, then run setup.bat again.
    pause
    exit /b 1
)

echo.
echo Installing Python dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Python dependency installation failed.
    pause
    exit /b 1
)

echo.
echo Installing frontend dependencies...
pushd frontend
call npm install
if errorlevel 1 (
    popd
    echo Frontend dependency installation failed.
    pause
    exit /b 1
)
popd

echo.
echo Setup complete.
echo Run run_app.bat to start Terrasset.
pause
