#!/usr/bin/env python3
"""
Mercedes-Benz COMMAND - Main Application
With ESP32-CAM reverse camera and sensor error management
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget #QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from config import WindowState, SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from styles import MAIN_STYLE
from utils.sensor_manager import SensorManager
from windows.main_menu import MainMenuWindow
from windows.dashboard import DashboardWindow
from windows.navigation import NavigationWindow
from windows.sensors import SensorsWindow
from windows.service import ServiceWindow
from windows.settings import SettingsWindow
from windows.media import MediaWindow
from windows.reverse_camera import ReverseCameraWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mercedes-Benz COMMAND")
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setStyleSheet(MAIN_STYLE)
        
        try:
            self.showFullScreen()
        except:
            self.showMaximized()
        
        # Initialize sensor manager
        self.sensor_manager = SensorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Stacked widget
        self.stack = QStackedWidget()
        
        # Initialize all windows
        self.windows = {
            WindowState.MAIN_MENU: MainMenuWindow(self),
            WindowState.DASHBOARD: DashboardWindow(self, self.sensor_manager),
            WindowState.NAVIGATION: NavigationWindow(self, self.sensor_manager),
            WindowState.SENSORS: SensorsWindow(self.sensor_manager),
            WindowState.SERVICE: ServiceWindow(self),
            WindowState.SETTINGS: SettingsWindow(self),
            WindowState.MEDIA: MediaWindow(self),
            WindowState.REVERSE_CAMERA: ReverseCameraWindow(self.sensor_manager, self),
        }
        
        # Add to stack in order of WindowState values
        for state in WindowState:
            if state in self.windows:
                self.stack.QWidget(self.windows[state])
            
        layout.addWidget(self.stack)
        
        # Global timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_all)
        self.timer.start(int(1000 / FPS))
        
        # Auto-switch to reverse camera if triggered
        self.reverse_check_timer = QTimer(self)
        self.reverse_check_timer.timeout.connect(self.check_reverse_camera)
        self.reverse_check_timer.start(200)  # Check every 200ms
        
    def change_window(self, state: WindowState):
        """Switch window"""
        if state in self.windows:
            self.stack.setCurrentIndex(int(state))
            print(f"Switched to: {state.name}")
            
    def update_all(self):
        """Update sensors and animations"""
        # Update sensor manager
        self.sensor_manager.update(0.016)
        
        # Update current window animation
        current = self.stack.currentWidget()
        if hasattr(current, 'update_animation'):
            current.update_animation()
            
    def check_reverse_camera(self):
        """Auto-switch to reverse camera when triggered"""
        # Don't interrupt if already in reverse camera
        if self.stack.currentIndex() == int(WindowState.REVERSE_CAMERA):
            return
            
        if self.sensor_manager.check_reverse_camera():
            self.change_window(WindowState.REVERSE_CAMERA)
            
    def keyPressEvent(self, event):
        """Keyboard shortcuts"""
        key_map = {
            Qt.Key_1: WindowState.MAIN_MENU,
            Qt.Key_2: WindowState.DASHBOARD,
            Qt.Key_3: WindowState.NAVIGATION,
            Qt.Key_4: WindowState.SENSORS,
            Qt.Key_5: WindowState.SERVICE,
            Qt.Key_6: WindowState.SETTINGS,
            Qt.Key_7: WindowState.MEDIA,
            Qt.Key_R: WindowState.REVERSE_CAMERA,  # Manual reverse camera
            Qt.Key_Escape: None,
        }
        
        if event.key() in key_map:
            action = key_map[event.key()]
            if action is None:
                self.close()
            else:
                self.change_window(action)
                
    def closeEvent(self, event):
        """Cleanup on close"""
        self.sensor_manager.cleanup()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    font = QFont("Arial", 12)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)
    
    window = MainWindow()
    sys.exit(app.exec_())