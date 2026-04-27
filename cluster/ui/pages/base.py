from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QWidget
from ui.theme import background_brush

class BasePage(QWidget):
    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), background_brush(self.height()))
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(255,255,255,10), 1))
        for y in range(0, self.height(), 44):
            p.drawLine(0, y, self.width(), y)
        for x in range(0, self.width(), 70):
            p.drawLine(x, 0, x, self.height())
