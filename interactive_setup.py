#!/usr/bin/env python3
# pyright: reportMissingImports=false, reportMissingTypeStubs=false
# pyright: reportMissingImports=false
# pyright: reportMissingTypeStubs=false
# mypy: ignore-missing-imports
# pylint: disable=import-error
"""
Interactive Setup Script for Dahua Camera Day/Night Switcher
This script helps non-technical users configure their camera settings
"""

import json
import os
import sys
import getpass
import importlib

CONFIG_FILE = "camera_config.json"

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print a nice header"""
    clear_screen()
    print("=" * 60)
    print("  Dahua Camera Day/Night Automation Setup")
    print("=" * 60)
    print()

def get_camera_ip():
    """Get camera IP address from user"""
    print("\nStep 1: Camera IP Address")
    print("-" * 30)
    print("Your camera's IP address is a number that looks like this:")
    print("Example: 192.168.1.108")
    print("\nYou can usually find this in your camera's manual or")
    print("in your router's connected devices list.")
    print()
    
    while True:
        ip = input("Enter your camera's IP address: ").strip()
        
        # Basic IP validation
        parts = ip.split('.')
        if len(parts) == 4:
            try:
                # Check if all parts are valid numbers
                for part in parts:
                    num = int(part)
                    if num < 0 or num > 255:
                        raise ValueError
                return ip
            except ValueError:
                pass
        
        print("That doesn't look like a valid IP address.")
        print("Please enter something like: 192.168.1.108")
        print()

def get_camera_credentials():
    """Get camera username and password"""
    print("\nStep 2: Camera Login Information")
    print("-" * 30)
    print("You need the username and password you use to log into your camera.")
    print("The default username is often 'admin'.")
    print()
    
    username = input("Enter your camera username (press Enter for 'admin'): ").strip()
    if not username:
        username = "admin"
    
    print("\nNow enter your camera password.")
    print("Note: The password won't show on screen as you type (this is normal).")
    password = getpass.getpass("Enter your camera password: ")
    
    return username, password

def test_camera_connection(ip, username, password):
    """Test connection to the camera"""
    print("\nTesting connection to your camera...")
    
    try:
        # Import here to avoid top-level linter errors for third-party packages
        import requests  # type: ignore[reportMissingImports]
        from requests.auth import HTTPDigestAuth  # type: ignore[reportMissingImports]

        url = f"http://{ip}/cgi-bin/magicBox.cgi?action=getSystemInfo"
        response = requests.get(url, auth=HTTPDigestAuth(username, password), timeout=10)
        
        if response.status_code == 200:
            print("Success! Connected to your camera.")
            return True
        elif response.status_code == 401:
            print("Error: Wrong username or password.")
            return False
        else:
            print(f"Error: Could not connect to camera (Error code: {response.status_code})")
            return False
    except requests.exceptions.Timeout:
        print("Error: Connection timed out. Please check the IP address.")
        return False
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to camera. Please check:")
        print("  - The IP address is correct")
        print("  - The camera is turned on")
        print("  - Your computer is on the same network as the camera")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def get_location():
    """Get user's location and convert to coordinates"""
    print("\nStep 3: Your Location")
    print("-" * 30)
    print("The system needs to know your location to calculate sunrise")
    print("and sunset times accurately.")
    print()
    print("Enter your location as: City, Country")
    print("Examples:")
    print("  - Denver, USA")
    print("  - London, UK")
    print("  - Sydney, Australia")
    print("  - Toronto, Canada")
    print()
    
    while True:
        location_input = input("Enter your location: ").strip()
        
        if not location_input:
            print("Please enter a location.")
            continue
        
        print(f"\nSearching for '{location_input}'...")
        
        try:
            # Use Nominatim geocoder (dynamic import to avoid type stub issues)
            geocoders_mod = importlib.import_module("geopy.geocoders")
            exc_mod = importlib.import_module("geopy.exc")
            Nominatim = getattr(geocoders_mod, "Nominatim")
            GeocoderTimedOut = getattr(exc_mod, "GeocoderTimedOut")
            GeocoderServiceError = getattr(exc_mod, "GeocoderServiceError")

            geolocator = Nominatim(user_agent="dahua-camera-switcher/1.0")
            location = geolocator.geocode(location_input, timeout=10)
            
            if location:
                print(f"\nFound: {location.address}")
                confirm = input("Is this correct? (yes/no): ").strip().lower()
                
                if confirm in ['yes', 'y']:
                    # Try to determine timezone
                    timezone = get_timezone_for_location(location.latitude, location.longitude)
                    
                    return {
                        'name': location_input,
                        'address': location.address,
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'timezone': timezone
                    }
                else:
                    print("\nLet's try again with a different location.")
            else:
                print(f"Sorry, I couldn't find '{location_input}'.")
                print("Try being more specific, like adding the state or country.")
                print()
        
        except GeocoderTimedOut:
            print("The location search timed out. Please try again.")
        except GeocoderServiceError:
            print("There was an error with the location service. Please try again.")
        except Exception as e:
            print(f"Error finding location: {str(e)}")
            print("Please try again.")

def get_timezone_for_location(latitude, longitude):
    """Try to determine timezone for given coordinates"""
    try:
        # Use timezonefinder if available, otherwise fall back to common zones
        try:
            tz_mod = importlib.import_module("timezonefinder")
            TimezoneFinder = getattr(tz_mod, "TimezoneFinder")
            tf = TimezoneFinder()
            tz_name = tf.timezone_at(lat=latitude, lng=longitude)
            if tz_name:
                return tz_name
        except Exception:
            pass
        
        # Fallback: ask user
        print("\nI need to know your timezone for accurate sunrise/sunset times.")
        print("Common timezones:")
        print("  - America/New_York (Eastern Time)")
        print("  - America/Chicago (Central Time)")
        print("  - America/Denver (Mountain Time)")
        print("  - America/Los_Angeles (Pacific Time)")
        print("  - Europe/London")
        print("  - Europe/Paris")
        print("  - Asia/Tokyo")
        print("  - Australia/Sydney")
        print()
        
        while True:
            tz_input = input("Enter your timezone (or press Enter to use UTC): ").strip()
            
            if not tz_input:
                return 'UTC'
            
            # Check if it's a valid timezone
            try:
                pytz = importlib.import_module("pytz")
                pytz.timezone(tz_input)
                return tz_input
            except Exception:
                print(f"'{tz_input}' is not a valid timezone. Please try again.")
                
    except Exception:
        return 'UTC'

def get_advanced_settings():
    """Get optional advanced settings"""
    print("\nStep 4: Advanced Settings (Optional)")
    print("-" * 30)
    print("These settings are optional. Press Enter to use the defaults.")
    print()
    
    # Camera port
    port_input = input("Camera port (default is 80): ").strip()
    port = 80
    if port_input:
        try:
            port = int(port_input)
        except ValueError:
            print("Invalid port number. Using default (80).")
            port = 80
    
    # Sunrise/sunset offsets
    print("\nYou can adjust when the camera switches modes relative to")
    print("sunrise and sunset. Enter the number of minutes:")
    print("  - Positive numbers = switch later")
    print("  - Negative numbers = switch earlier")
    print("  - Press Enter for no offset")
    print()
    
    sunrise_offset = 0
    sunrise_input = input("Minutes after sunrise to switch to day mode (default 0): ").strip()
    if sunrise_input:
        try:
            sunrise_offset = int(sunrise_input)
        except ValueError:
            print("Invalid number. Using default (0).")
    
    sunset_offset = 0
    sunset_input = input("Minutes after sunset to switch to night mode (default 0): ").strip()
    if sunset_input:
        try:
            sunset_offset = int(sunset_input)
        except ValueError:
            print("Invalid number. Using default (0).")
    
    return {
        'port': port,
        'sunrise_offset': sunrise_offset,
        'sunset_offset': sunset_offset
    }

def save_configuration(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving configuration: {str(e)}")
        return False

def main():
    """Main setup function"""
    print_header()
    
    print("Welcome! This setup will help you configure your Dahua camera")
    print("to automatically switch between day and night modes based on")
    print("sunrise and sunset times in your location.")
    print()
    print("Let's get started!")
    print()
    
    input("Press Enter to continue...")
    
    # Check if config already exists
    if os.path.exists(CONFIG_FILE):
        print_header()
        print("An existing configuration was found.")
        overwrite = input("Do you want to create a new configuration? (yes/no): ").strip().lower()
        if overwrite not in ['yes', 'y']:
            print("Setup cancelled.")
            return
    
    # Get camera IP
    print_header()
    camera_ip = get_camera_ip()
    
    # Get credentials
    print_header()
    username, password = get_camera_credentials()
    
    # Test connection
    while not test_camera_connection(camera_ip, username, password):
        print()
        retry = input("Would you like to try again? (yes/no): ").strip().lower()
        if retry not in ['yes', 'y']:
            print("Setup cancelled.")
            return
        
        print_header()
        print("Let's try again...")
        camera_ip = get_camera_ip()
        print_header()
        username, password = get_camera_credentials()
    
    # Get location
    print_header()
    location = get_location()
    
    # Get advanced settings
    print_header()
    advanced = get_advanced_settings()
    
    # Create configuration
    config = {
        'camera': {
            'ip': camera_ip,
            'port': advanced['port'],
            'username': username,
            'password': password
        },
        'location': location,
        'offsets': {
            'sunrise': advanced['sunrise_offset'],
            'sunset': advanced['sunset_offset']
        },
        'profiles': {
            'day': 0,
            'night': 1
        }
    }
    
    # Save configuration
    print_header()
    print("Saving your configuration...")
    
    if save_configuration(config):
        print("Configuration saved successfully!")
        print()
        print("Setup is complete! Your camera will now automatically")
        print("switch between day and night modes based on sunrise")
        print("and sunset times in your location.")
        print()
        print("To start the automation, run: run_camera_automation.bat")
        print()
    else:
        print("Failed to save configuration.")
        return 1
    
    input("Press Enter to exit...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
