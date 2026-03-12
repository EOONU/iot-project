"""
Main menu window with 6 module buttons
"""

import random
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import WindowState, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_GAP
from styles import MBColors
from widgets.touch_button import TouchButton


class MainMenuWindow(QWidget):
    """Main menu with clock and module buttons"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 80, 40, 40)
        layout.setSpacing(20)
        
        # Top status bar
        status_layout = QHBoxLayout()
        
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Arial", 48, QFont.Bold))
        self.time_label.setStyleSheet("color: white;")
        status_layout.addWidget(self.time_label)
        
        status_layout.addStretch()
        
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(10)
        
        star = QLabel("✦")
        star.setFont(QFont("Arial", 36))
        star.setStyleSheet("color: rgb(215, 215, 220);")
        logo_layout.addWidget(star)
        
        cmd = QLabel("COMMAND")
        cmd.setFont(QFont("Arial", 32, QFont.Bold))
        cmd.setStyleSheet("color: rgb(215, 215, 220);")
        logo_layout.addWidget(cmd)
        
        status_layout.addLayout(logo_layout)
        status_layout.addStretch()
        
        status = QLabel("● GPS  ● WiFi  85%")
        status.setFont(QFont("Arial", 20))
        status.setStyleSheet("color: rgb(0, 185, 85);")
        status_layout.addWidget(status)
        
        layout.addLayout(status_layout)
        
        welcome = QLabel("Welcome to Mercedes-Benz")
        welcome.setFont(QFont("Arial", 28))
        welcome.setStyleSheet("color: rgb(180, 180, 185);")
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)
        
        self.temp_label = QLabel("22.5°C")
        self.temp_label.setFont(QFont("Arial", 36))
        self.temp_label.setStyleSheet("color: rgb(255, 160, 0);")
        self.temp_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.temp_label)
        
        layout.addSpacing(40)
        
        grid = QGridLayout()
        grid.setSpacing(BUTTON_GAP)
        
        buttons = [
            ("Dashboard", "🚘", WindowState.DASHBOARD, MBColors.BLUE),
            ("Navigation", "🗺️", WindowState.NAVIGATION, MBColors.TEAL),
            ("Sensors", "📊", WindowState.SENSORS, MBColors.GREEN),
            ("Service", "🔧", WindowState.SERVICE, MBColors.AMBER),
            ("Media", "🎵", WindowState.MEDIA, MBColors.PURPLE),
            ("Settings", "⚙️", WindowState.SETTINGS, MBColors.SILVER),
        ]
        
        for i, (text, icon, state, color) in enumerate(buttons):
            btn = TouchButton(text, icon, BUTTON_WIDTH, BUTTON_HEIGHT, color)
            btn.clicked.connect(lambda checked, s=state: self.parent.change_window(s))
            grid.addWidget(btn, i // 3, i % 3)
            
        layout.addLayout(grid)
        layout.addStretch()
        
        hint = QLabel("Touch module to select")
        hint.setFont(QFont("Arial", 18))
        hint.setStyleSheet("color: rgb(180, 180, 185);")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        
    def update_time(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M"))
        
        temp = 22 + random.gauss(0, 0.5)
        self.temp_label.setText(f"{temp:.1f}°C")