"""
Service for monitoring system alerts from a file
"""
from PyQt6.QtCore import QObject, QTimer, QFileSystemWatcher
from utils.file_utils import get_active_warning
from ui.alert_screen import AlertScreen

# Map parameter to warning messages: (main, advice)
ALERT_MESSAGES = {
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

class AlertService(QObject):
    """
    Monitors a JSON file for alert conditions and displays an alert dialog.
    """
    def __init__(self, json_path: str, parent=None):
        super().__init__(parent)
        self.json_path = json_path
        self.parent = parent
        self.watcher = QFileSystemWatcher([json_path])
        self.watcher.fileChanged.connect(self.on_file_changed)
        
        self.dialog = None
        self.last_warning_key = None
        
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.update_alert)
        
        # Initial check
        self.update_alert()

    def on_file_changed(self, path: str):
        """Debounce file changes to avoid rapid firing."""
        # Debounce: wait 50ms before reading the file
        self.debounce_timer.start(50)

    def update_alert(self):
        """Check for active alerts and show/hide the dialog."""
        warning_key = get_active_warning(self.json_path)
        
        if warning_key:
            main_msg, advice_msg = ALERT_MESSAGES.get(
                warning_key, ('Warning detected!', '')
            )
            
            if self.dialog is None:
                self.dialog = AlertScreen(main_msg, advice_msg, self.parent)
                self.dialog.show()
            else:
                self.dialog.set_message(main_msg, advice_msg)
                
            self.last_warning_key = warning_key
        else:
            if self.dialog is not None:
                self.dialog.close()
                self.dialog = None
            self.last_warning_key = None 