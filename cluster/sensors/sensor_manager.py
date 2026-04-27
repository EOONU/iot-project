import random
import threading
import time
from config import ESP32_BASE_URL, USE_ESP32, SIM_MAX_SPEED_KMH
from services.esp32_service import ESP32Service
from services.trip_service import TripService

class SensorManager:
    def __init__(self):
        self.running = True
        self.speed = 0
        self.temp = 21.0
        self.humidity = 0.0
        self.rear_left_distance = 130
        self.rear_right_distance = 130
        self.heading = 0
        self.latitude = 53.3498
        self.longitude = -6.2603
        self.gforce_x = 0.0
        self.gforce_y = 0.0
        self.gforce_z = 1.0
        self.pitch_deg = 0.0
        self.roll_deg = 0.0
        self.camera_triggered = False
        self.security_alert = False
        self.simulation = False
        self.force_simulation = False

        self.ultrasonic_left_live = False
        self.ultrasonic_right_live = False
        self.bma400_live = False
        self.dht11_live = False
        self.gps_live = False

        self._have_gps = False
        self._have_temp = False
        self._have_esp32 = False
        self._have_bma400 = False

        self.esp32 = ESP32Service(ESP32_BASE_URL) if USE_ESP32 else None
        self.trip = TripService()
        self._last_save = time.time()
        self._sim_speed_target = 0

    def start(self):
        threading.Thread(target=self.loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.trip.save()

    def toggle_simulation(self):
        self.force_simulation = not self.force_simulation
        self.simulation = self.force_simulation

    def loop(self):
        last = time.time()
        while self.running:
            now = time.time()
            dt = max(0.02, min(0.25, now - last))
            last = now

            if self.force_simulation:
                self._run_simulation()
                self.simulation = True
                self.ultrasonic_left_live = False
                self.ultrasonic_right_live = False
                self.bma400_live = False
                self.dht11_live = False
                self.gps_live = False
                self._have_gps = False
                self._have_temp = False
                self._have_esp32 = False
                self._have_bma400 = False
            else:
                self._have_esp32 = self.esp32.update(self) if self.esp32 is not None else False
                self._have_gps = self.gps_live
                self._have_temp = self.dht11_live
                self._have_bma400 = self.bma400_live

                if not self._have_esp32:
                    self._hold_values_safely()

                self.simulation = False

            self.camera_triggered = False
            self.security_alert = False
            self.trip.update(self.speed, dt)

            if now - self._last_save > 8:
                self.trip.save()
                self._last_save = now

            time.sleep(0.035)

    def _run_simulation(self):
        self._simulate_motion()
        self.temp = max(16.0, min(32.0, self.temp + random.uniform(-0.08, 0.08)))
        self.humidity = max(30.0, min(80.0, self.humidity + random.uniform(-0.3, 0.3)))
        self.rear_left_distance = random.randint(35, 150)
        self.rear_right_distance = random.randint(35, 150)
        self.gforce_x = round(random.uniform(-0.4, 0.4), 2)
        self.gforce_y = round(random.uniform(-0.8, 0.8), 2)
        self.gforce_z = round(1.0 + random.uniform(-0.05, 0.05), 2)
        self.pitch_deg = round(random.uniform(-3.0, 3.0), 1)
        self.roll_deg = round(random.uniform(-3.5, 3.5), 1)

    def _hold_values_safely(self):
        self._simulate_motion()
        self.gforce_x += (0.0 - self.gforce_x) * 0.08
        self.gforce_y += (0.0 - self.gforce_y) * 0.08
        self.gforce_z += (1.0 - self.gforce_z) * 0.08
        self.pitch_deg += (0.0 - self.pitch_deg) * 0.08
        self.roll_deg += (0.0 - self.roll_deg) * 0.08

    def _simulate_motion(self):
        if random.random() < 0.04:
            self._sim_speed_target = random.choice([0, 10, 20, 30, 50, 80, 100, 120])
        if self.speed < self._sim_speed_target:
            self.speed = min(self._sim_speed_target, self.speed + random.randint(1, 4))
        elif self.speed > self._sim_speed_target:
            self.speed = max(self._sim_speed_target, self.speed - random.randint(1, 5))
        self.speed = max(0, min(SIM_MAX_SPEED_KMH, self.speed))
        self.heading = (self.heading + random.randint(0, 3)) % 360
        self.latitude += random.uniform(-0.00008, 0.00008)
        self.longitude += random.uniform(-0.00008, 0.00008)
