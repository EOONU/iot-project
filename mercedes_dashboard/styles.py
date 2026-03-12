"""
Qt Stylesheets and color definitions
"""

from PyQt5.QtGui import QColor

class MBColors:
    """Mercedes-Benz Night Edition Colors"""
    BG = QColor(5, 5, 8)
    DEEP_GRAY = QColor(15, 15, 20)
    PANEL_GRAY = QColor(28, 28, 35)
    SURFACE_GRAY = QColor(48, 48, 58)
    BORDER_GRAY = QColor(72, 72, 82)
    SILVER = QColor(180, 180, 185)
    PLATINUM = QColor(215, 215, 220)
    WHITE = QColor(255, 255, 255)
    AMBER = QColor(255, 160, 0)
    RED = QColor(220, 40, 40)
    BLUE = QColor(0, 130, 210)
    GREEN = QColor(0, 185, 85)
    TEAL = QColor(0, 175, 165)
    PURPLE = QColor(145, 75, 205)

# Main application stylesheet
MAIN_STYLE = """
    QWidget {
        background-color: rgb(5, 5, 8);
        color: rgb(255, 255, 255);
        font-family: Arial;
    }
    
    QLabel {
        background: transparent;
        border: none;
    }
"""

BUTTON_STYLE = """
    QPushButton {
        background-color: rgb(28, 28, 35);
        border: 2px solid rgb(72, 72, 82);
        border-radius: 16px;
        color: white;
        font-size: 24px;
        font-weight: bold;
        padding: 20px;
    }
    
    QPushButton:pressed {
        background-color: rgb(48, 48, 58);
        border: 3px solid rgb(255, 160, 0);
    }
    
    QPushButton:hover {
        background-color: rgb(35, 35, 42);
    }
"""

PANEL_STYLE = """
    QFrame {
        background-color: rgb(28, 28, 35);
        border: 2px solid rgb(72, 72, 82);
        border-radius: 12px;
    }
"""