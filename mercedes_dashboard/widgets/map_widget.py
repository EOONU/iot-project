"""
Navigation map widget with animated route and GPS tracking
"""

import math
import random
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt5.QtGui import (QPainter, QColor, QPen, QBrush, QFont, 
                         QLinearGradient, QRadialGradient, QPolygonF)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from styles import MBColors


class MapWidget(QWidget):
    """Animated navigation map with GPS tracking"""
    
    def __init__(self, parent=None, sensor_manager=None):
        super().__init__(parent)
        
        self.sensor_manager = sensor_manager
        self.track_points = []
        self.time = 0.0
        self.zoom_level = 1.0
        self.map_offset = QPointF(0, 0)
        
        self.grid_size = 80
        self.grid_color = MBColors.SURFACE_GRAY
        
        self.animation_speed = 0.05
        self.demo_mode = True
        
        self.setMinimumSize(800, 550)
        self.setStyleSheet("""
            background-color: rgb(15, 15, 20);
            border: 3px solid rgb(72, 72, 82);
            border-radius: 12px;
        """)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_route)
        self.timer.start(50)
        
        self._init_demo_route()
        
    def _init_demo_route(self):
        cx, cy = 400, 275
        
        for i in range(50):
            t = i * 0.1
            x = cx + math.sin(t * 0.5) * 200 + math.cos(t * 0.3) * 100
            y = cy + math.cos(t * 0.4) * 150 + math.sin(t * 0.2) * 80
            self.track_points.append(QPointF(
                max(50, min(750, x)), 
                max(50, min(500, y))
            ))
            
    def set_demo_mode(self, enabled: bool):
        self.demo_mode = enabled
        
    def zoom_in(self):
        self.zoom_level = min(3.0, self.zoom_level * 1.2)
        self.update()
        
    def zoom_out(self):
        self.zoom_level = max(0.5, self.zoom_level / 1.2)
        self.update()
        
    def reset_view(self):
        self.zoom_level = 1.0
        self.map_offset = QPointF(0, 0)
        self.update()
        
    def update_route(self):
        self.time += self.animation_speed
        
        cx = self.width() // 2
        cy = self.height() // 2
        
        if self.demo_mode:
            x = cx + math.sin(self.time * 0.5) * 200 + math.cos(self.time * 0.3) * 100
            y = cy + math.cos(self.time * 0.4) * 150 + math.sin(self.time * 0.2) * 80
            
            x += random.gauss(0, 2)
            y += random.gauss(0, 2)
        else:
            if self.sensor_manager and self.sensor_manager.data['gps']['fix']:
                gps = self.sensor_manager.data['gps']
                scale = 50000 * self.zoom_level
                x = cx + (gps['lon'] - gps.get('center_lon', gps['lon'])) * scale
                y = cy - (gps['lat'] - gps.get('center_lat', gps['lat'])) * scale
            else:
                return
                
        margin = 50
        x = max(margin, min(self.width() - margin, x))
        y = max(margin, min(self.height() - margin, y))
        
        new_point = QPointF(x, y)
        
        if not self.track_points or self._distance(self.track_points[-1], new_point) > 5:
            self.track_points.append(new_point)
            
        max_points = 500
        if len(self.track_points) > max_points:
            self.track_points.pop(0)
            
        self.update()
        
    def _distance(self, p1: QPointF, p2: QPointF) -> float:
        return math.sqrt((p1.x() - p2.x())**2 + (p1.y() - p2.y())**2)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        
        painter.fillRect(self.rect(), MBColors.DEEP_GRAY)
        
        self._draw_grid(painter, w, h)
        self._draw_track(painter)
        self._draw_prediction(painter)
        self._draw_position_marker(painter)
        self._draw_compass(painter)
        self._draw_scale(painter)
        self._draw_info_overlay(painter)
        
    def _draw_grid(self, painter, w, h):
        painter.setPen(QPen(self.grid_color, 1))
        
        grid_spacing = int(self.grid_size * self.zoom_level)
        offset_x = int(self.map_offset.x()) % grid_spacing
        offset_y = int(self.map_offset.y()) % grid_spacing
        
        for x in range(offset_x, w, grid_spacing):
            painter.drawLine(x, 0, x, h)
            
        for y in range(offset_y, h, grid_spacing):
            painter.drawLine(0, y, w, y)
            
        painter.setPen(QPen(MBColors.BORDER_GRAY, 2))
        
        for x in range(offset_x, w, grid_spacing * 5):
            painter.drawLine(x, 0, x, h)
            
        for y in range(offset_y, h, grid_spacing * 5):
            painter.drawLine(0, y, w, y)
            
    def _draw_track(self, painter):
        if len(self.track_points) < 2:
            return
            
        total_points = len(self.track_points)
        
        for i in range(total_points - 1):
            age_ratio = i / total_points
            
            r = int(MBColors.TEAL.red() * (0.3 + 0.7 * age_ratio))
            g = int(MBColors.TEAL.green() * (0.3 + 0.7 * age_ratio))
            b = int(MBColors.TEAL.blue() * (0.3 + 0.7 * age_ratio))
            
            alpha = int(50 + 205 * age_ratio)
            color = QColor(r, g, b, alpha)
            
            pen_width = 2 + 6 * age_ratio
            
            painter.setPen(QPen(color, pen_width, 
                               Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            
            p1 = self.track_points[i]
            p2 = self.track_points[i + 1]
            
            painter.drawLine(int(p1.x()), int(p1.y()), 
                           int(p2.x()), int(p2.y()))
                           
        if len(self.track_points) > 10:
            for i in range(10, total_points - 1, 20):
                self._draw_direction_arrow(painter, self.track_points[i-5], 
                                         self.track_points[i])
                                         
    def _draw_direction_arrow(self, painter, p1, p2):
        angle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
        
        size = 8
        
        tip_x = p2.x() - 15 * math.cos(angle)
        tip_y = p2.y() - 15 * math.sin(angle)
        
        arrow_points = QPolygonF([
            QPointF(tip_x, tip_y),
            QPointF(tip_x - size * math.cos(angle - 0.5),
                   tip_y - size * math.sin(angle - 0.5)),
            QPointF(tip_x - size * math.cos(angle + 0.5),
                   tip_y - size * math.sin(angle + 0.5))
        ])
        
        painter.setBrush(QColor(255, 255, 255, 150))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(arrow_points)
        
    def _draw_prediction(self, painter):
        if len(self.track_points) < 2 or not self.demo_mode:
            return
            
        last = self.track_points[-1]
        prev = self.track_points[-5] if len(self.track_points) > 5 else self.track_points[0]
        
        angle = math.atan2(last.y() - prev.y(), last.x() - prev.x())
        
        pen = QPen(MBColors.AMBER, 3, Qt.DashLine)
        painter.setPen(pen)
        
        pred_length = 100
        pred_x = last.x() + pred_length * math.cos(angle)
        pred_y = last.y() + pred_length * math.sin(angle)
        
        dash_len = 10
        gap_len = 5
        total_dist = self._distance(last, QPointF(pred_x, pred_y))
        
        current_dist = 0
        while current_dist < total_dist:
            ratio = current_dist / total_dist
            x1 = last.x() + (pred_x - last.x()) * ratio
            y1 = last.y() + (pred_y - last.y()) * ratio
            
            ratio2 = min(1.0, (current_dist + dash_len) / total_dist)
            x2 = last.x() + (pred_x - last.x()) * ratio2
            y2 = last.y() + (pred_y - last.y()) * ratio2
            
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            current_dist += dash_len + gap_len
            
    def _draw_position_marker(self, painter):
        if not self.track_points:
            return
            
        pos = self.track_points[-1]
        
        pulse = (math.sin(self.time * 3) + 1) * 0.5
        glow_radius = 25 + pulse * 10
        
        gradient = QRadialGradient(pos, glow_radius)
        gradient.setColorAt(0, QColor(MBColors.AMBER.red(), 
                                       MBColors.AMBER.green(),
                                       MBColors.AMBER.blue(), 100))
        gradient.setColorAt(1, QColor(MBColors.AMBER.red(),
                                       MBColors.AMBER.green(),
                                       MBColors.AMBER.blue(), 0))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(pos, glow_radius, glow_radius)
        
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(MBColors.AMBER, 3))
        painter.drawEllipse(pos, 18, 18)
        
        painter.setBrush(MBColors.WHITE)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(pos, 10, 10)
        
        if len(self.track_points) > 5:
            prev = self.track_points[-5]
            angle = math.atan2(pos.y() - prev.y(), pos.x() - prev.x())
            
            arrow_len = 35
            arrow_x = pos.x() + arrow_len * math.cos(angle)
            arrow_y = pos.y() + arrow_len * math.sin(angle)
            
            painter.setBrush(MBColors.AMBER)
            
            arrow_points = QPolygonF([
                QPointF(arrow_x, arrow_y),
                QPointF(arrow_x - 12 * math.cos(angle - 0.5),
                       arrow_y - 12 * math.sin(angle - 0.5)),
                QPointF(arrow_x - 12 * math.cos(angle + 0.5),
                       arrow_y - 12 * math.sin(angle + 0.5))
            ])
            
            painter.drawPolygon(arrow_points)
            
        if not self.demo_mode:
            accuracy = 20
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(MBColors.SILVER, 1, Qt.DashLine))
            painter.drawEllipse(pos, accuracy, accuracy)
            
    def _draw_compass(self, painter):
        cx, cy = 60, 60
        size = 40
        
        painter.setBrush(MBColors.PANEL_GRAY)
        painter.setPen(QPen(MBColors.BORDER_GRAY, 2))
        painter.drawEllipse(cx - size, cy - size, size * 2, size * 2)
        
        painter.setBrush(MBColors.RED)
        painter.setPen(Qt.NoPen)
        
        north_points = QPolygonF([
            QPointF(cx, cy - size + 10),
            QPointF(cx - 10, cy - size + 25),
            QPointF(cx + 10, cy - size + 25)
        ])
        painter.drawPolygon(north_points)
        
        painter.setPen(MBColors.WHITE)
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(cx - 15, cy - size - 10, 30, 20, 
                        Qt.AlignCenter, "N")
                        
    def _draw_scale(self, painter):
        x = self.width() - 150
        y = self.height() - 40
        
        bar_length = 100
        actual_length = int(bar_length * self.zoom_level)
        
        painter.setPen(QPen(MBColors.WHITE, 2))
        painter.drawLine(x, y, x + actual_length, y)
        painter.drawLine(x, y - 5, x, y + 5)
        painter.drawLine(x + actual_length, y - 5, x + actual_length, y + 5)
        
        scale_text = f"{int(100 * self.zoom_level)}m"
        painter.setFont(QFont("Arial", 12))
        painter.setPen(MBColors.SILVER)
        painter.drawText(x, y - 10, actual_length, 20, 
                        Qt.AlignCenter, scale_text)
                        
    def _draw_info_overlay(self, painter):
        if not self.track_points:
            return
            
        if self.demo_mode:
            lat, lon = 51.5074 + math.sin(self.time * 0.1) * 0.01, \
                      -0.1278 + math.cos(self.time * 0.1) * 0.01
        else:
            lat = self.sensor_manager.data['gps']['lat'] if self.sensor_manager else 0
            lon = self.sensor_manager.data['gps']['lon'] if self.sensor_manager else 0
            
        info_text = f"Lat: {lat:.5f}°  Lon: {lon:.5f}°"
        
        painter.setFont(QFont("Arial", 14))
        painter.setPen(MBColors.SILVER)
        painter.drawText(10, self.height() - 10, info_text)
        
        painter.setFont(QFont("Arial", 10))
        painter.drawText(10, self.height() - 25, 
                        f"Track points: {len(self.track_points)}")
                        
    def mousePressEvent(self, event):
        self.last_mouse_pos = event.pos()
        
    def mouseMoveEvent(self, event):
        if hasattr(self, 'last_mouse_pos'):
            delta = event.pos() - self.last_mouse_pos
            self.map_offset += QPointF(delta.x(), delta.y())
            self.last_mouse_pos = event.pos()
            self.update()
            
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.track_points:
            self._init_demo_route()