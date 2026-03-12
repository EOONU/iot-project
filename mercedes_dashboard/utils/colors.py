"""
Color utilities
"""

from PyQt5.QtGui import QColor

def interpolate_color(color1: QColor, color2: QColor, factor: float) -> QColor:
    """Interpolate between two colors"""
    r = int(color1.red() + (color2.red() - color1.red()) * factor)
    g = int(color1.green() + (color2.green() - color1.green()) * factor)
    b = int(color1.blue() + (color2.blue() - color1.blue()) * factor)
    return QColor(r, g, b)

def get_zone_color(value: float, max_val: float, 
                   low_color=QColor(0, 185, 85),
                   mid_color=QColor(255, 160, 0),
                   high_color=QColor(220, 40, 40)) -> QColor:
    """Get color based on value zone"""
    ratio = value / max_val
    
    if ratio < 0.5:
        return interpolate_color(low_color, mid_color, ratio * 2)
    else:
        return interpolate_color(mid_color, high_color, (ratio - 0.5) * 2)