
import sys
from PyQt5.QtWidgets import QApplication
from app.ui.dashboard import DashboardWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.showFullScreen()
    sys.exit(app.exec_())
    
    
        
