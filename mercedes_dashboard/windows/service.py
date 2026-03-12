"""
Service reminders window
"""

import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QProgressBar, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

from config import WindowState
from styles import MBColors, PANEL_STYLE
from windows.base_window import BaseWindow


class ServiceItem(QFrame):
    """Service reminder item"""
    
    def __init__(self, name: str, percent: int, remaining: str, 
                 color: QColor, urgent: bool = False, parent=None):
        super().__init__(parent)
        
        self.urgent = urgent
        self.color = color
        self.time = 0.0
        
        self.setStyleSheet(PANEL_STYLE)
        self.setFixedHeight(100)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Icon
        icon = QLabel("🔧")
        icon.setFont(QFont("Segoe UI Emoji", 36))
        layout.addWidget(icon)
        
        # Info
        info_layout = QVBoxLayout()
        
        name_lbl = QLabel(name)
        name_lbl.setFont(QFont("Arial", 22, QFont.Bold))
        name_lbl.setStyleSheet("color: white;")
        info_layout.addWidget(name_lbl)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(percent)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgb(15, 15, 20);
                border-radius: 6px;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: rgb({color.red()}, {color.green()}, {color.blue()});
                border-radius: 6px;
            }}
        """)
        self.progress.setFixedWidth(400)
        info_layout.addWidget(self.progress)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Remaining
        rem = QLabel(remaining)
        rem.setFont(QFont("Arial", 18))
        rem.setStyleSheet(f"color: rgb({color.red()}, {color.green()}, {color.blue()});")
        layout.addWidget(rem)
        
        if urgent:
            self.warning = QLabel("⚠ URGENT")
            self.warning.setFont(QFont("Arial", 14, QFont.Bold))
            self.warning.setStyleSheet("color: rgb(220, 40, 40);")
            layout.addWidget(self.warning)
        else:
            self.warning = None
            
    def update_pulse(self, t):
        """Update urgent warning pulse"""
        if self.warning:
            pulse = (math.sin(t * 4) + 1) * 0.5
            alpha = int(255 * pulse)
            self.warning.setStyleSheet(f"color: rgba(220, 40, 40, {alpha});")


class ServiceWindow(BaseWindow):
    """Service schedule window"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Service Schedule")
        
        self.time = 0.0
        self.setup_ui()
        
    def setup_ui(self):
        services = [
            ("Engine Oil Change", 75, "2,500 km / 90 days", MBColors.GREEN, False),
            ("Tire Rotation", 35, "1,200 km / 45 days", MBColors.AMBER, False),
            ("Brake Pad Inspection", 12, "400 km / 12 days", MBColors.RED, True),
            ("Air Filter Replacement", 88, "8,800 km / 320 days", MBColors.GREEN, False),
            ("Cabin Filter", 65, "5,200 km / 180 days", MBColors.BLUE, False),
            ("Coolant Check", 50, "4,000 km / 150 days", MBColors.TEAL, False),
        ]
        
        self.items = []
        for name, pct, remaining, color, urgent in services:
            item = ServiceItem(name, pct, remaining, color, urgent)
            self.main_layout.addWidget(item)
            self.items.append(item)
            
        self.main_layout.addStretch()
        self.add_back_button()
        
    def update_animation(self):
        self.time += 0.05
        for item in self.items:
            item.update_pulse(self.time)