from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QFont, QPen, QPainter
from PyQt5.QtWidgets import QPushButton
from ui.pages.base import BasePage

class TripPage(BasePage):
    def __init__(self, sensors):
        super().__init__()
        self.sensors = sensors
        self.reset_btn = QPushButton("Reset Trip", self)
        self.reset_btn.clicked.connect(self.sensors.trip.reset_trip)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(500)

    def resizeEvent(self, event):
        self.reset_btn.setGeometry(self.width()-180, 26, 150, 42)
        super().resizeEvent(event)

    def _fmt_time(self, seconds):
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        st = self.sensors.trip.state
        avg = st["trip_km"] / (st["moving_seconds"] / 3600.0) if st["moving_seconds"] > 0 else 0.0
        p.setPen(QColor(255,255,255))
        p.setFont(QFont("Arial", 34, QFont.Bold))
        p.drawText(36, 56, "Journey Data")
        items = [
            ("Trip distance", f"{st['trip_km']:.2f} km"),
            ("Odometer", f"{st['odometer_km']:.1f} km"),
            ("Travel time", self._fmt_time(st["elapsed_seconds"])),
            ("Moving time", self._fmt_time(st["moving_seconds"])),
            ("Average speed", f"{avg:.1f} km/h"),
            ("Max speed", f"{st['max_speed_kmh']:.0f} km/h"),
            ("GPS", f"{self.sensors.latitude:.5f}, {self.sensors.longitude:.5f}"),
            ("Heading", f"{int(self.sensors.heading)}°"),
        ]
        x1, y1, card_w, card_h = 40, 110, 280, 112
        gap_x, gap_y = 28, 24
        for i, (title, value) in enumerate(items):
            col = i % 2
            row = i // 2
            x = x1 + col * (card_w + gap_x)
            y = y1 + row * (card_h + gap_y)
            p.setPen(QPen(QColor(255,255,255,36), 1))
            p.setBrush(QColor(255,255,255,18))
            p.drawRoundedRect(x, y, card_w, card_h, 24, 24)
            p.setPen(QColor(190,198,208))
            p.setFont(QFont("Arial", 14))
            p.drawText(x+16, y+28, title)
            p.setPen(QColor(245,248,250))
            p.setFont(QFont("Arial", 24, QFont.Bold))
            p.drawText(x+16, y+78, value)
