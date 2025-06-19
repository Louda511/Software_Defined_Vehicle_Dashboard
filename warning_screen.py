import json
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QFileSystemWatcher, QObject, QTimer
import sys

class WarningScreen(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Warning!')
        self.setModal(True)
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        self.label = QLabel(message)
        self.label.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        self.setLayout(layout)
    def set_message(self, message):
        self.label.setText(message)

# Map parameter to warning message
WARNING_MESSAGES = {
    'drowsy': 'Drowsiness detected! Please stay alert.',
    'distracted': 'Distraction detected! Please focus on the road.',
    'yawning': 'Yawning detected! Please take a break if needed.'
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
            message = WARNING_MESSAGES.get(warning_key, 'Warning detected!')
            if self.dialog is None:
                self.dialog = WarningScreen(message, self.parent)
                self.dialog.show()
            else:
                self.dialog.set_message(message)
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