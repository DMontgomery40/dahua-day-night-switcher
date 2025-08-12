@echo off
REM Easy start script for Dahua Camera Automation

echo ======================================
echo   Welcome to Dahua Camera Automation
echo ======================================
echo.
echo This program will make your camera automatically
echo switch between day and night modes based on
echo sunrise and sunset times in your location.
echo.

REM Check if already configured
if exist camera_config.json (
    echo Your camera is already configured!
    echo.
    echo What would you like to do?
    echo   1. Run the automation
    echo   2. Change settings
    echo   3. Exit
    echo.
    choice /C 123 /N /M "Enter your choice (1, 2, or 3): "
    
    if errorlevel 3 exit /b 0
    if errorlevel 2 goto :setup
    if errorlevel 1 goto :run
) else (
    echo Let's set up your camera first...
    echo.
    pause
    goto :setup
)

:setup
call setup.bat
goto :end

:run
call run_camera_automation.bat
goto :end

:end
exit /b 0
