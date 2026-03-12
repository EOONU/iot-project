"""
Sensors window with car diagram
"""

import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QTimer,QPointF
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QPolygonF 

from config import WindowState
from styles import MBColors, PANEL_STYLE
from windows.base_window import BaseWindow


class CarWidget(QWidget):
    """Car diagram with sensor zones"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 500)
        self.time = 0.0
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        cx, cy = self.width() // 2, self.height() // 2
        
        # Car body
        car_w, car_h = 140, 280
        
        # Body
        painter.setBrush(MBColors.SILVER)
        painter.setPen(QPen(MBColors.WHITE, 3))
        painter.drawRoundedRect(cx - car_w//2, cy - car_h//2, car_w, car_h, 20, 20)
        
        # Wheels
        wheel_y = [cy - car_h//2 + 40, cy + car_h//2 - 40]
        for wy in wheel_y:
            painter.setBrush(MBColors.BORDER_GRAY)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(cx - car_w//2 - 20, wy - 20, 40, 40)
            painter.drawEllipse(cx + car_w//2 - 20, wy - 20, 40, 40)
        
        # Sensor zones with animation
        sensors = [
            (cx, cy - car_h//2 - 30, "F", 0, -1, MBColors.BLUE),
            (cx, cy + car_h//2 + 30, "R", 0, 1, MBColors.RED),
            (cx - car_w//2 - 40, cy, "L", -1, 0, MBColors.GREEN),
            (cx + car_w//2 + 40, cy, "R", 1, 0, MBColors.AMBER),
        ]
        
        for sx, sy, name, dx, dy, color in sensors:
            # Animated pulse
            pulse = (math.sin(self.time * 3) + 1) * 0.5
            cone_len = 80 + pulse * 40
            
            # Draw cone
            painter.setPen(QPen(color, 2))
            painter.setBrush(QColor(color.red(), color.green(), color.blue(), int(60 * pulse)))
            
            if dy != 0:  # Front/Rear
                points = QPolygonF([
                    QPointF(sx - 40, sy),
                    QPointF(sx - 80, sy + cone_len * dy),
                    QPointF(sx + 80, sy + cone_len * dy),
                    QPointF(sx + 40, sy)
                ])
            else:  # Left/Right
                points = QPolygonF([
                    QPointF(sx, sy - 40),
                    QPointF(sx + cone_len * dx, sy - 80),
                    QPointF(sx + cone_len * dx, sy + 80),
                    QPointF(sx, sy + 40)
                ])
            
            painter.drawPolygon(points)
            
            # Distance text
            dist = 150 + int(pulse * 50)
            painter.setPen(color)
            painter.setFont(QFont("Arial", 24, QFont.Bold))
            text_x = sx + (120 * dx) - 30 if dx != 0 else sx - 30
            text_y = sy + (120 * dy) - 15 if dy != 0 else sy - 15
            painter.drawText(int(text_x), int(text_y), f"{dist}")
            
            painter.setFont(QFont("Arial", 14))
            painter.setPen(MBColors.SILVER)
            painter.drawText(int(text_x) + 50, int(text_y) + 5, "cm")
            
    def update_animation(self):
        self.time += 0.05
        self.update()


class SensorsWindow(BaseWindow):
    """Sensor visualization window"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Sensor Array")
        
        self.setup_ui()
        
    def setup_ui(self):
        content = QHBoxLayout()
        
        # Car diagram
        self.car_widget = CarWidget()
        content.addWidget(self.car_widget)
        
        # Data panel
        panel = QFrame()
        panel.setStyleSheet(PANEL_STYLE)
        panel.setFixedWidth(520)
        panel_layout = QVBoxLayout(panel)
        
        title = QLabel("Live Data")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: rgb(255, 160, 0);")
        panel_layout.addWidget(title)
        
        # Simulated readings
        self.readings = [
            ("Ultrasonic Front", "150 cm", MBColors.BLUE),
            ("Ultrasonic Rear", "120 cm", MBColors.RED),
            ("Ultrasonic Left", "180 cm", MBColors.GREEN),
            ("Ultrasonic Right", "140 cm", MBColors.AMBER),
            ("Accelerometer X", "0.002 g", MBColors.TEAL),
            ("Accelerometer Y", "-0.001 g", MBColors.TEAL),
            ("Accelerometer Z", "1.005 g", MBColors.TEAL),
        ]
        
        self.reading_labels = []
        for label_text, value, color in self.readings:
            row = QFrame()
            row.setStyleSheet("background-color: rgb(48, 48, 58); border-radius: 8px;")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 8, 10, 8)
            
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Arial", 16))
            lbl.setStyleSheet("color: rgb(180, 180, 185);")
            row_layout.addWidget(lbl)
            
            row_layout.addStretch()
            
            val = QLabel(value)
            val.setFont(QFont("Arial", 18, QFont.Bold))
            val.setStyleSheet(f"color: rgb({color.red()}, {color.green()}, {color.blue()});")
            row_layout.addWidget(val)
            
            self.reading_labels.append(val)
            panel_layout.addWidget(row)
            
        panel_layout.addStretch()
        content.addWidget(panel)
        
        self.main_layout.addLayout(content)
        self.add_back_button()
        
    def update_animation(self):
        self.car_widget.update_animation()
        
        # Update simulated values
        import random
        for i, val_label in enumerate(self.reading_labels[:4]):
            dist = 120 + random.randint(-20, 30)
            val_label.setText(f"{dist} cm")
            
        for i, val_label in enumerate(self.reading_labels[4:], start=4):
            val = random.gauss(0, 0.002) if i < 6 else 1.0 + random.gauss(0, 0.001)
            val_label.setText(f"{val:.3f} g")