@echo off
REM Reset/cleanup script for Dahua Camera Automation

echo ======================================\necho   :)  Reset Camera Automation Settings\necho ======================================\n
echo.
echo This will delete your saved camera settings.
echo You will need to run START_HERE.bat again.
echo.

choice /C YN /M "Are you sure you want to reset all settings"
if errorlevel 2 (
    echo.
    echo Reset cancelled.
    pause
    exit /b 0
)

echo.
echo Deleting configuration...

if exist camera_config.json del camera_config.json
if exist dahua_daynight.log del dahua_daynight.log

echo.
echo Settings have been reset.
echo Run START_HERE.bat to configure again.
echo.
pause
