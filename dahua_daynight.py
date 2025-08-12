#!/usr/bin/env python3
# pyright: ignore-all
# mypy: ignore-missing-imports
# pylint: disable=import-error
"""
Dahua Camera Day/Night Mode Automation Script
Automatically switches between day and night modes based on sunrise/sunset times
"""

import requests
from requests.auth import HTTPDigestAuth
import json
import time
from datetime import datetime, timedelta
import logging
import sys
import os
import importlib
from types import SimpleNamespace

# Configuration file
CONFIG_FILE = "camera_config.json"

# Logging Configuration
LOG_FILE = "dahua_daynight.log"
LOG_LEVEL = logging.INFO

def load_configuration():
    """Load configuration from file"""
    if not os.path.exists(CONFIG_FILE):
        print("ERROR: Configuration file not found!")
        print("Please run 'interactive_setup.py' first to configure your camera.")
        sys.exit(1)
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        # Extract configuration values
        camera_config = config['camera']
        location_config = config['location']
        offsets = config.get('offsets', {'sunrise': 0, 'sunset': 0})
        profiles = config.get('profiles', {'day': 0, 'night': 1})
        
        # Store location info as plain dict (converted to namespace later)
        location = {
            'name': location_config['name'],
            'timezone': location_config['timezone'],
            'latitude': location_config['latitude'],
            'longitude': location_config['longitude']
        }
        
        return {
            'camera_ip': camera_config['ip'],
            'camera_port': camera_config.get('port', 80),
            'username': camera_config['username'],
            'password': camera_config['password'],
            'location': location,
            'sunrise_offset': offsets['sunrise'],
            'sunset_offset': offsets['sunset'],
            'day_profile': profiles['day'],
            'night_profile': profiles['night']
        }
    
    except Exception as e:
        print(f"ERROR: Failed to load configuration: {str(e)}")
        print("Please run 'interactive_setup.py' to reconfigure.")
        sys.exit(1)

# Load configuration at startup
config = load_configuration()

# Extract configuration values
CAMERA_IP = config['camera_ip']
CAMERA_PORT = config['camera_port']
USERNAME = config['username']
PASSWORD = config['password']
# Turn location dict into SimpleNamespace so we can use dot notation
LOCATION = SimpleNamespace(**config['location'])
SUNRISE_OFFSET = config['sunrise_offset']
SUNSET_OFFSET = config['sunset_offset']
DAY_PROFILE = config['day_profile']
NIGHT_PROFILE = config['night_profile']

# Setup logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DahuaCameraController:
    """Controller for Dahua camera day/night mode switching"""
    
    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.base_url = f"http://{ip}:{port}"
        self.auth = HTTPDigestAuth(username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        
    def test_connection(self):
        """Test connection to the camera"""
        try:
            url = f"{self.base_url}/cgi-bin/magicBox.cgi?action=getSystemInfo"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                logger.info("Successfully connected to camera")
                return True
            else:
                logger.error(f"Failed to connect: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def get_current_profile(self):
        """Get the current video profile"""
        try:
            # This endpoint may vary by camera model
            url = f"{self.base_url}/cgi-bin/configManager.cgi?action=getConfig&name=VideoInMode"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                # Parse the response to get current mode
                content = response.text
                logger.debug(f"Current profile response: {content}")
                return content
            return None
        except Exception as e:
            logger.error(f"Error getting current profile: {e}")
            return None
    
    def switch_to_day_mode(self):
        """Switch camera to day mode"""
        try:
            # Method 1: Switch video profile
            url = f"{self.base_url}/cgi-bin/configManager.cgi?action=setConfig&VideoInMode[0].Config[0]={DAY_PROFILE}"
            response = self.session.get(url, timeout=10)
            
            # Method 2: Alternative - Set IR cut filter (if supported)
            ir_url = f"{self.base_url}/cgi-bin/configManager.cgi?action=setConfig&VideoInOptions[0].NightOptions.SwitchMode=0"
            self.session.get(ir_url, timeout=10)
            
            if response.status_code == 200:
                logger.info("Successfully switched to DAY mode")
                return True
            else:
                logger.error(f"Failed to switch to day mode: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error switching to day mode: {e}")
            return False
    
    def switch_to_night_mode(self):
        """Switch camera to night mode"""
        try:
            # Method 1: Switch video profile
            url = f"{self.base_url}/cgi-bin/configManager.cgi?action=setConfig&VideoInMode[0].Config[0]={NIGHT_PROFILE}"
            response = self.session.get(url, timeout=10)
            
            # Method 2: Alternative - Set IR cut filter (if supported)
            ir_url = f"{self.base_url}/cgi-bin/configManager.cgi?action=setConfig&VideoInOptions[0].NightOptions.SwitchMode=1"
            self.session.get(ir_url, timeout=10)
            
            if response.status_code == 200:
                logger.info("Successfully switched to NIGHT mode")
                return True
            else:
                logger.error(f"Failed to switch to night mode: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error switching to night mode: {e}")
            return False


def get_sun_times():
    """Get today's sunrise and sunset times for Denver"""
    pytz = importlib.import_module("pytz")
    tz = pytz.timezone(LOCATION.timezone)
    today = datetime.now(tz).date()

    suntime_mod = importlib.import_module("suntime")
    Sun = getattr(suntime_mod, "Sun")
    SunTimeException = getattr(suntime_mod, "SunTimeException")
    sun = Sun(LOCATION.latitude, LOCATION.longitude)
    try:
        sunrise = sun.get_local_sunrise_time(today) + timedelta(minutes=SUNRISE_OFFSET)
        sunset = sun.get_local_sunset_time(today) + timedelta(minutes=SUNSET_OFFSET)
    except SunTimeException as exc:
        logger.error(f"Error calculating sunrise/sunset: {exc}")
        # Fallback: don't adjust
        sunrise = tz.localize(datetime(today.year, today.month, today.day, 6, 0))
        sunset = tz.localize(datetime(today.year, today.month, today.day, 18, 0))
    
    return sunrise, sunset


def check_and_switch_mode(camera):
    """Check current time and switch camera mode if necessary"""
    pytz = importlib.import_module("pytz")
    tz = pytz.timezone(LOCATION.timezone)
    now = datetime.now(tz)
    sunrise, sunset = get_sun_times()
    
    logger.debug(f"Current time: {now}")
    logger.debug(f"Sunrise: {sunrise}, Sunset: {sunset}")
    
    # Determine if it should be day or night mode
    if sunrise <= now < sunset:
        # It's daytime
        logger.info(f"It's daytime (between {sunrise.strftime('%H:%M')} and {sunset.strftime('%H:%M')})")
        camera.switch_to_day_mode()
    else:
        # It's nighttime
        logger.info(f"It's nighttime (before {sunrise.strftime('%H:%M')} or after {sunset.strftime('%H:%M')})")
        camera.switch_to_night_mode()


def schedule_daily_switches(camera):
    """Schedule the camera switches for today"""
    sunrise, sunset = get_sun_times()
    pytz = importlib.import_module("pytz")
    tz = pytz.timezone(LOCATION.timezone)
    now = datetime.now(tz)
    
    # Clear existing scheduled jobs
    schedule = importlib.import_module("schedule")
    schedule.clear()
    
    # Schedule sunrise switch
    sunrise_time = sunrise.strftime("%H:%M")
    if now < sunrise:
        schedule.every().day.at(sunrise_time).do(camera.switch_to_day_mode)
        logger.info(f"Scheduled switch to DAY mode at {sunrise_time}")
    
    # Schedule sunset switch
    sunset_time = sunset.strftime("%H:%M")
    if now < sunset:
        schedule.every().day.at(sunset_time).do(camera.switch_to_night_mode)
        logger.info(f"Scheduled switch to NIGHT mode at {sunset_time}")
    
    # Schedule daily recalculation at midnight
    schedule.every().day.at("00:01").do(lambda: schedule_daily_switches(camera))


def main():
    """Main function to run the camera controller"""
    logger.info("=" * 50)
    logger.info("Starting Dahua Camera Day/Night Automation")
    logger.info(f"Location: {LOCATION.name}")
    logger.info(f"Camera: {CAMERA_IP}:{CAMERA_PORT}")
    logger.info("=" * 50)
    
    # Initialize camera controller
    camera = DahuaCameraController(CAMERA_IP, CAMERA_PORT, USERNAME, PASSWORD)
    
    # Test connection
    if not camera.test_connection():
        logger.error("Failed to connect to camera. Please check settings.")
        sys.exit(1)
    
    # Get and display sun times
    sunrise, sunset = get_sun_times()
    logger.info(f"Today's sunrise: {sunrise.strftime('%H:%M:%S %Z')}")
    logger.info(f"Today's sunset: {sunset.strftime('%H:%M:%S %Z')}")
    
    # Initial mode check and switch
    check_and_switch_mode(camera)
    
    # Schedule daily switches
    schedule_daily_switches(camera)
    
    # Run the scheduler
    logger.info("Scheduler started. Press Ctrl+C to stop.")
    try:
        while True:
            schedule = importlib.import_module("schedule")
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()