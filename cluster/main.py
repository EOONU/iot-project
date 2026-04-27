import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from sensors.sensor_manager import SensorManager
from ui.main_window import DashboardWindow
from ui.pages.startup_page import StartupPage

def main():
    app = QApplication(sys.argv)
    sensors = SensorManager()
    dashboard = DashboardWindow(sensors)

    def open_dashboard():
        dashboard.showFullScreen()
        QTimer.singleShot(200, sensors.start)

    startup = StartupPage(open_dashboard)
    startup.showFullScreen()

    code = app.exec_()
    sensors.stop()
    sys.exit(code)

if __name__ == "__main__":
    main()
