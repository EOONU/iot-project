import math
import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QTimer, Qt, QPointF
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QFont,
    QRadialGradient, QPolygonF
)


class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AMG Performance Dashboard")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: #0a0a0a;")

        # Demo values
        self.speed = 0
        self.rpm = 0
        self.temperature = 60

        # Direction values for looping
        self.speed_dir = 2
        self.rpm_dir = 120
        self.temp_dir = 0.3

        # Colors
        self.colors = {
            'bg': QColor(10, 10, 12),
            'dark': QColor(35, 35, 40),
            'red': QColor(255, 30, 60),
            'orange': QColor(255, 140, 0),
            'yellow': QColor(255, 215, 0),
            'white': QColor(240, 240, 245),
            'dim': QColor(150, 150, 160),
        }

        # Timer (~60fps)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

    # ===============================
    # ANIMATION LOOP
    # ===============================
    def update_animation(self):

        # Speed loop
        self.speed += self.speed_dir
        if self.speed >= 260:
            self.speed_dir = -2
        elif self.speed <= 0:
            self.speed_dir = 2

        # RPM loop
        self.rpm += self.rpm_dir
        if self.rpm >= 8000:
            self.rpm_dir = -120
        elif self.rpm <= 0:
            self.rpm_dir = 120

        # Temperature loop
        self.temperature += self.temp_dir
        if self.temperature >= 110:
            self.temp_dir = -0.3
        elif self.temperature <= 60:
            self.temp_dir = 0.3

        self.update()

    # ===============================
    # PAINT EVENT
    # ===============================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), self.colors['bg'])

        cx = self.width() // 2
        cy = self.height() // 2 + 40

        self.draw_speedometer(painter, cx, cy, 220)
        self.draw_rpm(painter, 200, cy, 130)
        self.draw_temp(painter, self.width() - 200, cy, 100)

        self.draw_branding(painter)

    # ===============================
    # SPEEDOMETER
    # ===============================
    def draw_speedometer(self, painter, cx, cy, radius):

        # Background arc
        painter.setPen(QPen(self.colors['dark'], 14, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(cx - radius, cy - radius,
                        radius * 2, radius * 2,
                        135 * 16, 270 * 16)

        # Active arc
        active_angle = (self.speed / 260) * 270

        if self.speed < 100:
            color = self.colors['yellow']
        elif self.speed < 180:
            color = self.colors['orange']
        else:
            color = self.colors['red']

        painter.setPen(QPen(color, 14, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(cx - radius, cy - radius,
                        radius * 2, radius * 2,
                        135 * 16, -int(active_angle * 16))

        # Digital speed
        painter.setPen(self.colors['white'])
        painter.setFont(QFont("Arial", 80, QFont.Bold))
        painter.drawText(cx - 120, cy - 50, 240, 100,
                         Qt.AlignCenter, str(int(self.speed)))

        painter.setFont(QFont("Arial", 20))
        painter.setPen(self.colors['dim'])
        painter.drawText(cx - 50, cy + 30, 100, 40,
                         Qt.AlignCenter, "km/h")

        # Needle
        angle = 135 + active_angle
        self.draw_needle(painter, cx, cy, radius - 30, angle, color)

    # ===============================
    # RPM
    # ===============================
    def draw_rpm(self, painter, cx, cy, radius):

        painter.setPen(QPen(self.colors['dark'], 10, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(cx - radius, cy - radius,
                        radius * 2, radius * 2,
                        135 * 16, 270 * 16)

        rpm_angle = (self.rpm / 8000) * 270

        if self.rpm < 4000:
            color = self.colors['yellow']
        elif self.rpm < 6000:
            color = self.colors['orange']
        else:
            color = self.colors['red']

        painter.setPen(QPen(color, 10, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(cx - radius, cy - radius,
                        radius * 2, radius * 2,
                        135 * 16, -int(rpm_angle * 16))

        painter.setPen(self.colors['white'])
        painter.setFont(QFont("Arial", 30, QFont.Bold))
        painter.drawText(cx - 60, cy - 20, 120, 40,
                         Qt.AlignCenter, f"{int(self.rpm)}")

        self.draw_needle(painter, cx, cy, radius - 20,
                         135 + rpm_angle, color)

    # ===============================
    # TEMP
    # ===============================
    def draw_temp(self, painter, cx, cy, radius):

        painter.setPen(QPen(self.colors['dark'], 8, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(cx - radius, cy - radius,
                        radius * 2, radius * 2,
                        180 * 16, 180 * 16)

        temp_angle = ((self.temperature - 60) / 50) * 180

        painter.setPen(QPen(self.colors['orange'], 8, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(cx - radius, cy - radius,
                        radius * 2, radius * 2,
                        180 * 16, -int(temp_angle * 16))

        painter.setPen(self.colors['white'])
        painter.setFont(QFont("Arial", 24, QFont.Bold))
        painter.drawText(cx - 40, cy - 10, 80, 30,
                         Qt.AlignCenter, f"{int(self.temperature)}°C")

    # ===============================
    # NEEDLE
    # ===============================
    def draw_needle(self, painter, cx, cy, length, angle_deg, color):

        angle_rad = math.radians(angle_deg)

        painter.setBrush(color)
        painter.setPen(Qt.NoPen)

        points = QPolygonF([
            QPointF(cx, cy),
            QPointF(cx + (length - 10) * math.cos(angle_rad - 0.04),
                    cy - (length - 10) * math.sin(angle_rad - 0.04)),
            QPointF(cx + length * math.cos(angle_rad),
                    cy - length * math.sin(angle_rad)),
            QPointF(cx + (length - 10) * math.cos(angle_rad + 0.04),
                    cy - (length - 10) * math.sin(angle_rad + 0.04))
        ])

        painter.drawPolygon(points)

        gradient = QRadialGradient(cx, cy, 15)
        gradient.setColorAt(0, QColor(80, 80, 80))
        gradient.setColorAt(1, QColor(30, 30, 30))
        painter.setBrush(gradient)
        painter.drawEllipse(cx - 12, cy - 12, 24, 24)

    # ===============================
    # BRANDING
    # ===============================
    def draw_branding(self, painter):
        painter.setPen(self.colors['red'])
        painter.setFont(QFont("Arial", 32, QFont.Bold))
        painter.drawText(30, 60, "AMG")

        painter.setPen(self.colors['dim'])
        painter.setFont(QFont("Arial", 14))
        painter.drawText(30, 85, "PERFORMANCE")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())