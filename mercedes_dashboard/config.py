"""
Configuration and constants
"""

from enum import IntEnum
from dataclasses import dataclass

# Display settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
FPS = 60

# ESP32-CAM Configuration
ESP32_CAM_IP = "192.168.4.1"
ESP32_CAM_PORT = 80
ESP32_CAM_STREAM_URL = f"http://{ESP32_CAM_IP}:81/stream"
ESP32_CAM_SNAPSHOT_URL = f"http://{ESP32_CAM_IP}/capture"

# Reverse camera trigger
REVERSE_CAMERA_TRIGGER = True

# Window states - explicit integer values for QStackedWidget compatibility
class WindowState(IntEnum):
    MAIN_MENU = 0
    DASHBOARD = 1
    NAVIGATION = 2
    SENSORS = 3
    SERVICE = 4
    SETTINGS = 5
    MEDIA = 6
    REVERSE_CAMERA = 7

# Button layout
BUTTON_WIDTH = 360
BUTTON_HEIGHT = 240
BUTTON_GAP = 40
GRID_COLS = 3
GRID_ROWS = 2

# Gauge settings
GAUGE_WIDTH = 360
GAUGE_HEIGHT = 400

# Status bar
STATUS_HEIGHT = 60

# Sensor error values
@dataclass
class SensorDefaults:
    TEMPERATURE = 22.0
    HUMIDITY = 45.0
    SPEED = 0.0
    RPM = 800
    FUEL_LEVEL = 75.0
    GPS_LAT = 51.5074
    GPS_LON = -0.1278
    GPS_ALT = 0.0
    GPS_SATS = 0
    ULTRASONIC_FRONT = 150.0
    ULTRASONIC_REAR = 150.0
    ULTRASONIC_LEFT = 150.0
    ULTRASONIC_RIGHT = 150.0
    ACCEL_X = 0.0
    ACCEL_Y = 0.0
    ACCEL_Z = 1.0