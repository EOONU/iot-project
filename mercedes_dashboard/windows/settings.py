"""
Settings window
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QSlider, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from config import WindowState
from styles import MBColors, PANEL_STYLE
from windows.base_window import BaseWindow


class SettingItem(QFrame):
    """Individual setting row"""
    
    def __init__(self, name: str, value: str, has_slider: bool = False,
                 color: QColor = MBColors.BLUE, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet(PANEL_STYLE)
        self.setFixedHeight(100)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Name
        name_lbl = QLabel(name)
        name_lbl.setFont(QFont("Arial", 22, QFont.Bold))
        name_lbl.setStyleSheet("color: white;")
        layout.addWidget(name_lbl)
        
        layout.addStretch()
        
        if has_slider:
            # Slider
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(85 if "Brightness" in name else 70)
            slider.setFixedWidth(300)
            slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    background: rgb(15, 15, 20);
                    height: 20px;
                    border-radius: 10px;
                }
                QSlider::sub-page:horizontal {
                    background: rgb(0, 130, 210);
                    border-radius: 10px;
                }
                QSlider::handle:horizontal {
                    background: white;
                    width: 20px;
                    margin: -5px 0;
                    border-radius: 10px;
                }
            """)
            layout.addWidget(slider)
            
            # Value
            val_lbl = QLabel(value)
            val_lbl.setFont(QFont("Arial", 20))
            val_lbl.setStyleSheet(f"color: rgb({color.red()}, {color.green()}, {color.blue()});")
            layout.addWidget(val_lbl)
        else:
            # Toggle/text value
            val_lbl = QLabel(value)
            val_lbl.setFont(QFont("Arial", 24, QFont.Bold))
            val_lbl.setStyleSheet(f"color: rgb({color.red()}, {color.green()}, {color.blue()});")
            layout.addWidget(val_lbl)
            
            # Toggle indicator
            if value in ["On", "Connected", "Dark"]:
                indicator = QLabel("●")
                indicator.setFont(QFont("Arial", 20))
                indicator.setStyleSheet(f"color: rgb({color.red()}, {color.green()}, {color.blue()});")
                layout.addWidget(indicator)


class SettingsWindow(BaseWindow):
    """System settings window"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "System Settings")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Two column layout
        columns = QHBoxLayout()
        
        left_col = QVBoxLayout()
        right_col = QVBoxLayout()
        
        settings = [
            ("Display Brightness", "85%", True, MBColors.BLUE),
            ("Audio Volume", "70%", True, MBColors.BLUE),
            ("Voice Guidance", "On", False, MBColors.GREEN),
            ("Units", "Metric", False, MBColors.TEAL),
            ("Time Format", "24h", False, MBColors.TEAL),
            ("Map Theme", "Dark", False, MBColors.PURPLE),
            ("Bluetooth", "Connected", False, MBColors.BLUE),
            ("WiFi", "Connected", False, MBColors.GREEN),
        ]
        
        for i, (name, value, has_slider, color) in enumerate(settings):
            item = SettingItem(name, value, has_slider, color)
            if i < 4:
                left_col.addWidget(item)
            else:
                right_col.addWidget(item)
                
        columns.addLayout(left_col)
        columns.addLayout(right_col)
        
        self.main_layout.addLayout(columns)
        self.main_layout.addStretch()
        self.add_back_button()