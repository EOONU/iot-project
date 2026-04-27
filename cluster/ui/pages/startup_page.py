from PyQt5.QtCore import QEasingCurve, QParallelAnimationGroup, QPropertyAnimation, QRect, Qt, QTimer, pyqtProperty
from PyQt5.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen, QBrush
from PyQt5.QtWidgets import QWidget

class StartupPage(QWidget):
    def __init__(self, finished_callback):
        super().__init__()
        self.finished_callback = finished_callback
        self._ring_progress = 0.0
        self._logo_opacity = 0.0
        self._subtitle_opacity = 0.0
        self._flash = 0.0

        self.group = QParallelAnimationGroup(self)
        for name, dur, end in [("ringProgress",1600,1.0),("logoOpacity",1000,1.0),("subtitleOpacity",1400,1.0)]:
            anim = QPropertyAnimation(self, bytes(name, "utf-8"))
            anim.setDuration(dur)
            anim.setStartValue(0.0)
            anim.setEndValue(end)
            anim.setEasingCurve(QEasingCurve.InOutCubic)
            self.group.addAnimation(anim)

        flash_anim = QPropertyAnimation(self, b"flash")
        flash_anim.setDuration(800)
        flash_anim.setStartValue(0.0)
        flash_anim.setKeyValueAt(0.5,1.0)
        flash_anim.setEndValue(0.0)
        flash_anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.group.addAnimation(flash_anim)

        self.group.start()
        QTimer.singleShot(2100, self.finish)

    def finish(self):
        self.close()
        self.finished_callback()

    def get_ring_progress(self): return self._ring_progress
    def set_ring_progress(self, v): self._ring_progress = float(v); self.update()
    ringProgress = pyqtProperty(float, get_ring_progress, set_ring_progress)

    def get_logo_opacity(self): return self._logo_opacity
    def set_logo_opacity(self, v): self._logo_opacity = float(v); self.update()
    logoOpacity = pyqtProperty(float, get_logo_opacity, set_logo_opacity)

    def get_subtitle_opacity(self): return self._subtitle_opacity
    def set_subtitle_opacity(self, v): self._subtitle_opacity = float(v); self.update()
    subtitleOpacity = pyqtProperty(float, get_subtitle_opacity, set_subtitle_opacity)

    def get_flash(self): return self._flash
    def set_flash(self, v): self._flash = float(v); self.update()
    flash = pyqtProperty(float, get_flash, set_flash)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor(2, 3, 8))
        grad.setColorAt(0.5, QColor(7, 12, 24))
        grad.setColorAt(1.0, QColor(3, 4, 7))
        p.fillRect(self.rect(), QBrush(grad))
        cx, cy = self.width() // 2, self.height() // 2 - 10
        p.setPen(QPen(QColor(0, 170, 255, int(70 + 70 * self._flash)), 26))
        p.drawEllipse(cx - 150, cy - 150, 300, 300)
        p.setPen(QPen(QColor(255, 255, 255, 28), 18))
        p.drawEllipse(cx - 150, cy - 150, 300, 300)
        p.setPen(QPen(QColor(0, 180, 255, 220), 12))
        p.drawArc(cx - 132, cy - 132, 264, 264, 90 * 16, int(-360 * 16 * self._ring_progress))
        p.setOpacity(self._logo_opacity)
        p.setPen(QColor(245, 248, 250))
        p.setFont(QFont("Arial", 56, QFont.Bold))
        p.drawText(QRect(cx - 140, cy - 40, 280, 80), Qt.AlignCenter, "AMG")
        p.setOpacity(self._subtitle_opacity)
        p.setPen(QColor(190, 198, 208))
        p.setFont(QFont("Arial", 18))
        p.drawText(QRect(cx - 220, cy + 60, 440, 40), Qt.AlignCenter, "Performance Cluster Initialising")
