from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QFont, QPainter
from PyQt5.QtWidgets import QPushButton
from ui.pages.base import BasePage
from ui.theme import ACCENT_AMBER, ACCENT_GREEN

class SensorsPage(BasePage):
    def __init__(self, sensors):
        super().__init__()
        self.sensors = sensors
        self.toggle_btn = QPushButton("Toggle Simulation", self)
        self.toggle_btn.clicked.connect(self.sensors.toggle_simulation)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(160)

    def resizeEvent(self, event):
        self.toggle_btn.setGeometry(self.width() - 230, 24, 190, 42)
        super().resizeEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Arial", 34, QFont.Bold))
        p.drawText(36, 56, "Sensor Status")

        mode_color = ACCENT_AMBER if self.sensors.force_simulation else ACCENT_GREEN
        mode_text = "SIMULATION ON" if self.sensors.force_simulation else "SIMULATION OFF"
        p.setPen(mode_color)
        p.setFont(QFont("Arial", 16, QFont.Bold))
        p.drawText(36, 88, mode_text)

        lines = [
            f"ESP32 hub live: {'YES' if self.sensors._have_esp32 else 'NO'}",
            f"GPS live: {'YES' if self.sensors.gps_live else 'NO'}",
            f"BMA400 live: {'YES' if self.sensors.bma400_live else 'NO'}",
            f"DHT11 live: {'YES' if self.sensors.dht11_live else 'NO'}",
            f"Rear left ultrasonic live: {'YES' if self.sensors.ultrasonic_left_live else 'NO'}",
            f"Rear right ultrasonic live: {'YES' if self.sensors.ultrasonic_right_live else 'NO'}",
            "",
            f"Rear left distance: {int(self.sensors.rear_left_distance)} cm",
            f"Rear right distance: {int(self.sensors.rear_right_distance)} cm",
            f"Temperature: {self.sensors.temp:.1f} °C",
            f"Humidity: {self.sensors.humidity:.1f} %",
            f"Latitude: {self.sensors.latitude:.5f}",
            f"Longitude: {self.sensors.longitude:.5f}",
            f"Speed: {int(self.sensors.speed)} km/h",
            f"Heading: {int(self.sensors.heading)}°",
            f"G-force X: {self.sensors.gforce_x:.2f} g",
            f"G-force Y: {self.sensors.gforce_y:.2f} g",
            f"G-force Z: {self.sensors.gforce_z:.2f} g",
            f"Pitch: {self.sensors.pitch_deg:.1f}°",
            f"Roll: {self.sensors.roll_deg:.1f}°",
        ]

        y = 122
        p.setPen(QColor(235, 240, 245))
        p.setFont(QFont("Arial", 22))
        for line in lines:
            p.drawText(44, y, line)
            y += 34
