"""
Dashboard window with real sensor data and error indicators
"""

import math
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QFrame, QVBoxLayout
from PyQt5.QtCore import Qt

from config import WindowState, SensorDefaults
from styles import MBColors
from windows.base_window import BaseWindow
from widgets.gauge_widget import GaugeWidget
from widgets.info_panel import InfoPanel


class DashboardWindow(BaseWindow):
    """Vehicle dashboard with sensor integration"""
    
    def __init__(self, parent=None, sensor_manager=None):
        super().__init__(parent, "Vehicle Status")
        self.sensor_manager = sensor_manager
        
        self.demo_time = 0.0
        self.error_indicators = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Error indicator bar (shows which sensors are using defaults)
        if self.sensor_manager and self.sensor_manager.demo_mode:
            error_bar = QFrame()
            error_bar.setFixedHeight(40)
            error_bar.setStyleSheet("background-color: rgb(100, 50, 0); border-radius: 8px;")
            error_layout = QHBoxLayout(error_bar)
            error_layout.setContentsMargins(10, 5, 10, 5)
            
            error_text = QLabel("⚠ NO SENSORS DETECTED - USING DEFAULT VALUES")
            error_text.setFont(QFont("Arial", 14))
            error_text.setStyleSheet("color: rgb(255, 200, 100);")
            error_layout.addWidget(error_text)
            
            self.main_layout.addWidget(error_bar)
        
        # Gauges row
        gauges_layout = QHBoxLayout()
        
        self.speed_gauge = GaugeWidget("SPEED", "km/h", 240, MBColors.BLUE)
        self.rpm_gauge = GaugeWidget("RPM", "x100", 80, MBColors.AMBER)
        self.temp_gauge = GaugeWidget("COOLANT", "°C", 120, MBColors.TEAL)
        
        gauges_layout.addWidget(self.speed_gauge)
        gauges_layout.addWidget(self.rpm_gauge)
        gauges_layout.addWidget(self.temp_gauge)
        
        self.main_layout.addLayout(gauges_layout)
        
        # Info panels
        panels_layout = QHBoxLayout()
        
        # Check which sensors are available
        has_sensors = self.sensor_manager and not self.sensor_manager.demo_mode
        
        panels = [
            ("Trip Computer", 
             ["Distance: 124.5 km", "Average: 7.2 L/100km", 
              f"Range: {SensorDefaults.FUEL_LEVEL * 6:.0f} km", "Time: 1:45"],
             MBColors.AMBER),
            ("Fuel Level",
             [f"{SensorDefaults.FUEL_LEVEL:.0f}%", 
              "320 km remaining", 
              "Efficiency: Good"],
             MBColors.GREEN),
            ("System Status",
             ["All systems operational" if has_sensors else "Sensors offline - defaults active",
              f"GPS: {self.sensor_manager.data['gps']['sats'] if has_sensors else 'N/A'} satellites",
              "No warnings active"],
             MBColors.BLUE if has_sensors else MBColors.AMBER),
        ]
        
        for title, lines, color in panels:
            panel = InfoPanel(title, lines, color)
            panels_layout.addWidget(panel)
            
        self.main_layout.addLayout(panels_layout)
        
        # Reverse camera button
        if self.sensor_manager and self.sensor_manager.sensors_available.get('esp32_cam'):
            cam_btn = QPushButton("📷 Reverse Camera")
            cam_btn.setFixedSize(200, 60)
            cam_btn.setFont(QFont("Arial", 16))
            cam_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgb(28, 28, 35);
                    color: white;
                    border: 2px solid rgb(0, 130, 210);
                    border-radius: 8px;
                }
                QPushButton:pressed {
                    background-color: rgb(48, 48, 58);
                }
            """)
            cam_btn.clicked.connect(
                lambda: self.parent.change_window(WindowState.REVERSE_CAMERA)
            )
            self.main_layout.addWidget(cam_btn, alignment=Qt.AlignCenter)
        
        self.main_layout.addStretch()
        self.add_back_button()
        
    def update_animation(self):
        """Update with real or demo values"""
        if self.sensor_manager:
            # Use real sensor data
            data = self.sensor_manager.data
            
            self.speed_gauge.set_value(data['speed'])
            self.rpm_gauge.set_value(data['rpm'])
            self.temp_gauge.set_value(data['temp'])
        else:
            # Demo mode
            self.demo_time += 0.05
            speed = 60 + math.sin(self.demo_time * 0.5) * 40
            rpm = 20 + math.sin(self.demo_time * 0.3) * 15
            temp = 90 + math.sin(self.demo_time * 0.2) * 5
            
            self.speed_gauge.set_value(speed)
            self.rpm_gauge.set_value(rpm)
            self.temp_gauge.set_value(temp)