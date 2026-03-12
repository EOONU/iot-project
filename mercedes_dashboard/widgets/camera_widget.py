"""
ESP32-CAM live video widget with parking guidelines
"""

import logging
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from styles import MBColors
from config import ESP32_CAM_SNAPSHOT_URL

try:
    import urllib.request
    import io
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available, camera display disabled")


class CameraWidget(QWidget):
    """Live camera feed with parking guidelines"""
    
    reverse_triggered = pyqtSignal(bool)
    
    def __init__(self, sensor_manager, parent=None):
        super().__init__(parent)
        
        self.sensor_manager = sensor_manager
        self.stream_active = False
        self.current_frame = None
        
        self.setup_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(50)
        
        self.in_reverse = False
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setMinimumSize(800, 600)
        layout.addWidget(self.video_label)
        
        self.status_label = QLabel("CAMERA OFFLINE")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.status_label.setStyleSheet("color: red; background: transparent;")
        self.status_label.hide()
        layout.addWidget(self.status_label)
        
    def update_frame(self):
        reverse_active = self.sensor_manager.check_reverse_camera()
        
        if reverse_active != self.in_reverse:
            self.in_reverse = reverse_active
            self.reverse_triggered.emit(reverse_active)
            
        if not reverse_active:
            self.video_label.clear()
            self.status_label.setText("NOT IN REVERSE")
            self.status_label.show()
            return
            
        if not PIL_AVAILABLE:
            self.status_label.setText("PIL NOT AVAILABLE")
            self.status_label.show()
            return
            
        frame = self.sensor_manager.get_esp32_frame()
        
        if frame is None:
            self.status_label.setText("NO SIGNAL")
            self.status_label.show()
            return
            
        self.status_label.hide()
        
        try:
            if frame.mode != 'RGB':
                frame = frame.convert('RGB')
                
            frame = frame.resize((800, 600))
            
            img_data = frame.tobytes()
            qimage = QImage(img_data, frame.width, frame.height, 
                          frame.width * 3, QImage.Format_RGB888)
            
            qimage = self.draw_guidelines(qimage)
            
            pixmap = QPixmap.fromImage(qimage)
            self.video_label.setPixmap(pixmap)
            self.current_frame = pixmap
            
        except Exception as e:
            logging.error(f"Frame conversion error: {e}")
            self.status_label.setText("FRAME ERROR")
            self.status_label.show()
            
    def draw_guidelines(self, image: QImage) -> QImage:
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = image.width(), image.height()
        cx, cy = w // 2, h // 2
        
        distance = self.sensor_manager.data['ultrasonic']['rear']
        
        if distance > 100:
            color = QColor(0, 255, 0, 180)
        elif distance > 50:
            color = QColor(255, 255, 0, 180)
        else:
            color = QColor(255, 0, 0, 180)
            
        painter.setPen(QPen(color, 3))
        
        painter.drawLine(cx, h - 50, cx, h - 200)
        painter.drawLine(cx - 100, h - 50, cx - 50, h - 200)
        painter.drawLine(cx + 100, h - 50, cx + 50, h - 200)
        
        for i, dist in enumerate([50, 100, 150]):
            y = h - 50 - (i + 1) * 50
            painter.drawArc(cx - 100, y - 20, 200, 40, 0, 180 * 16)
            
        painter.setFont(QFont("Arial", 32, QFont.Bold))
        painter.setPen(color)
        painter.drawText(cx - 100, 50, 200, 50, Qt.AlignCenter, 
                        f"{distance:.0f} cm")
        
        if distance < 30:
            painter.setPen(QColor(255, 0, 0))
            painter.setFont(QFont("Arial", 48, QFont.Bold))
            painter.drawText(cx - 200, cy - 50, 400, 100, 
                           Qt.AlignCenter, "STOP!")
            
        painter.end()
        return image
        
    def start_stream(self):
        self.stream_active = True
        self.timer.start()
        
    def stop_stream(self):
        self.stream_active = False
        self.timer.stop()
        self.video_label.clear()