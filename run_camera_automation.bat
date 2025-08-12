@echo off
REM Dahua Camera Day/Night Automation Runner
REM This script runs the camera automation

echo ======================================\necho  Dahua Camera Automation \necho ======================================\n
echo.

REM Check if configuration exists
if not exist camera_config.json (
    echo ERROR: No configuration found!
    echo.
    echo Please run "START_HERE.bat" first to configure your camera.
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

REM Run the automation script
echo Starting camera automation...
echo.
echo The automation is now running and will:
echo   - Switch to DAY mode at sunrise
echo   - Switch to NIGHT mode at sunset
echo   - Update daily based on your location
echo.
echo Press Ctrl+C to stop the automation.
echo.

python dahua_daynight.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: The automation stopped unexpectedly!
    echo Please check the log file (dahua_daynight.log) for details.
    echo.
    echo If you need to reconfigure, run "START_HERE.bat"
    echo.
    pause
)

pause