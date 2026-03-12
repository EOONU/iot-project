"""
Touch-optimized button with Mercedes styling
"""

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont, QLinearGradient, QPen

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from styles import MBColors


class TouchButton(QPushButton):
    """Large touch-optimized button"""
    
    def __init__(self, text: str, icon: str = "", 
                 width: int = 360, height: int = 240,
                 accent_color=None, parent=None):
        super().__init__(parent)
        
        if accent_color is None:
            accent_color = MBColors.AMBER
            
        self.setText(text)
        self.icon_text = icon
        self.accent_color = accent_color
        self.setFixedSize(width, height)
        
        self.is_pressed = False
        self.is_hovered = False
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 60))
        painter.drawRoundedRect(rect.translated(6, 6), 16, 16)
        
        gradient = QLinearGradient(0, 0, 0, rect.height())
        base = self.accent_color if self.is_hovered else MBColors.PANEL_GRAY
        
        gradient.setColorAt(0, QColor(base.red(), base.green(), base.blue()))
        gradient.setColorAt(1, QColor(int(base.red() * 0.8), 
                                     int(base.green() * 0.8), 
                                     int(base.blue() * 0.8)))
        
        painter.setBrush(gradient)
        
        border_col = self.accent_color if (self.is_hovered or self.is_pressed) else MBColors.BORDER_GRAY
        painter.setPen(QPen(border_col, 3 if self.is_hovered else 2))
        painter.drawRoundedRect(rect, 16, 16)
        
        if self.icon_text:
            painter.setPen(MBColors.WHITE)
            painter.setFont(QFont("Segoe UI Emoji", 72))
            icon_rect = rect.adjusted(0, 20, 0, -rect.height() // 2)
            painter.drawText(icon_rect, Qt.AlignCenter, self.icon_text)
        
        painter.setFont(QFont("Arial", 24, QFont.Bold))
        painter.setPen(MBColors.WHITE)
        text_rect = rect.adjusted(0, rect.height() // 2, 0, -20)
        painter.drawText(text_rect, Qt.AlignCenter, self.text())
        
    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        self.is_pressed = True
        self.update()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        self.is_pressed = False
        self.update()
        super().mouseReleaseEvent(event)