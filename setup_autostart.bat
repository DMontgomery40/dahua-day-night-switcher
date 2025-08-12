@echo off
REM Setup automatic startup for Dahua Camera Automation

echo ======================================
echo   Setup Automatic Startup
echo ======================================
echo.
echo This will make the camera automation start
echo automatically when Windows starts.
echo.

REM Get current directory
set CURRENT_DIR=%CD%

echo Current installation directory: %CURRENT_DIR%
echo.

choice /C YN /M "Do you want to set up automatic startup"
if errorlevel 2 (
    echo.
    echo Setup cancelled.
    pause
    exit /b 0
)

echo.
echo Creating scheduled task...

REM Update the XML file with the correct path
powershell -Command "(gc '%CURRENT_DIR%\dahua_camera_task.xml') -replace 'C:\\DahuaCameraAutomation', '%CURRENT_DIR%' | Out-File -encoding UTF8 '%TEMP%\dahua_task_temp.xml'"

REM Import the task
schtasks /create /tn "DahuaCameraAutomation" /xml "%TEMP%\dahua_task_temp.xml" /f

if %errorlevel% equ 0 (
    echo.
    echo Success! The camera automation will now start automatically
    echo when Windows starts.
    echo.
    echo To test it now, you can:
    echo   1. Restart your computer
    echo   2. Run run_camera_automation.bat manually
    echo.
    echo To disable automatic startup later:
    echo   - Open Task Scheduler
    echo   - Find "DahuaCameraAutomation"
    echo   - Right-click and select "Disable" or "Delete"
) else (
    echo.
    echo ERROR: Failed to create scheduled task.
    echo.
    echo Alternative method:
    echo   1. Press Windows+R
    echo   2. Type: shell:startup
    echo   3. Press Enter
    echo   4. Copy run_camera_automation.bat to that folder
)

REM Clean up temp file
if exist "%TEMP%\dahua_task_temp.xml" del "%TEMP%\dahua_task_temp.xml"

echo.
pause
