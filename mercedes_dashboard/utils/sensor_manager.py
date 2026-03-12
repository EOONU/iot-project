"""
Sensor manager with error handling and default values
"""

import math
import random
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple

try:
    import board
    import busio
    import adafruit_dht
    import RPi.GPIO as GPIO
    from gps3 import gps3
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    logging.warning("Hardware libraries not available, using simulation mode")

# Fix import - use absolute import from parent directory
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SensorDefaults, ESP32_CAM_IP, ESP32_CAM_STREAM_URL, ESP32_CAM_SNAPSHOT_URL, REVERSE_CAMERA_TRIGGER


class SensorManager:
    """Manages all sensors with fallback to defaults on error"""
    
    def __init__(self):
        self.sensors_available = {
            'dht': False,
            'gps': False,
            'ultrasonic': False,
            'accelerometer': False,
            'esp32_cam': False,
        }
        
        self.data = {
            'temp': SensorDefaults.TEMPERATURE,
            'humidity': SensorDefaults.HUMIDITY,
            'speed': SensorDefaults.SPEED,
            'rpm': SensorDefaults.RPM,
            'fuel': SensorDefaults.FUEL_LEVEL,
            'gps': {
                'lat': SensorDefaults.GPS_LAT,
                'lon': SensorDefaults.GPS_LON,
                'alt': SensorDefaults.GPS_ALT,
                'sats': SensorDefaults.GPS_SATS,
                'fix': False,
                'track': []
            },
            'ultrasonic': {
                'front': SensorDefaults.ULTRASONIC_FRONT,
                'rear': SensorDefaults.ULTRASONIC_REAR,
                'left': SensorDefaults.ULTRASONIC_LEFT,
                'right': SensorDefaults.ULTRASONIC_RIGHT,
            },
            'accel': {
                'x': SensorDefaults.ACCEL_X,
                'y': SensorDefaults.ACCEL_Y,
                'z': SensorDefaults.ACCEL_Z,
            },
            'esp32_cam': {
                'connected': False,
                'stream_url': ESP32_CAM_STREAM_URL,
                'last_frame': None,
                'reverse_active': False,
            }
        }
        
        self.error_counts = {
            'dht': 0,
            'gps': 0,
            'ultrasonic': 0,
        }
        
        self.max_errors = 5
        
        if HARDWARE_AVAILABLE:
            self._init_hardware()
            
        self.demo_mode = not any(self.sensors_available.values())
        self.demo_time = 0.0
        
    def _init_hardware(self):
        """Initialize hardware sensors with error handling"""
        # Try DHT11
        try:
            self.dht = adafruit_dht.DHT11(board.D4)
            self.sensors_available['dht'] = True
            logging.info("DHT11 sensor initialized")
        except Exception as e:
            logging.warning(f"DHT11 not available: {e}")
            self.sensors_available['dht'] = False
            
        # Try GPS
        try:
            self.gps_socket = gps3.GPSDSocket()
            self.data_stream = gps3.DataStream()
            self.gps_socket.connect()
            self.gps_socket.watch()
            self.sensors_available['gps'] = True
            logging.info("GPS initialized")
        except Exception as e:
            logging.warning(f"GPS not available: {e}")
            self.sensors_available['gps'] = False
            
        # Try Ultrasonic
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            self.ultrasonic_pins = {
                'front': (25, 26),
                'rear': (27, 14),
                'left': (12, 13),
                'right': (6, 5)
            }
            for name, (trig, echo) in self.ultrasonic_pins.items():
                GPIO.setup(trig, GPIO.OUT)
                GPIO.setup(echo, GPIO.IN)
                GPIO.output(trig, False)
            self.sensors_available['ultrasonic'] = True
            logging.info("Ultrasonic sensors initialized")
        except Exception as e:
            logging.warning(f"Ultrasonic not available: {e}")
            self.sensors_available['ultrasonic'] = False
            
        # Try ESP32-CAM
        self._check_esp32_cam()
        
    def _check_esp32_cam(self):
        """Check ESP32-CAM connection"""
        try:
            import urllib.request
            import socket
            socket.setdefaulttimeout(2)
            urllib.request.urlopen(f"http://{ESP32_CAM_IP}", timeout=2)
            self.sensors_available['esp32_cam'] = True
            self.data['esp32_cam']['connected'] = True
            logging.info("ESP32-CAM connected")
        except Exception as e:
            logging.warning(f"ESP32-CAM not available: {e}")
            self.sensors_available['esp32_cam'] = False
            self.data['esp32_cam']['connected'] = False
            
    def read_dht(self):
        """Read DHT sensor with error handling"""
        if not self.sensors_available['dht']:
            return
            
        try:
            self.data['temp'] = self.dht.temperature
            self.data['humidity'] = self.dht.humidity
            self.error_counts['dht'] = 0
        except Exception as e:
            self.error_counts['dht'] += 1
            if self.error_counts['dht'] >= self.max_errors:
                logging.error(f"DHT failed {self.max_errors} times, using defaults")
                self.sensors_available['dht'] = False
                self.data['temp'] = SensorDefaults.TEMPERATURE
                self.data['humidity'] = SensorDefaults.HUMIDITY
                
    def read_gps(self):
        """Read GPS with error handling"""
        if not self.sensors_available['gps']:
            return
            
        try:
            for new_data in self.gps_socket:
                if new_data:
                    self.data_stream.unpack(new_data)
                    if self.data_stream.TPV['lat'] != 'n/a':
                        self.data['gps']['lat'] = float(self.data_stream.TPV['lat'])
                        self.data['gps']['lon'] = float(self.data_stream.TPV['lon'])
                        self.data['gps']['speed'] = float(self.data_stream.TPV.get('speed', 0)) * 3.6
                        self.data['gps']['alt'] = float(self.data_stream.TPV.get('alt', 0))
                        self.data['gps']['fix'] = True
                        self.data['gps']['track'].append(
                            (self.data['gps']['lon'], self.data['gps']['lat'])
                        )
                        if len(self.data['gps']['track']) > 500:
                            self.data['gps']['track'].pop(0)
                    if self.data_stream.SKY['satellites']:
                        self.data['gps']['sats'] = len(self.data_stream.SKY['satellites'])
                    self.error_counts['gps'] = 0
                    break
        except Exception as e:
            self.error_counts['gps'] += 1
            if self.error_counts['gps'] >= self.max_errors:
                logging.error(f"GPS failed {self.max_errors} times, using defaults")
                self.sensors_available['gps'] = False
                self.data['gps'].update({
                    'lat': SensorDefaults.GPS_LAT,
                    'lon': SensorDefaults.GPS_LON,
                    'fix': False,
                    'sats': 0
                })
                
    def read_ultrasonic(self, name: str) -> float:
        """Read single ultrasonic sensor"""
        if not self.sensors_available['ultrasonic']:
            return self.data['ultrasonic'][name]
            
        try:
            import time
            trig, echo = self.ultrasonic_pins[name]
            GPIO.output(trig, True)
            time.sleep(0.00001)
            GPIO.output(trig, False)
            
            start = time.time()
            timeout = start + 0.04
            
            while GPIO.input(echo) == 0 and start < timeout:
                start = time.time()
            if start >= timeout:
                raise TimeoutError("Echo start timeout")
                
            end = time.time()
            timeout = end + 0.04
            while GPIO.input(echo) == 1 and end < timeout:
                end = time.time()
            if end >= timeout:
                raise TimeoutError("Echo end timeout")
                
            duration = end - start
            distance = (duration * 34300) / 2
            
            if distance < 0 or distance > 400:
                raise ValueError(f"Invalid distance: {distance}")
                
            self.data['ultrasonic'][name] = round(distance, 1)
            return self.data['ultrasonic'][name]
            
        except Exception as e:
            logging.debug(f"Ultrasonic {name} error: {e}")
            return self.data['ultrasonic'][name]
            
    def update_demo_values(self, dt: float):
        """Generate demo values when no sensors connected"""
        self.demo_time += dt
        
        self.data['temp'] = SensorDefaults.TEMPERATURE + math.sin(self.demo_time * 0.5) * 3
        self.data['humidity'] = SensorDefaults.HUMIDITY + math.cos(self.demo_time * 0.3) * 5
        self.data['speed'] = abs(60 + math.sin(self.demo_time * 0.2) * 40)
        self.data['rpm'] = 20 + math.sin(self.demo_time * 0.4) * 15
        
        self.data['gps']['lat'] = SensorDefaults.GPS_LAT + math.sin(self.demo_time * 0.1) * 0.001
        self.data['gps']['lon'] = SensorDefaults.GPS_LON + math.cos(self.demo_time * 0.1) * 0.001
        self.data['gps']['speed'] = self.data['speed']
        self.data['gps']['fix'] = True
        self.data['gps']['sats'] = 8
        
        for name in self.data['ultrasonic']:
            base = getattr(SensorDefaults, f'ULTRASONIC_{name.upper()}')
            self.data['ultrasonic'][name] = base + random.gauss(0, 10)
            
    def check_reverse_camera(self) -> bool:
        """Check if reverse camera should be active"""
        if isinstance(REVERSE_CAMERA_TRIGGER, int):
            try:
                return GPIO.input(REVERSE_CAMERA_TRIGGER)
            except:
                pass
        return self.sensors_available['esp32_cam']
        
    def get_esp32_frame(self):
        """Get frame from ESP32-CAM"""
        if not self.sensors_available['esp32_cam']:
            return None
            
        try:
            import urllib.request
            import io
            from PIL import Image
            
            response = urllib.request.urlopen(
                ESP32_CAM_SNAPSHOT_URL, 
                timeout=1
            )
            img_data = response.read()
            
            image = Image.open(io.BytesIO(img_data))
            self.data['esp32_cam']['last_frame'] = image
            return image
            
        except Exception as e:
            logging.debug(f"ESP32-CAM frame error: {e}")
            return self.data['esp32_cam']['last_frame']
            
    def update(self, dt: float):
        """Update all sensors"""
        if self.demo_mode:
            self.update_demo_values(dt)
        else:
            self.read_dht()
            self.read_gps()
            
            if self.sensors_available['ultrasonic']:
                for name in self.data['ultrasonic']:
                    self.read_ultrasonic(name)
                    
        if int(self.demo_time) % 5 == 0:
            self._check_esp32_cam()
            
    def cleanup(self):
        """Cleanup hardware"""
        if HARDWARE_AVAILABLE and self.sensors_available.get('ultrasonic'):
            GPIO.cleanup()