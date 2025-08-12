@echo off
REM Reset/cleanup script for Dahua Camera Automation

echo ======================================
|echo   _____       _                      _      
echo  |  __ \\     | |                    | |     
echo  | |  \\/ __ _| |__  _ __ ___   __ _ | | ___ 
echo  | | __ / _` | '_ \\| '_ ` _ \\ / _` || |/ __|
echo  | |_\\ \\ (_| | |_) | | | | | | (_| || |\\__ \\
echo   \\____/ \\__,_|_.__/|_| |_| |_|\\__,_||_|\\___/
echo        Reset Camera Automation Settings
echo ======================================
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
