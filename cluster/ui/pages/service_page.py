from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QFont, QPen, QPainter
from PyQt5.QtWidgets import QPushButton
from ui.pages.base import BasePage
from config import VEHICLE_NAME

class ServicePage(BasePage):
    def __init__(self, sensors):
        super().__init__()
        self.sensors = sensors
        self.done_btn = QPushButton("Mark Service Done", self)
        self.done_btn.clicked.connect(self.sensors.trip.mark_service_done)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def resizeEvent(self, event):
        self.done_btn.setGeometry(self.width()-230, 26, 190, 42)
        super().resizeEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        svc = self.sensors.trip.service_status()
        p.setPen(QColor(255,255,255))
        p.setFont(QFont("Arial", 34, QFont.Bold))
        p.drawText(36, 56, "Service Reminder")
        p.setFont(QFont("Arial", 18))
        p.setPen(QColor(180,188,198))
        p.drawText(36, 88, VEHICLE_NAME)
        status_text = "SERVICE DUE" if svc["due"] else "SERVICE OK"
        status_color = QColor(255, 80, 80) if svc["due"] else QColor(0, 190, 120)
        p.setPen(status_color)
        p.setFont(QFont("Arial", 28, QFont.Bold))
        p.drawText(36, 142, status_text)
        cards = [
            ("Current odometer", f"{self.sensors.trip.state['odometer_km']:.1f} km"),
            ("Last service date", self.sensors.trip.state["last_service_date"]),
            ("Distance since service", f"{svc['km_since']:.1f} km"),
            ("Distance remaining", f"{svc['km_remaining']:.1f} km"),
            ("Days since service", f"{svc['days_since']}"),
            ("Days remaining", f"{svc['days_remaining']}"),
        ]
        x1, y1, card_w, card_h = 40, 180, 280, 112
        gap_x, gap_y = 28, 24
        for i, (title, value) in enumerate(cards):
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
            p.setFont(QFont("Arial", 22, QFont.Bold))
            p.drawText(x+16, y+76, value)
