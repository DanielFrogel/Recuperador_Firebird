import sys
from PyQt6.QtWidgets import QApplication
from models.windows import MainWindow, dark_fusion_style

# Starts the application and creates the main window
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dark_fusion_style(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
