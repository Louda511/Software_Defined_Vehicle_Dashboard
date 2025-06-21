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
    """A styled dialog for showing feature info."""
    def __init__(self, feature: Feature, parent=None):
        super().__init__(parent)
        self.feature = feature
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumWidth(750)
        self.setWindowOpacity(0.0) # Start transparent for fade-in

        self._setup_ui()
        theme_manager.theme_changed.connect(self.update_styles)
        self.update_styles()

    def showEvent(self, event):
        super().showEvent(event)
        # Fade-in animation
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(300)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _get_feature_icon_path(self) -> str:
        """Helper to get the correct icon path."""
        feature_name = self.feature.name.lower()
        if 'adaptive cruise control' in feature_name:
            return 'resources/icons/adaptive-cruise.svg'
        if 'lane' in feature_name: return 'resources/icons/lane.svg'
        if 'cruise' in feature_name: return 'resources/icons/cruise.svg'
        if 'brake' in feature_name: return 'resources/icons/brake.svg'
        if 'hello' in feature_name: return 'resources/icons/hello.svg'
        if 'weather' in feature_name: return self._get_weather_icon(self.feature.short_description)
        return 'resources/icons/store.svg'

    def _setup_ui(self):
        container = QWidget()
        container.setObjectName("Container")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(container)
        
        # A single vertical layout for a centered design
        layout = QVBoxLayout(container)
        layout.setContentsMargins(35,35,35,35)
        layout.setSpacing(15)

        # Icon in the middle
        icon_container = QFrame()
        icon_container.setObjectName("IconContainer")
        icon_container.setFixedSize(140, 140) # Increased size
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0,0,0,0)
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(self.icon_label)
        layout.addWidget(icon_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Title under the icon
        title_label = QLabel(self.feature.name)
        title_label.setObjectName("InfoTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Short Description
        short_desc_label = QLabel(self.feature.short_desc)
        short_desc_label.setObjectName("InfoShortDescription")
        short_desc_label.setWordWrap(True)
        short_desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(short_desc_label)

        # Separator
        separator = QFrame()
        separator.setObjectName("Separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Long Description
        desc_label = QLabel(self.feature.long_desc)
        desc_label.setObjectName("InfoLongDescription")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # Close button at the bottom
        close_button = QPushButton("Close")
        close_button.setObjectName("CloseButton")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def update_styles(self):
        theme = theme_manager.theme
        icon_path = self._get_feature_icon_path()
        
        # Use the default theme color for the icon for high contrast
        themed_icon = get_themed_icon(icon_path)
        self.icon_label.setPixmap(themed_icon.pixmap(120, 120)) # Larger icon

        self.setStyleSheet(f"""
            #Container {{
                background-color: {theme['card_bg']};
                border-radius: 16px;
                border: 1px solid {theme['border']};
            }}
            #IconContainer {{
                background-color: {theme['background']};
                border-radius: 70px; /* Half of width/height for a perfect circle */
                border: 1px solid {theme['border']};
            }}
            #InfoTitle {{
                font-size: 30px;
                font-weight: bold;
                color: {theme['text']};
                padding-top: 10px;
            }}
            #InfoShortDescription {{
                font-size: 18px;
                font-style: italic;
                color: {theme['text_secondary']};
                padding-bottom: 15px;
            }}
            #Separator {{
                background-color: {theme['accent']};
                height: 1px;
            }}
            #InfoLongDescription {{
                font-size: 16px;
                color: {theme['text']};
            }}
            #CloseButton {{
                background-color: {theme['accent']};
                color: {theme.get('card_bg', '#FFFFFF')};
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }}
            #CloseButton:hover {{
                background-color: {theme['accent_hover']};
            }}
        """) 