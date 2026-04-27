from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from ui.pages.base import BasePage

class ReversePage(BasePage):
    def __init__(self, sensors):
        super().__init__()
        self.sensors = sensors
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def _zone(self, cm):
        if cm < 25: return QColor(255, 70, 70, 220)
        if cm < 55: return QColor(255, 185, 60, 220)
        return QColor(0, 170, 255, 180)

    def _bar(self, p, x, y, h, value, label):
        p.setPen(QPen(QColor(255,255,255,30), 1))
        p.setBrush(QColor(255,255,255,16))
        p.drawRoundedRect(x, y, 74, h, 22, 22)
        fill = int((150 - min(max(value, 0), 150)) / 150 * h)
        p.setBrush(self._zone(value))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(x+6, y+h-fill-6, 62, fill, 18, 18)
        p.setPen(QColor(255,255,255))
        p.setFont(QFont("Arial", 16, QFont.Bold))
        p.drawText(x+24, y-10, label)
        p.drawText(x+8, y+h+28, f"{int(value)} cm")

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        p.setPen(QColor(255,255,255))
        p.setFont(QFont("Arial", 34, QFont.Bold))
        p.drawText(36, 56, "Reverse Assist")
        self._bar(p, 54, 130, 350, self.sensors.rear_left_distance, "L")
        self._bar(p, w-128, 130, 350, self.sensors.rear_right_distance, "R")
        cx = w // 2
        p.setPen(QPen(QColor(255,255,255,100), 3))
        p.setBrush(QColor(255,255,255,14))
        p.drawRoundedRect(cx-170, 150, 340, 250, 80, 80)
        p.drawRoundedRect(cx-118, 120, 236, 120, 56, 56)
        p.setPen(QColor(255,255,255))
        p.setFont(QFont("Arial", 20))
        p.drawText(36, 92, f"Rear left {int(self.sensors.rear_left_distance)} cm    Rear right {int(self.sensors.rear_right_distance)} cm")
        if self.sensors.rear_left_distance < 25 or self.sensors.rear_right_distance < 25:
            p.setPen(QColor(255,70,70))
            p.setFont(QFont("Arial", 24, QFont.Bold))
            p.drawText(cx-38, h-36, "STOP")
