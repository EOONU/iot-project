import threading
import time
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QFont, QImage, QPainter, QPixmap, QPen
from PyQt5.QtWidgets import QLabel, QVBoxLayout
from config import ESP32_STREAM_URL, USE_ESP32, USE_CAMERA
from ui.pages.base import BasePage

class CameraPage(BasePage):
    def __init__(self, sensors):
        super().__init__()
        self.sensors = sensors
        self.cv2 = None
        self.cap = None
        self.frame = None
        self.running = False
        self.thread_started = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 26, 26, 26)
        self.label = QLabel("Camera loading...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.paint_latest_frame)
        self.timer.start(33)

    def showEvent(self, event):
        self.start_camera()
        super().showEvent(event)

    def start_camera(self):
        if self.thread_started:
            return
        if not USE_ESP32 or not USE_CAMERA:
            self.label.setText("Camera disabled in config")
            return
        self.thread_started = True
        self.running = True
        t = threading.Thread(target=self.camera_loop, daemon=True)
        t.start()

    def camera_loop(self):
        try:
            import cv2
            self.cv2 = cv2
            while self.running:
                if self.cap is None or not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(ESP32_STREAM_URL)
                    try:
                        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    except Exception:
                        pass
                    time.sleep(0.08)
                    continue

                # Grab extra frames to keep latency low.
                for _ in range(2):
                    self.cap.grab()
                ok, frame = self.cap.read()

                if ok:
                    self.frame = frame
                else:
                    try:
                        self.cap.release()
                    except Exception:
                        pass
                    self.cap = None
                    time.sleep(0.08)
        except Exception:
            self.frame = None

    def paint_latest_frame(self):
        if not USE_ESP32 or not USE_CAMERA:
            self.label.setText("Camera disabled in config")
            return
        if self.frame is None or self.cv2 is None:
            self.label.setText("Waiting for camera stream...")
            return

        frame = self.cv2.cvtColor(self.frame, self.cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(image).scaled(self.label.size(), Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 20, QFont.Bold))
        painter.drawText(20, 34, "Rear Camera")
        painter.setFont(QFont("Arial", 18, QFont.Bold))
        painter.drawText(20, 64, f"L {int(self.sensors.rear_left_distance)} cm   R {int(self.sensors.rear_right_distance)} cm")

        guide_y = pix.height() - 120
        center = pix.width() // 2
        painter.setPen(QPen(QColor(0, 170, 255, 180), 3))
        painter.drawLine(center - 160, guide_y, center - 230, pix.height() - 10)
        painter.drawLine(center + 160, guide_y, center + 230, pix.height() - 10)
        painter.drawLine(center - 90, guide_y, center - 130, pix.height() - 10)
        painter.drawLine(center + 90, guide_y, center + 130, pix.height() - 10)
        painter.end()
        self.label.setPixmap(pix)

    def closeEvent(self, event):
        self.running = False
        try:
            if self.cap is not None:
                self.cap.release()
        except Exception:
            pass
        super().closeEvent(event)
