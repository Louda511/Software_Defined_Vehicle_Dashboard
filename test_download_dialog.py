import sys
import time
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from ui.dialogs import DownloadInstallDialog

def show_success_dialog():
    dialog = DownloadInstallDialog("test-image")
    dialog.show()
    # Simulate download for 2 seconds, then show success
    QTimer.singleShot(2000, lambda: dialog.show_success("Downloaded and installed successfully!"))
    dialog.exec()

def show_error_dialog():
    dialog = DownloadInstallDialog("test-image")
    dialog.show()
    # Simulate download for 2 seconds, then show error
    QTimer.singleShot(2000, lambda: dialog.show_error("Installation failed. Please try again."))
    dialog.exec()

if __name__ == "__main__":
    from PyQt6.QtCore import QTimer
    from PyQt6.QtGui import QPainter
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)
    btn_success = QPushButton("Test Success Page")
    btn_success.clicked.connect(show_success_dialog)
    btn_error = QPushButton("Test Error Page")
    btn_error.clicked.connect(show_error_dialog)
    layout.addWidget(btn_success)
    layout.addWidget(btn_error)
    window.setWindowTitle("Download Dialog Test")
    window.resize(300, 120)
    window.show()
    sys.exit(app.exec()) 