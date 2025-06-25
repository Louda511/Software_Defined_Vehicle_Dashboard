"""
Dialog components for the ADAS App Store
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QHBoxLayout, QPushButton, QWidget, QFrame
)
from PyQt6.QtGui import QPixmap, QFont, QIcon, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QByteArray
from models.feature import Feature
from services.podman_service import PodmanWorker
from .styles import theme_manager
from .icon_utils import get_themed_icon
import os


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


class InfoDialog(QDialog):
    """A robust, modern, and scalable dialog for showing feature info."""
    ICON_KEYWORDS = {
        'adaptive cruise': 'adaptive-cruise.svg',
        'lane': 'lane.svg',
        'cruise': 'cruise.svg',
        'brake': 'brake.svg',
        'hello': 'hello.svg',
        'weather': 'weather-clear.svg',
        'store': 'store.svg',
    }

    def __init__(self, feature: Feature, parent=None):
        super().__init__(parent)
        self.feature = feature
        # Frameless window for a modern look
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(420)
        self._setup_ui()
        self.update_styles()

    def _get_feature_icon_path(self) -> str:
        icon_path = self.feature.icon
        if icon_path and os.path.exists(icon_path):
            return icon_path
        name = self.feature.name.lower()
        icon_path_lower = icon_path.lower() if icon_path else ''
        for keyword, icon_file in self.ICON_KEYWORDS.items():
            if keyword in name or keyword in icon_path_lower:
                return f'resources/icons/{icon_file}'
        return 'resources/icons/store.svg'

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(48, 48, 48, 48)

        # Icon in a circle
        icon_circle = QFrame()
        icon_circle.setObjectName("IconCircle")
        icon_circle.setFixedSize(140, 140)
        icon_circle_layout = QVBoxLayout(icon_circle)
        icon_circle_layout.setContentsMargins(0, 0, 0, 0)
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(90, 90)
        icon_circle_layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_circle, alignment=Qt.AlignmentFlag.AlignCenter)

        # Title
        title_label = QLabel(self.feature.name)
        title_label.setObjectName("InfoTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Short Description (italic subtitle)
        short_desc_label = QLabel(self.feature.short_desc)
        short_desc_label.setObjectName("InfoShortDescription")
        short_desc_label.setWordWrap(True)
        short_desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(short_desc_label)

        # Separator (thin colored line)
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName("Separator")
        layout.addWidget(separator)

        # Long Description (left-aligned)
        desc_label = QLabel(self.feature.long_desc)
        desc_label.setObjectName("InfoLongDescription")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(desc_label)

        layout.addStretch()

        # Close button (wide, rounded, centered)
        close_button = QPushButton("Close")
        close_button.setObjectName("CloseButton")
        close_button.clicked.connect(self.accept)
        close_button.setMinimumWidth(180)
        close_button.setMinimumHeight(44)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def update_styles(self):
        theme = theme_manager.theme
        icon_path = self._get_feature_icon_path()
        themed_icon = get_themed_icon(icon_path)
        self.icon_label.setPixmap(themed_icon.pixmap(90, 90))
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['card_bg']};
                color: {theme['text']};
                border-radius: 28px;
                border: none;
                padding: 0px;
            }}
            #IconCircle {{
                background-color: {theme['background']};
                border-radius: 70px;
                border: 2px solid {theme['border']};
            }}
            #InfoTitle {{
                font-size: 32px;
                font-weight: bold;
                color: {theme['text']};
                margin-bottom: 8px;
            }}
            #InfoShortDescription {{
                font-size: 18px;
                font-style: italic;
                color: {theme['text_secondary']};
                margin-bottom: 12px;
            }}
            #Separator {{
                background-color: {theme['accent']};
                height: 2px;
                margin: 10px 0 18px 0;
            }}
            #InfoLongDescription {{
                font-size: 16px;
                color: {theme['text']};
                margin-bottom: 10px;
            }}
            #CloseButton {{
                background-color: {theme['accent']};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 36px;
                font-size: 18px;
                font-weight: bold;
                min-width: 180px;
            }}
            #CloseButton:hover {{
                background-color: {theme['accent_hover']};
            }}
        """) 