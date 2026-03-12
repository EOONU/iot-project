"""
Information panel widget
"""

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from styles import MBColors, PANEL_STYLE


class InfoPanel(QFrame):
    """Styled information panel"""
    
    def __init__(self, title: str, lines: list, 
                 color=None, width: int = 350, height: int = 180,
                 parent=None):
        super().__init__(parent)
        
        if color is None:
            color = MBColors.AMBER
            
        self.setStyleSheet(PANEL_STYLE)
        self.setFixedSize(width, height)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)
        
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Arial", 20, QFont.Bold))
        title_lbl.setStyleSheet(f"color: rgb({color.red()}, {color.green()}, {color.blue()});")
        layout.addWidget(title_lbl)
        
        for line in lines:
            lbl = QLabel(line)
            lbl.setFont(QFont("Arial", 16))
            lbl.setStyleSheet("color: rgb(215, 215, 220);")
            layout.addWidget(lbl)
            
        layout.addStretch()