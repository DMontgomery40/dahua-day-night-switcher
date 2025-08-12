@echo off
REM Dahua Camera Day/Night Automation Setup Script
REM This script installs Python dependencies and sets up the automation

echo ======================================
echo   Dahua Camera Automation Setup
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Python is installed.
echo.

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available!
    echo Please ensure Python is properly installed with pip.
    echo.
    pause
    exit /b 1
)

REM Create virtual environment (optional but recommended)
echo Creating Python virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo WARNING: Could not create virtual environment.
    echo Continuing with global Python installation...
    echo.
) else (
    echo Virtual environment created.
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

REM Install required packages
echo Installing required packages...
echo This may take a few minutes...
echo.

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install required packages!
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo All packages installed successfully!
echo.

REM Check if configuration exists
if exist camera_config.json (
    echo Configuration file found.
    echo.
    choice /C YN /M "Do you want to reconfigure your camera settings"
    if errorlevel 2 goto :skip_config
)

REM Run interactive setup
echo.
echo Starting interactive configuration...
echo.
python interactive_setup.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Configuration failed!
    echo Please try again.
    echo.
    pause
    exit /b 1
)

:skip_config
echo.
echo ======================================
echo   Setup Complete!
echo ======================================
echo.
echo Your camera automation is now configured.
echo.
echo To start the automation:
echo   1. Double-click "run_camera_automation.bat"
echo   2. (Recommended) Run "setup_autostart.bat" to configure automatic startup at login
echo.
echo The automation will:
echo   - Switch to DAY mode at sunrise
echo   - Switch to NIGHT mode at sunset
echo   - Update daily based on your location
echo.
pause