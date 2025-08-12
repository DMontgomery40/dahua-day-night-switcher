# Dahua Camera Day/Night Automation

This program automatically switches your Dahua camera between day and night modes based on sunrise and sunset times in your location.

## What You Need

1. A Dahua camera connected to your network
2. Your camera's IP address (like 192.168.1.108)
3. Your camera's username and password
4. A Windows computer that stays on

## Quick Start

1. **Download all files** to a folder on your computer (like C:\DahuaCamera)

2. **Double-click START_HERE.bat**
   - The program will guide you through setup
   - It will ask for your camera information and location
   - Everything is automatic after that!

## What the Program Does

- Switches your camera to **day mode** at sunrise
- Switches your camera to **night mode** at sunset
- Updates automatically every day
- Works with your exact location for accurate sunrise/sunset times

## First Time Setup

When you run START_HERE.bat for the first time:

1. **Install Python** (if not installed)
   - Go to https://python.org
   - Download Python
   - **IMPORTANT**: Check "Add Python to PATH" during installation

2. **Run START_HERE.bat again**
   - It will ask for:
     - Your camera's IP address
     - Your camera's username (usually "admin")
     - Your camera's password
     - Your location (like "Denver, USA" or "London, UK")

3. **That's it!** The program will handle everything else

## Running the Automation

After setup, you have two options:

**Option 1: Manual Start**
- Double-click START_HERE.bat
- Choose "Run the automation"
- Keep the window open (minimize it if you want)

**Option 2: Automatic Start** (Recommended)
- Run `setup_autostart.bat` once to create a Windows Task Scheduler entry
- The automation will then launch automatically every time you log in

## Making it Run Automatically

To make the program start automatically when Windows starts:

1. Double-click `setup_autostart.bat` and follow the prompts.
2. That's it!  You can reboot now to test, or just run `run_camera_automation.bat` once to start immediately.

## Troubleshooting

**"Python is not installed"**
- Download Python from https://python.org
- During installation, check "Add Python to PATH"

**"Cannot connect to camera"**
- Check your camera's IP address is correct
- Make sure your computer and camera are on the same network
- Verify your username and password

**"Location not found"**
- Try being more specific (add state/country)
- Examples: "New York, USA" or "Paris, France"

**Need to change settings?**
- Run START_HERE.bat
- Choose "Change settings"

## Files Included

- START_HERE.bat - Main launcher (double-click this)
- setup.bat - Installs Python packages and guides first-time setup
- setup_autostart.bat - Configures Windows to start the automation at login
- run_camera_automation.bat - Runs the automation manually
- Other files - Don't modify these

## Support

The program creates a log file (dahua_daynight.log) that tracks what it's doing. If something goes wrong, this file will have information about the problem.