@echo off
REM Easy start script for Dahua Camera Automation

echo ======================================\necho   Dahua Camera Automation\necho ======================================\n
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
REM === Integrated setup (replaces setup.bat and setup_autostart.bat) ===
REM 1) Ensure Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://python.org (check "Add Python to PATH") and run this file again.
    pause
    exit /b 1
)

REM 2) Create and activate virtual environment if it does not already exist
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM 3) Install/upgrade required Python packages
echo Installing required packages...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install required packages!
    pause
    exit /b 1
)

REM 4) Run interactive configuration
python interactive_setup.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Configuration failed!
    pause
    exit /b 1
)

REM 5) Offer automatic startup via Task Scheduler
choice /C YN /M "Would you like the automation to start automatically when Windows starts"
if errorlevel 2 goto :post_setup  REM user chose N

REM -- User chose Y --
set "CURRENT_DIR=%CD%"
REM Prepare updated XML with correct path
powershell -Command "(gc '%CURRENT_DIR%\dahua_camera_task.xml') -replace 'C:\\DahuaCameraAutomation', '%CURRENT_DIR%' | Out-File -encoding UTF8 '%TEMP%\dahua_task_temp.xml'"

schtasks /create /tn "DahuaCameraAutomation" /xml "%TEMP%\dahua_task_temp.xml" /f
if exist "%TEMP%\dahua_task_temp.xml" del "%TEMP%\dahua_task_temp.xml"

:post_setup
REM Setup complete, run the automation now
goto :run
REM === End integrated setup ===

:run
call run_camera_automation.bat
goto :end

:end
exit /b 0
