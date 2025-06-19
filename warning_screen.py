import json
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication, QHBoxLayout, QPushButton, QDialogButtonBox, QWidget
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt, QFileSystemWatcher, QObject, QTimer
import sys

class WarningScreen(QDialog):
    def __init__(self, main_message, advice_message, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Warning!')
        self.setModal(True)
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        # Header
        header = QWidget()
        header_layout = QHBoxLayout()
        header.setStyleSheet('background-color: #e53935; border-top-left-radius: 8px; border-top-right-radius: 8px;')
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(16, 16))  # Placeholder for icon
        icon_label.setText('⚠️')
        icon_label.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        icon_label.setStyleSheet('color: white;')
        header_layout.addStretch()
        header_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        caution_label = QLabel('CAUTION')
        caution_label.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        caution_label.setStyleSheet('color: white; margin-left: 8px;')
        header_layout.addWidget(caution_label, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addStretch()
        header.setLayout(header_layout)
        layout.addWidget(header)
        # Main message
        self.main_label = QLabel(main_message)
        self.main_label.setFont(QFont('Segoe UI', 15, QFont.Weight.Bold))
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_label.setWordWrap(True)
        layout.addWidget(self.main_label)
        # Advice message
        self.advice_label = QLabel(advice_message)
        self.advice_label.setFont(QFont('Segoe UI', 11))
        self.advice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.advice_label.setWordWrap(True)
        layout.addWidget(self.advice_label)
        self.setLayout(layout)
    def set_message(self, main_message, advice_message):
        self.main_label.setText(main_message)
        self.advice_label.setText(advice_message)

# Map parameter to warning messages: (main, advice)
WARNING_MESSAGES = {
    'drowsy': (
        'Drowsiness Detected!',
        'Please stay alert and take a break if needed.'
    ),
    'distracted': (
        'Distraction Detected!',
        'Please focus on the road and avoid distractions.'
    ),
    'yawning': (
        'Yawning Detected!',
        'Consider taking a break to rest.'
    )
}

def get_active_warning(json_path):
    """
    Returns the first active warning key if any, else None.
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        for key in ['drowsy', 'distracted', 'yawning']:
            if data.get(key, False) is True:
                return key
        return None
    except (json.JSONDecodeError, FileNotFoundError):
        # Suppress transient errors due to file being written
        return None
    except Exception as e:
        print(f"Error reading warning data: {e}")
        return None

class WarningFileWatcher(QObject):
    def __init__(self, json_path, parent=None):
        super().__init__(parent)
        self.json_path = json_path
        self.parent = parent
        self.watcher = QFileSystemWatcher([json_path])
        self.watcher.fileChanged.connect(self.on_file_changed)
        self.dialog = None
        self.last_warning_key = None
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.update_warning)
        # Initial check
        self.update_warning()

    def on_file_changed(self, path):
        # Debounce: wait 50ms before reading the file
        self.debounce_timer.start(50)

    def update_warning(self):
        warning_key = get_active_warning(self.json_path)
        if warning_key:
            main_msg, advice_msg = WARNING_MESSAGES.get(
                warning_key, ('Warning detected!', '')
            )
            if self.dialog is None:
                self.dialog = WarningScreen(main_msg, advice_msg, self.parent)
                self.dialog.show()
            else:
                self.dialog.set_message(main_msg, advice_msg)
            self.last_warning_key = warning_key
        else:
            if self.dialog is not None:
                self.dialog.close()
                self.dialog = None
            self.last_warning_key = None

# Example usage (standalone test)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    watcher = WarningFileWatcher('resources/results.json')
    print("Watching for warnings. Modify the file to trigger a warning dialog.")
    sys.exit(app.exec()) 