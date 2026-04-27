from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QGraphicsOpacityEffect
from ui.pages.cluster import ClusterPage
from ui.pages.navigation_page import NavigationPage
from ui.pages.trip_page import TripPage
from ui.pages.service_page import ServicePage
from ui.pages.sensors_page import SensorsPage
from ui.pages.reverse_page import ReversePage
from ui.pages.camera_page import CameraPage

class DashboardWindow(QWidget):
    def __init__(self, sensors):
        super().__init__()
        self.sensors = sensors
        self.start_x = 0
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet('''
            QWidget { color: white; font-family: Arial; background: transparent; }
            QPushButton {
                background-color: rgba(255,255,255,20);
                border: 1px solid rgba(255,255,255,35);
                border-radius: 18px;
                padding: 10px 16px;
                color: white;
                font-size: 16px;
            }
            QPushButton:pressed { background-color: rgba(255,255,255,38); }
        ''')

        self.stack = QStackedWidget()
        for page in [
            ClusterPage(sensors),
            NavigationPage(sensors),
            TripPage(sensors),
            ServicePage(sensors),
            SensorsPage(sensors),
            ReversePage(sensors),
            CameraPage(sensors),
        ]:
            self.stack.addWidget(page)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.opacity_effect = QGraphicsOpacityEffect(self.stack)
        self.stack.setGraphicsEffect(self.opacity_effect)

        # Auto switching to reverse assist is disabled.
        # User changes pages manually only.

    def animate_to(self, index):
        if index == self.stack.currentIndex():
            return
        self.fade = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.fade.setDuration(160)
        self.fade.setStartValue(1.0)
        self.fade.setKeyValueAt(0.45, 0.2)
        self.fade.setEndValue(1.0)
        self.fade.setEasingCurve(QEasingCurve.InOutCubic)
        self.fade.finished.connect(lambda: self.stack.setCurrentIndex(index))
        self.fade.start()

    def mousePressEvent(self, event):
        self.start_x = event.x()

    def mouseReleaseEvent(self, event):
        delta = event.x() - self.start_x
        if delta > 80:
            self.animate_to((self.stack.currentIndex() - 1) % self.stack.count())
        elif delta < -80:
            self.animate_to((self.stack.currentIndex() + 1) % self.stack.count())
