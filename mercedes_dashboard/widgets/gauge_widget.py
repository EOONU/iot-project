"""
Circular gauge widget with needle
"""

import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QPolygonF, QRadialGradient

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from styles import MBColors


class GaugeWidget(QWidget):
    """Mercedes-style circular gauge"""
    
    def __init__(self, title: str, unit: str, max_value: float, 
                 color=None, parent=None):
        super().__init__(parent)
        
        if color is None:
            color = MBColors.BLUE
            
        self.title = title
        self.unit = unit
        self.max_value = max_value
        self.color = color
        
        self.value = 0.0
        self.target_value = 0.0
        
        self.setMinimumSize(300, 350)
        self.setMaximumSize(400, 450)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)
        
    def set_value(self, value: float):
        """Set target value"""
        self.target_value = max(0, min(value, self.max_value))
        
    def animate(self):
        """Smooth value animation"""
        diff = self.target_value - self.value
        if abs(diff) > 0.1:
            self.value += diff * 0.1
            self.update()
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        cx = self.width() // 2
        cy = self.height() // 2 - 10
        radius = min(cx, cy) - 30
        
        self._draw_background(painter, cx, cy, radius)
        self._draw_ticks(painter, cx, cy, radius)
        self._draw_value_arc(painter, cx, cy, radius)
        self._draw_needle(painter, cx, cy, radius - 25)
        self._draw_center_text(painter, cx, cy)
        self._draw_labels(painter, cx, cy, radius)
        
    def _draw_background(self, painter, cx, cy, radius):
        """Draw gauge background track"""
        track_pen = QPen(MBColors.SURFACE_GRAY, 12)
        track_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(cx - radius, cy - radius, radius * 2, radius * 2,
                       135 * 16, 270 * 16)
        
    def _draw_ticks(self, painter, cx, cy, radius):
        """Draw tick marks"""
        painter.setPen(QPen(MBColors.SILVER, 2))
        
        for i in range(0, 271, 10):
            angle = math.radians(135 + i)
            is_major = i % 30 == 0
            
            r_inner = radius - 25
            r_outer = radius - 15 if is_major else radius - 20
            
            x1 = cx + r_inner * math.cos(angle)
            y1 = cy - r_inner * math.sin(angle)
            x2 = cx + r_outer * math.cos(angle)
            y2 = cy - r_outer * math.sin(angle)
            
            painter.setPen(QPen(MBColors.SILVER, 3 if is_major else 1))
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            
    def _draw_value_arc(self, painter, cx, cy, radius):
        """Draw colored value arc"""
        if self.max_value <= 0:
            return
            
        ratio = min(1.0, self.value / self.max_value)
        segments = int(ratio * 27)
        
        for i in range(segments):
            angle = 135 + (i * 270 / 27)
            
            grad = i / 27
            r = int(self.color.red() + (255 - self.color.red()) * grad * 0.3)
            g = int(self.color.green() + (255 - self.color.green()) * grad * 0.3)
            b = int(self.color.blue() + (255 - self.color.blue()) * grad * 0.3)
            
            seg_pen = QPen(QColor(r, g, b), 10)
            seg_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(seg_pen)
            painter.drawArc(cx - radius, cy - radius, radius * 2, radius * 2,
                          int(angle * 16), int((270/27) * 16))
                          
    def _draw_needle(self, painter, cx, cy, length):
        """Draw gauge needle"""
        if self.max_value <= 0:
            return
            
        angle_deg = 135 + (self.value / self.max_value) * 270
        angle_rad = math.radians(angle_deg)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 100))
        
        offset = 3
        shadow_pts = QPolygonF([
            QPointF(cx + offset, cy + offset),
            QPointF(cx + (length - 10) * math.cos(angle_rad - 0.05) + offset,
                   cy - (length - 10) * math.sin(angle_rad - 0.05) + offset),
            QPointF(cx + length * math.cos(angle_rad) + offset,
                   cy - length * math.sin(angle_rad) + offset),
            QPointF(cx + (length - 10) * math.cos(angle_rad + 0.05) + offset,
                   cy - (length - 10) * math.sin(angle_rad + 0.05) + offset)
        ])
        painter.drawPolygon(shadow_pts)
        
        painter.setBrush(MBColors.RED)
        points = QPolygonF([
            QPointF(cx, cy),
            QPointF(cx + (length - 10) * math.cos(angle_rad - 0.05),
                   cy - (length - 10) * math.sin(angle_rad - 0.05)),
            QPointF(cx + length * math.cos(angle_rad),
                   cy - length * math.sin(angle_rad)),
            QPointF(cx + (length - 10) * math.cos(angle_rad + 0.05),
                   cy - (length - 10) * math.sin(angle_rad + 0.05))
        ])
        painter.drawPolygon(points)
        
        gradient = QRadialGradient(cx, cy, 15)
        gradient.setColorAt(0, MBColors.SURFACE_GRAY)
        gradient.setColorAt(1, MBColors.DEEP_GRAY)
        painter.setBrush(gradient)
        painter.setPen(QPen(MBColors.BORDER_GRAY, 2))
        painter.drawEllipse(cx - 12, cy - 12, 24, 24)
        
    def _draw_center_text(self, painter, cx, cy):
        """Draw center value and unit"""
        painter.setFont(QFont("Arial", 72, QFont.Bold))
        painter.setPen(MBColors.WHITE)
        val_text = f"{int(self.value)}"
        painter.drawText(cx - 80, cy - 40, 160, 80, Qt.AlignCenter, val_text)
        
        painter.setFont(QFont("Arial", 20))
        painter.setPen(MBColors.SILVER)
        painter.drawText(cx - 40, cy + 20, 80, 30, Qt.AlignCenter, self.unit)
        
    def _draw_labels(self, painter, cx, cy, radius):
        """Draw title and scale numbers"""
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.setPen(MBColors.WHITE)
        
        for i in range(0, int(self.max_value) + 1, max(1, int(self.max_value / 6))):
            angle = math.radians(135 + (i / self.max_value) * 270)
            x = cx + (radius - 45) * math.cos(angle)
            y = cy - (radius - 45) * math.sin(angle)
            painter.drawText(int(x - 20), int(y + 7), 40, 20, 
                           Qt.AlignCenter, str(int(i)))
        
        painter.setFont(QFont("Arial", 18))
        painter.setPen(MBColors.SILVER)
        painter.drawText(cx - 60, cy + radius + 20, 120, 30, 
                        Qt.AlignCenter, self.title)