from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QLinearGradient, QBrush
from ui.pages.base import BasePage
from ui.theme import ACCENT_BLUE, ACCENT_RED, ACCENT_AMBER, TEXT, SUBTEXT

class ClusterPage(BasePage):
    def __init__(self, sensors):
        super().__init__()
        self.sensors = sensors
        self.display_speed = 0.0
        self.display_gx = 0.0
        self.display_gy = 0.0
        self.display_gz = 1.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(25)

    def _tick(self):
        self.display_speed += (self.sensors.speed - self.display_speed) * 0.16
        self.display_gx += (self.sensors.gforce_x - self.display_gx) * 0.2
        self.display_gy += (self.sensors.gforce_y - self.display_gy) * 0.2
        self.display_gz += (self.sensors.gforce_z - self.display_gz) * 0.2
        self.update()

    def _speed_color(self, speed):
        if speed >= 110: return ACCENT_RED
        if speed >= 70: return ACCENT_AMBER
        return ACCENT_BLUE

    def _clamp(self, value, lo, hi):
        return max(lo, min(hi, value))

    def _glass_card(self, p, x, y, w, h, title, value):
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0, 55))
        p.drawRoundedRect(x + 4, y + 8, w, h, 24, 24)
        grad = QLinearGradient(x, y, x, y + h)
        grad.setColorAt(0.0, QColor(255, 255, 255, 34))
        grad.setColorAt(1.0, QColor(255, 255, 255, 14))
        p.setBrush(QBrush(grad))
        p.setPen(QPen(QColor(255, 255, 255, 42), 1))
        p.drawRoundedRect(x, y, w, h, 24, 24)
        p.setPen(QColor(190, 198, 208))
        p.setFont(QFont("Arial", 14))
        p.drawText(x + 16, y + 34, title)
        p.setPen(QColor(245, 248, 250))
        p.setFont(QFont("Arial", 24, QFont.Bold))
        p.drawText(x + 16, y + 78, value)

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        top_grad = QLinearGradient(0, 0, w, 0)
        top_grad.setColorAt(0.0, QColor(0, 170, 255, 0))
        top_grad.setColorAt(0.5, QColor(0, 170, 255, 24))
        top_grad.setColorAt(1.0, QColor(0, 170, 255, 0))
        p.fillRect(0, 0, w, 90, QBrush(top_grad))

        scx, scy = int(w * 0.30), int(h * 0.45)
        p.setPen(QPen(QColor(0, 0, 0, 70), 34))
        p.drawEllipse(scx - 167, scy - 167, 334, 334)
        p.setPen(QPen(QColor(255, 255, 255, 16), 28))
        p.drawEllipse(scx - 165, scy - 165, 330, 330)
        p.setPen(QPen(self._speed_color(self.display_speed), 14))
        p.drawEllipse(scx - 148, scy - 148, 296, 296)
        p.setPen(SUBTEXT)
        p.setFont(QFont("Arial", 14))
        p.drawText(scx - 170, scy - 188, 340, 24, Qt.AlignCenter, f"Rear L {int(self.sensors.rear_left_distance)} cm   Rear R {int(self.sensors.rear_right_distance)} cm")
        p.setPen(TEXT)
        p.setFont(QFont("Arial", 86, QFont.Bold))
        p.drawText(scx - 120, scy - 48, 240, 120, Qt.AlignCenter, str(int(round(self.display_speed))))
        p.setPen(SUBTEXT)
        p.setFont(QFont("Arial", 22))
        p.drawText(scx - 120, scy + 44, 240, 36, Qt.AlignCenter, "km/h")

        gcx, gcy, radius = int(w * 0.73), int(h * 0.42), 135
        p.setPen(QPen(QColor(255, 255, 255, 70), 2))
        p.drawEllipse(gcx - radius, gcy - radius, radius * 2, radius * 2)
        p.drawEllipse(gcx - 90, gcy - 90, 180, 180)
        p.drawLine(gcx - radius, gcy, gcx + radius, gcy)
        p.drawLine(gcx, gcy - radius, gcx, gcy + radius)

        dot_x = gcx + int(self._clamp(self.display_gy, -1.5, 1.5) / 1.5 * (radius - 18))
        dot_y = gcy - int(self._clamp(self.display_gx, -1.5, 1.5) / 1.5 * (radius - 18))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 180, 255, 90))
        p.drawEllipse(dot_x - 24, dot_y - 24, 48, 48)
        p.setBrush(QColor(0, 180, 255, 230))
        p.drawEllipse(dot_x - 14, dot_y - 14, 28, 28)

        p.setPen(TEXT)
        p.setFont(QFont("Arial", 16, QFont.Bold))
        p.drawText(gcx - 55, gcy - radius - 26, 110, 24, Qt.AlignCenter, "ACCEL")
        p.drawText(gcx - 55, gcy + radius + 6, 110, 24, Qt.AlignCenter, "BRAKE")
        p.setPen(SUBTEXT)
        p.setFont(QFont("Arial", 14))
        p.drawText(gcx - 140, gcy + radius + 36, 280, 22, Qt.AlignCenter, f"X {self.display_gx:.2f}g   Y {self.display_gy:.2f}g   Z {self.display_gz:.2f}g")
        p.drawText(gcx - 140, gcy + radius + 58, 280, 22, Qt.AlignCenter, f"Pitch {self.sensors.pitch_deg:.1f}°   Roll {self.sensors.roll_deg:.1f}°")

        p.setPen(TEXT)
        p.setFont(QFont("Arial", 18, QFont.Bold))
        p.drawText(40, 46, "DRIVE")
        p.setPen(SUBTEXT)
        p.setFont(QFont("Arial", 16))
        p.drawText(w - 200, 46, f"{self.sensors.trip.state['odometer_km']:.1f} km")

        self._glass_card(p, 36, h - 160, 220, 104, "Temperature", f"{self.sensors.temp:.1f} °C")
        self._glass_card(p, w // 2 - 110, h - 170, 220, 120, "Trip", f"{self.sensors.trip.state['trip_km']:.1f} km")
        self._glass_card(p, w - 256, h - 160, 220, 104, "Heading", f"{int(self.sensors.heading)}°")

        if self.sensors.force_simulation:
            p.setPen(ACCENT_AMBER)
            p.setFont(QFont("Arial", 16, QFont.Bold))
            p.drawText(40, 86, "SIMULATION MODE ON")
