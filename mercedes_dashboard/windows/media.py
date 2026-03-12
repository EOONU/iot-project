"""
Media player window
"""

import math
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor, QPen

from config import WindowState
from styles import MBColors, PANEL_STYLE
from windows.base_window import BaseWindow


class WaveformWidget(QFrame):
    """Animated audio waveform"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(450, 450)
        self.setStyleSheet("""
            background-color: rgb(15, 15, 20);
            border: 3px solid rgb(72, 72, 82);
            border-radius: 20px;
        """)
        self.time = 0.0
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        cy = h // 2
        
        # Draw bars
        for i in range(20):
            x = 25 + i * 20
            
            # Animated height
            height = 30 + math.sin(self.time * 5 + i * 0.5) * 25
            height = abs(height)
            
            color = MBColors.BLUE if i % 2 == 0 else MBColors.TEAL
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(x, int(cy - height/2), 15, int(height), 7, 7)
            
    def update_animation(self):
        self.time += 0.05
        self.update()


class MediaWindow(BaseWindow):
    """Media player interface"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "Media Player")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Center content
        center = QVBoxLayout()
        center.setAlignment(Qt.AlignCenter)
        
        # Album art / waveform
        self.waveform = WaveformWidget()
        center.addWidget(self.waveform, alignment=Qt.AlignCenter)
        
        # Track info
        track = QLabel("Midnight City")
        track.setFont(QFont("Arial", 32, QFont.Bold))
        track.setStyleSheet("color: white;")
        track.setAlignment(Qt.AlignCenter)
        center.addWidget(track)
        
        artist = QLabel("M83 • Hurry Up, We're Dreaming")
        artist.setFont(QFont("Arial", 20))
        artist.setStyleSheet("color: rgb(180, 180, 185);")
        artist.setAlignment(Qt.AlignCenter)
        center.addWidget(artist)
        
        # Progress
        progress_layout = QHBoxLayout()
        
        time1 = QLabel("2:34")
        time1.setFont(QFont("Arial", 16))
        time1.setStyleSheet("color: rgb(180, 180, 185);")
        progress_layout.addWidget(time1)
        
        # Progress bar (simplified)
        progress_bar = QFrame()
        progress_bar.setFixedSize(600, 8)
        progress_bar.setStyleSheet("""
            background-color: rgb(48, 48, 58);
            border-radius: 4px;
        """)
        progress_layout.addWidget(progress_bar)
        
        time2 = QLabel("4:03")
        time2.setFont(QFont("Arial", 16))
        time2.setStyleSheet("color: rgb(180, 180, 185);")
        progress_layout.addWidget(time2)
        
        center.addLayout(progress_layout)
        
        # Controls
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        buttons = [
            ("⏮", 50),
            ("⏪", 40),
            ("⏯", 70),  # Play/Pause - larger
            ("⏩", 40),
            ("⏭", 50),
        ]
        
        for icon, size in buttons:
            btn = QPushButton(icon)
            btn.setFixedSize(size * 2, size * 2)
            btn.setFont(QFont("Segoe UI Emoji", size))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgb(48, 48, 58);
                    color: white;
                    border-radius: {size}px;
                    border: 2px solid rgb(72, 72, 82);
                }}
                QPushButton:pressed {{
                    background-color: rgb(72, 72, 82);
                    border-color: rgb(255, 160, 0);
                }}
            """)
            controls.addWidget(btn)
            
        center.addLayout(controls)
        self.main_layout.addLayout(center)
        self.main_layout.addStretch()
        
        self.add_back_button()
        
    def update_animation(self):
        self.waveform.update_animation()