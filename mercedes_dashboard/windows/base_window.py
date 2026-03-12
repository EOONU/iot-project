"""
Base window with common functionality
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import WindowState, STATUS_HEIGHT
from styles import MBColors


class BaseWindow(QWidget):
    """Base class for all windows"""
    
    def __init__(self, parent=None, title: str = ""):
        super().__init__(parent)
        self.parent = parent
        self.title_text = title
        
        self.setup_base_ui()
        
    def setup_base_ui(self):
        """Setup common UI elements"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, STATUS_HEIGHT + 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        if self.title_text:
            self.title_label = QLabel(self.title_text)
            self.title_label.setFont(QFont("Arial", 36, QFont.Bold))
            self.title_label.setStyleSheet("color: white;")
            self.title_label.setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(self.title_label)
            
    def add_back_button(self):
        """Add back button to layout"""
        back_btn = QPushButton("← Back")
        back_btn.setFixedSize(120, 50)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(28, 28, 35);
                color: white;
                font-size: 18px;
                border: 2px solid rgb(72, 72, 82);
                border-radius: 8px;
            }
            QPushButton:pressed {
                background-color: rgb(48, 48, 58);
                border-color: rgb(255, 160, 0);
            }
        """)
        back_btn.clicked.connect(lambda: self.parent.change_window(WindowState.MAIN_MENU))
        self.main_layout.addWidget(back_btn, alignment=Qt.AlignLeft)
        
    def update_animation(self):
        """Override for animations"""
        pass