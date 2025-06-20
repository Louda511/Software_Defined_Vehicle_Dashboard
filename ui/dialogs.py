"""
Dialog components for the ADAS App Store
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QHBoxLayout
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
from models.feature import Feature
from services.podman_service import PodmanWorker


class FeatureDialog(QDialog):
    """Dialog for displaying detailed feature information"""
    
    def __init__(self, feature: Feature, parent=None):
        super().__init__(parent)
        self.setWindowTitle(feature.name)
        self.setMinimumWidth(350)
        self._setup_ui(feature)
    
    def _setup_ui(self, feature: Feature):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Icon
        icon = QLabel()
        pixmap = QPixmap(feature.icon)
        icon.setPixmap(pixmap.scaled(
            64, 64, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)
        
        # Description
        desc = QLabel(feature.long_desc)
        desc.setWordWrap(True)
        desc.setFont(QFont('Segoe UI', 11))
        layout.addWidget(desc)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setLayout(layout)


class DownloadInstallDialog(QDialog):
    """Dialog for showing download and installation progress"""
    
    def __init__(self, image_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Downloading and Installing')
        self.setModal(True)
        self.setMinimumWidth(350)
        self.image_name = image_name
        self.worker = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Spinner
        self.spinner = QLabel()
        self.spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner.setText('⏳')
        layout.addWidget(self.spinner)
        
        # Status label
        self.status_label = QLabel('Starting...')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def set_status(self, text: str):
        """Update the status text"""
        self.status_label.setText(text)
    
    def start_worker(self, url: str, main_window, on_finish_callback=None):
        """Start the Podman worker thread"""
        self.worker = PodmanWorker(url)
        self.worker.status_update.connect(self.set_status)
        
        def on_finish(success: bool, msg: str):
            self.set_status(msg)
            self.accept()
            main_window.show()
            if on_finish_callback:
                on_finish_callback(success)
        
        self.worker.finished.connect(on_finish)
        self.worker.start() 