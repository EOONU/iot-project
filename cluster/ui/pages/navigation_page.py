from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton
from ui.pages.base import BasePage
from services.map_service import MapService

class NavigationPage(BasePage):
    def __init__(self, sensors):
        super().__init__()
        self.sensors = sensors
        self.map_service = MapService()
        self.map_label = QLabel(self)
        self.map_label.setScaledContents(True)

        self.zoom_in_btn = QPushButton("+", self)
        self.zoom_out_btn = QPushButton("-", self)
        self.center_btn = QPushButton("Center", self)
        self.auto_zoom_btn = QPushButton("Auto Zoom", self)

        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.center_btn.clicked.connect(self.center_on_gps)
        self.auto_zoom_btn.clicked.connect(self.toggle_auto_zoom)

        self.follow_gps = True
        self.auto_zoom = True
        self.center_lat = sensors.latitude
        self.center_lon = sensors.longitude
        self.dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_map)
        self.timer.start(650)

    def resizeEvent(self, event):
        self.map_label.setGeometry(26, 86, self.width() - 52, self.height() - 120)
        bx = self.width() - 312
        self.zoom_in_btn.setGeometry(bx, 26, 50, 42)
        self.zoom_out_btn.setGeometry(bx + 58, 26, 50, 42)
        self.center_btn.setGeometry(bx + 116, 26, 84, 42)
        self.auto_zoom_btn.setGeometry(bx + 208, 26, 104, 42)
        super().resizeEvent(event)

    def _apply_auto_zoom(self):
        s = int(self.sensors.speed)
        if s < 20:
            self.map_service.set_zoom(15)
        elif s < 60:
            self.map_service.set_zoom(13)
        elif s < 100:
            self.map_service.set_zoom(12)
        else:
            self.map_service.set_zoom(10)

    def zoom_in(self):
        self.auto_zoom = False
        self.map_service.set_zoom(self.map_service.zoom + 1)
        self.refresh_map()

    def zoom_out(self):
        self.auto_zoom = False
        self.map_service.set_zoom(self.map_service.zoom - 1)
        self.refresh_map()

    def center_on_gps(self):
        self.follow_gps = True
        self.center_lat = self.sensors.latitude
        self.center_lon = self.sensors.longitude
        self.refresh_map()

    def toggle_auto_zoom(self):
        self.auto_zoom = not self.auto_zoom
        self.refresh_map()

    def refresh_map(self):
        if self.follow_gps:
            self.center_lat = self.sensors.latitude
            self.center_lon = self.sensors.longitude
        if self.auto_zoom:
            self._apply_auto_zoom()

        w = max(200, self.map_label.width())
        h = max(200, self.map_label.height())
        img = self.map_service.render(self.center_lat, self.center_lon, w, h)
        self.map_label.setPixmap(QPixmap.fromImage(img))
        self.update()

    def mousePressEvent(self, event):
        if self.map_label.geometry().contains(event.pos()):
            self.dragging = True
            self.follow_gps = False
            self.last_mouse_x = event.x()
            self.last_mouse_y = event.y()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            dx = event.x() - self.last_mouse_x
            dy = event.y() - self.last_mouse_y
            self.center_lat, self.center_lon = self.map_service.pan(self.center_lat, self.center_lon, dx, dy)
            self.last_mouse_x = event.x()
            self.last_mouse_y = event.y()
            self.refresh_map()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Arial", 34, QFont.Bold))
        p.drawText(36, 56, "Navigation")
        p.setPen(QColor(180, 188, 198))
        p.setFont(QFont("Arial", 16))
        mode = "FOLLOW GPS" if self.follow_gps else "MANUAL PAN"
        zoom_mode = "AUTO ZOOM" if self.auto_zoom else "MANUAL ZOOM"
        p.drawText(36, 82, f"{self.center_lat:.5f}, {self.center_lon:.5f}   Heading {int(self.sensors.heading)}°   Speed {int(self.sensors.speed)} km/h   {mode}   {zoom_mode}")
