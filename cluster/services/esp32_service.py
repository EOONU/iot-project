class ESP32Service:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def update(self, sensors):
        try:
            import requests
            data = requests.get(f"{self.base_url}/data", timeout=0.18).json()

            sensors.ultrasonic_left_live = bool(data.get("ultrasonic_left_live", False))
            sensors.ultrasonic_right_live = bool(data.get("ultrasonic_right_live", False))
            sensors.bma400_live = bool(data.get("bma400_live", False))
            sensors.dht11_live = bool(data.get("dht11_live", False))
            sensors.gps_live = bool(data.get("gps_live", False))

            if sensors.ultrasonic_left_live:
                sensors.rear_left_distance = int(float(data.get("rear_left_cm", sensors.rear_left_distance)))
            if sensors.ultrasonic_right_live:
                sensors.rear_right_distance = int(float(data.get("rear_right_cm", sensors.rear_right_distance)))
            if sensors.dht11_live:
                sensors.temp = float(data.get("temp_c", sensors.temp))
                sensors.humidity = float(data.get("humidity", sensors.humidity))
            if sensors.bma400_live:
                sensors.gforce_x = float(data.get("gforce_x", sensors.gforce_x))
                sensors.gforce_y = float(data.get("gforce_y", sensors.gforce_y))
                sensors.gforce_z = float(data.get("gforce_z", sensors.gforce_z))
                sensors.pitch_deg = float(data.get("pitch_deg", sensors.pitch_deg))
                sensors.roll_deg = float(data.get("roll_deg", sensors.roll_deg))
            if sensors.gps_live:
                sensors.latitude = float(data.get("latitude", sensors.latitude))
                sensors.longitude = float(data.get("longitude", sensors.longitude))
                sensors.speed = max(0, int(float(data.get("speed_kmh", sensors.speed))))
                sensors.heading = int(float(data.get("heading_deg", sensors.heading)))

            return True
        except Exception:
            sensors.ultrasonic_left_live = False
            sensors.ultrasonic_right_live = False
            sensors.bma400_live = False
            sensors.dht11_live = False
            sensors.gps_live = False
            return False
