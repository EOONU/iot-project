"""
Reverse camera full-screen window
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from config import WindowState
from styles import MBColors
from widgets.camera_widget import CameraWidget


class ReverseCameraWindow(QWidget):
    """Full-screen reverse camera with parking sensors"""
    
    def __init__(self, sensor_manager, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.sensor_manager = sensor_manager
        
        self.setWindowTitle("Reverse Camera")
        self.setup_ui()
        
        # Auto-close timer (if reverse signal lost)
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_reverse_state)
        self.check_timer.start(100)  # Check every 100ms
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top bar with distance info
        top_bar = QWidget()
        top_bar.setFixedHeight(80)
        top_bar.setStyleSheet("background-color: rgb(15, 15, 20);")
        top_layout = QHBoxLayout(top_bar)
        
        # Rear distance
        self.distance_label = QLabel("150 cm")
        self.distance_label.setFont(QFont("Arial", 36, QFont.Bold))
        self.distance_label.setStyleSheet("color: rgb(0, 255, 0);")
        top_layout.addWidget(self.distance_label)
        
        top_layout.addStretch()
        
        # Warning
        self.warning_label = QLabel("")
        self.warning_label.setFont(QFont("Arial", 28, QFont.Bold))
        self.warning_label.setStyleSheet("color: red;")
        top_layout.addWidget(self.warning_label)
        
        top_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("✕ Close")
        close_btn.setFixedSize(150, 50)
        close_btn.setFont(QFont("Arial", 16))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(220, 40, 40);
                color: white;
                border-radius: 8px;
            }
            QPushButton:pressed {
                background-color: rgb(180, 30, 30);
            }
        """)
        close_btn.clicked.connect(self.close_camera)
        top_layout.addWidget(close_btn)
        
        layout.addWidget(top_bar)
        
        # Camera feed
        self.camera = CameraWidget(self.sensor_manager, self)
        self.camera.reverse_triggered.connect(self.on_reverse_change)
        layout.addWidget(self.camera)
        
        # Bottom sensor display
        bottom_bar = QWidget()
        bottom_bar.setFixedHeight(100)
        bottom_bar.setStyleSheet("background-color: rgb(15, 15, 20);")
        bottom_layout = QHBoxLayout(bottom_bar)
        
        # Side distances
        for side in ['Left', 'Rear', 'Right']:
            dist = QLabel(f"{side}: 150 cm")
            dist.setFont(QFont("Arial", 20))
            dist.setStyleSheet("color: rgb(180, 180, 185);")
            bottom_layout.addWidget(dist)
            setattr(self, f"{side.lower()}_label", dist)
            
        layout.addWidget(bottom_bar)
        
    def update_animation(self):
        """Update sensor displays"""
        # Update distances
        ultra = self.sensor_manager.data['ultrasonic']
        
        rear_dist = ultra['rear']
        self.distance_label.setText(f"{rear_dist:.0f} cm")
        
        # Color coding
        if rear_dist > 100:
            self.distance_label.setStyleSheet("color: rgb(0, 255, 0);")
            self.warning_label.setText("")
        elif rear_dist > 50:
            self.distance_label.setStyleSheet("color: rgb(255, 255, 0);")
            self.warning_label.setText("CAUTION")
        else:
            self.distance_label.setStyleSheet("color: rgb(255, 0, 0);")
            self.warning_label.setText("STOP!")
            
        # Side sensors
        self.left_label.setText(f"Left: {ultra['left']:.0f} cm")
        self.right_label.setText(f"Right: {ultra['right']:.0f} cm")
        
        # Check if we should auto-close
        if not self.sensor_manager.check_reverse_camera():
            self.close_camera()
            
    def check_reverse_state(self):
        """Check if still in reverse"""
        if not self.sensor_manager.check_reverse_camera():
            self.close_camera()
            
    def on_reverse_change(self, in_reverse: bool):
        """Handle reverse state change"""
        if not in_reverse:
            self.close_camera()
            
    def close_camera(self):
        """Close camera and return to previous window"""
        self.camera.stop_stream()
        if self.parent:
            self.parent.change_window(WindowState.DASHBOARD)
            
    def showEvent(self, event):
        """Start camera when shown"""
        self.camera.start_stream()
        super().showEvent(event)
        
    def closeEvent(self, event):
        """Stop camera when closed"""
        self.camera.stop_stream()
        super().closeEvent(event)