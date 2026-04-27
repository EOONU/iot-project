from datetime import datetime
from services.state_store import StateStore
from config import ODOMETER_START_KM, LAST_SERVICE_ODOMETER_KM, LAST_SERVICE_DATE, SERVICE_INTERVAL_KM, SERVICE_INTERVAL_DAYS

class TripService:
    def __init__(self):
        self.store = StateStore()
        default = {
            "odometer_km": ODOMETER_START_KM,
            "trip_km": 0.0,
            "moving_seconds": 0.0,
            "elapsed_seconds": 0.0,
            "max_speed_kmh": 0.0,
            "last_service_odometer_km": LAST_SERVICE_ODOMETER_KM,
            "last_service_date": LAST_SERVICE_DATE,
        }
        self.state = self.store.load(default)

    def update(self, speed_kmh, dt_seconds):
        self.state["elapsed_seconds"] += dt_seconds
        dist = speed_kmh * dt_seconds / 3600.0
        self.state["odometer_km"] += dist
        self.state["trip_km"] += dist
        if speed_kmh > 1:
            self.state["moving_seconds"] += dt_seconds
        if speed_kmh > self.state["max_speed_kmh"]:
            self.state["max_speed_kmh"] = speed_kmh

    def reset_trip(self):
        self.state["trip_km"] = 0.0
        self.state["moving_seconds"] = 0.0
        self.state["elapsed_seconds"] = 0.0
        self.state["max_speed_kmh"] = 0.0
        self.save()

    def service_status(self):
        odo = self.state["odometer_km"]
        last_odo = self.state["last_service_odometer_km"]
        km_since = max(0.0, odo - last_odo)
        km_remaining = SERVICE_INTERVAL_KM - km_since
        try:
            last_date = datetime.strptime(self.state["last_service_date"], "%Y-%m-%d").date()
            days_since = (datetime.utcnow().date() - last_date).days
        except Exception:
            days_since = 0
        days_remaining = SERVICE_INTERVAL_DAYS - days_since
        return {"km_since": km_since, "km_remaining": km_remaining, "days_since": days_since, "days_remaining": days_remaining, "due": km_remaining <= 0 or days_remaining <= 0}

    def mark_service_done(self):
        self.state["last_service_odometer_km"] = self.state["odometer_km"]
        self.state["last_service_date"] = datetime.utcnow().date().isoformat()
        self.save()

    def save(self):
        self.store.save(self.state)
