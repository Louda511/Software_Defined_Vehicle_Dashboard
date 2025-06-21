"""
Service for monitoring system alerts from a file
"""
from PyQt6.QtCore import QObject, QTimer, QFileSystemWatcher
from utils.file_utils import get_active_warnings
from ui.alert_screen import AlertScreen
import json

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

# Priority order: drowsy (highest) -> distracted -> yawning (lowest)
WARNING_PRIORITY = ['drowsy', 'distracted', 'yawning']

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
        self.last_warning_keys = set()
        
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
        active_warnings = get_active_warnings(self.json_path)
        current_warning_keys = set(active_warnings)
        
        # Check if all warnings are explicitly set to false
        all_warnings_cleared = self._are_all_warnings_cleared()
        
        if active_warnings:
            # Get the highest priority warning
            highest_priority_warning = self._get_highest_priority_warning(active_warnings)
            
            if highest_priority_warning:
            main_msg, advice_msg = ALERT_MESSAGES.get(
                    highest_priority_warning, ('Warning detected!', '')
            )
            
            if self.dialog is None:
                self.dialog = AlertScreen(main_msg, advice_msg, self.parent)
                self.dialog.show()
            else:
                self.dialog.set_message(main_msg, advice_msg)
                
            self.last_warning_keys = current_warning_keys
        elif all_warnings_cleared:
            # Only dismiss if all warnings are explicitly set to false
            if self.dialog is not None:
                self.dialog.close()
                self.dialog = None
            self.last_warning_keys = set()
        # If warnings are not detected but not explicitly cleared, keep the dialog open

    def _get_highest_priority_warning(self, active_warnings: list) -> str | None:
        """Get the highest priority warning from the list of active warnings."""
        for priority_warning in WARNING_PRIORITY:
            if priority_warning in active_warnings:
                return priority_warning
        return active_warnings[0] if active_warnings else None

    def _are_all_warnings_cleared(self) -> bool:
        """Check if all warnings are explicitly set to false in the JSON file."""
        try:
            with open(self.json_path, 'r') as f:
                data = json.load(f)
            
            # Check if all warning keys are explicitly set to false
            for key in ['drowsy', 'distracted', 'yawning']:
                if data.get(key) is not False:  # Not explicitly false
                    return False
            return True
        except (json.JSONDecodeError, FileNotFoundError):
            return False
        except Exception as e:
            print(f"Error checking warning states: {e}")
            return False 