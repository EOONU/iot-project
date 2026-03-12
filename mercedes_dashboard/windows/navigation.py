"""
Navigation window with map
"""

from PyQt5.QtWidgets import QHBoxLayout, QLabel, QFrame, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from config import WindowState
from styles import MBColors, PANEL_STYLE
from windows.base_window import BaseWindow
from widgets.map_widget import MapWidget


class NavigationWindow(BaseWindow):
    """Navigation/map view"""
    
    def __init__(self, parent=None, sensor_manager=None):
        super().__init__(parent, "Navigation")
        self.sensor_manager = sensor_manager
        
        self.setup_ui()
        
    def setup_ui(self):
        # Map and side panel container
        content_layout = QHBoxLayout()
        
        # LEFT SIDE: Map widget
        # This is where the map_widget goes - in the main content area
        self.map_widget = MapWidget(self, self.sensor_manager)
        self.map_widget.set_demo_mode(True)  # Set to False when real GPS available
        # Make map expand to fill space
        self.map_widget.setSizePolicy(
            QSizePolicy.Expanding, 
            QSizePolicy.Expanding
        )
        content_layout.addWidget(self.map_widget, stretch=3)  # stretch factor gives it more space
        
        # RIGHT SIDE: Info panel
        side_panel = QFrame()
        side_panel.setStyleSheet(PANEL_STYLE)
        side_panel.setFixedWidth(360)
        side_layout = QVBoxLayout(side_panel)
        side_layout.setSpacing(20)
        
        # Next turn section
        turn_title = QLabel("Next Turn")
        turn_title.setFont(QFont("Arial", 20, QFont.Bold))
        turn_title.setStyleSheet("color: rgb(255, 160, 0);")
        side_layout.addWidget(turn_title)
        
        # Turn direction icon
        turn_icon = QLabel("↱")
        turn_icon.setFont(QFont("Segoe UI Emoji", 64))
        turn_icon.setStyleSheet("color: white;")
        turn_icon.setAlignment(Qt.AlignCenter)
        side_layout.addWidget(turn_icon)
        
        # Distance to turn
        turn_dist = QLabel("200 m")
        turn_dist.setFont(QFont("Arial", 32, QFont.Bold))
        turn_dist.setStyleSheet("color: white;")
        turn_dist.setAlignment(Qt.AlignCenter)
        side_layout.addWidget(turn_dist)
        
        # Street name
        street = QLabel("onto Friedrichstraße")
        street.setFont(QFont("Arial", 16))
        street.setStyleSheet("color: rgb(180, 180, 185);")
        street.setAlignment(Qt.AlignCenter)
        side_layout.addWidget(street)
        
        side_layout.addSpacing(30)
        
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: rgb(72, 72, 82);")
        line.setFixedHeight(2)
        side_layout.addWidget(line)
        
        side_layout.addSpacing(20)
        
        # Route information section
        route_title = QLabel("Route Info")
        route_title.setFont(QFont("Arial", 18, QFont.Bold))
        route_title.setStyleSheet("color: rgb(215, 215, 220);")
        side_layout.addWidget(route_title)
        
        # Info items
        infos = [
            ("Destination", "Berlin Center", "🏢"),
            ("Total Distance", "45.2 km", "📏"),
            ("ETA", "12:45", "⏰"),
            ("Traffic", "Clear", "🟢"),
        ]
        
        for label, value, icon in infos:
            # Container for each info row
            row = QFrame()
            row.setStyleSheet("background-color: rgb(35, 35, 42); border-radius: 8px;")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(15, 10, 15, 10)
            
            # Icon
            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont("Segoe UI Emoji", 20))
            row_layout.addWidget(icon_lbl)
            
            # Label
            lbl = QLabel(label)
            lbl.setFont(QFont("Arial", 14))
            lbl.setStyleSheet("color: rgb(180, 180, 185);")
            row_layout.addWidget(lbl)
            
            row_layout.addStretch()
            
            # Value
            val = QLabel(value)
            val.setFont(QFont("Arial", 16, QFont.Bold))
            val.setStyleSheet("color: white;")
            row_layout.addWidget(val)
            
            side_layout.addWidget(row)
            
        side_layout.addStretch()
        
        # Zoom controls
        zoom_layout = QHBoxLayout()
        
        zoom_out = QPushButton("−")
        zoom_out.setFixedSize(50, 50)
        zoom_out.setFont(QFont("Arial", 20, QFont.Bold))
        zoom_out.setStyleSheet("""
            QPushButton {
                background-color: rgb(48, 48, 58);
                color: white;
                border-radius: 25px;
            }
            QPushButton:pressed {
                background-color: rgb(72, 72, 82);
            }
        """)
        zoom_out.clicked.connect(self.map_widget.zoom_out)
        zoom_layout.addWidget(zoom_out)
        
        zoom_in = QPushButton("+")
        zoom_in.setFixedSize(50, 50)
        zoom_in.setFont(QFont("Arial", 20, QFont.Bold))
        zoom_in.setStyleSheet("""
            QPushButton {
                background-color: rgb(48, 48, 58);
                color: white;
                border-radius: 25px;
            }
            QPushButton:pressed {
                background-color: rgb(72, 72, 82);
            }
        """)
        zoom_in.clicked.connect(self.map_widget.zoom_in)
        zoom_layout.addWidget(zoom_in)
        
        reset_btn = QPushButton("⟲")
        reset_btn.setFixedSize(50, 50)
        reset_btn.setFont(QFont("Arial", 16))
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(48, 48, 58);
                color: white;
                border-radius: 25px;
            }
            QPushButton:pressed {
                background-color: rgb(72, 72, 82);
            }
        """)
        reset_btn.clicked.connect(self.map_widget.reset_view)
        zoom_layout.addWidget(reset_btn)
        
        side_layout.addLayout(zoom_layout)
        
        # Add side panel to content layout (with less stretch)
        content_layout.addWidget(side_panel, stretch=1)
        
        # Add content layout to main layout
        self.main_layout.addLayout(content_layout)
        
        # Bottom: Back button
        self.add_back_button()
        
    def update_animation(self):
        """Update map and info"""
        # The map widget updates itself via its own timer
        # But we can update side panel info here if needed
        pass