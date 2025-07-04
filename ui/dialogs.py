"""
Dialog components for the ADAS App Store
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QHBoxLayout, QPushButton, QWidget, QFrame, QProgressBar, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QPixmap, QFont, QIcon, QPainter, QColor
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
    """Modern dialog for showing download and installation progress"""
    
    def __init__(self, image_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Downloading and Installing')
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setMinimumHeight(300)
        # Frameless window for a modern look
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.image_name = image_name
        self.worker = None
        self._setup_ui()
        self.update_styles()
    
    def _setup_ui(self):
        """Setup the modern dialog UI"""
        layout = QVBoxLayout()
        layout.setSpacing(24)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Centered Title and Subtitle
        self.title_label = QLabel("Downloading your feature")
        self.title_label.setObjectName("DownloadTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label = QLabel("")
        self.subtitle_label.setObjectName("DownloadSubtitle")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtitle_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Progress section
        self.progress_frame = QFrame()
        self.progress_frame.setObjectName("ProgressFrame")
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setSpacing(16)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("ProgressBar")
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        # Status message
        self.status_label = QLabel("Downloading your feature")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(self.progress_frame)
        
        # Success/Error message (initially hidden)
        self.result_frame = QFrame()
        self.result_frame.setObjectName("ResultFrame")
        self.result_frame.setVisible(False)
        result_layout = QVBoxLayout(self.result_frame)
        
        self.result_icon = QLabel()
        self.result_icon.setFixedSize(48, 48)
        self.result_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_icon.setObjectName("ResultIcon")
        result_layout.addWidget(self.result_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.result_message = QLabel()
        self.result_message.setObjectName("ResultMessage")
        self.result_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_message.setWordWrap(True)
        result_layout.addWidget(self.result_message)
        
        layout.addWidget(self.result_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("CancelButton")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        self.close_button = QPushButton("Close")
        self.close_button.setObjectName("CloseButton")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setVisible(False)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Add drop shadow to dialog
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        
        self.result_frame.setWindowOpacity(0)
        self.result_fade_anim = QPropertyAnimation(self.result_frame, b"windowOpacity")
        self.result_fade_anim.setDuration(400)
        self.result_fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def update_styles(self):
        """Update the dialog styles based on current theme"""
        theme = theme_manager.theme
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['card_bg']};
                color: {theme['text']};
                border-radius: 16px;
                border: 1px solid {theme['border']};
            }}
            
            #DownloadTitle {{
                font-size: 24px;
                font-weight: bold;
                color: {theme['text']};
                margin-bottom: 4px;
            }}
            
            #DownloadSubtitle {{
                font-size: 14px;
                color: {theme['text_secondary']};
            }}
            
            #ProgressFrame {{
                background-color: {theme['background']};
                border-radius: 12px;
                padding: 20px;
                border: 1px solid {theme['border']};
            }}
            
            #ProgressBar {{
                border: 2px solid {theme['border']};
                border-radius: 8px;
                background-color: {theme['card_bg']};
                height: 12px;
                text-align: center;
            }}
            
            #ProgressBar::chunk {{
                background-color: {theme['accent']};
                border-radius: 6px;
                margin: 1px;
            }}
            
            #StatusLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {theme['text']};
                margin-top: 16px;
            }}
            
            #ResultFrame {{
                background-color: {theme['background']};
                border-radius: 12px;
                padding: 20px;
                border: 1px solid {theme['border']};
            }}
            
            #ResultMessage {{
                font-size: 16px;
                font-weight: bold;
                margin-top: 12px;
            }}
            
            #CancelButton, #CloseButton {{
                background-color: {theme['accent']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }}
            
            #CancelButton:hover, #CloseButton:hover {{
                background-color: {theme['accent_hover']};
            }}
            
            #CancelButton:pressed, #CloseButton:pressed {{
                background-color: {theme['accent']};
            }}
        """)
    
    def set_status(self, text: str):
        """Update the status text - always show 'Downloading your feature'"""
        self.status_label.setText("Downloading your feature")
    
    def colorize_svg_icon(self, svg_path, color, size=48):
        """Load an SVG icon and tint it with the given color, returning a QPixmap."""
        renderer = QSvgRenderer(svg_path)
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(color))
        painter.end()
        return pixmap
    
    def show_success(self, message: str):
        """Show success state"""
        self.progress_frame.setVisible(False)
        self.result_frame.setVisible(True)
        self.result_fade_anim.setStartValue(0)
        self.result_fade_anim.setEndValue(1)
        self.result_fade_anim.start()
        
        # Use a modern checkmark icon and tint it green
        check_icon_path = 'resources/icons/checkmark.svg'
        if os.path.exists(check_icon_path):
            pixmap = QPixmap(check_icon_path)
            self.result_icon.setPixmap(pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.result_icon.setPixmap(get_themed_icon('resources/icons/hello.svg').pixmap(48, 48))
        
        self.result_message.setText("Downloaded and installed successfully!")
        self.result_message.setStyleSheet(f"color: {theme_manager.theme['success']};")
        
        self.cancel_button.setVisible(False)
        self.close_button.setVisible(True)
        
        self.title_label.setText("Installation Complete!")
        self.title_label.setFont(QFont('Segoe UI', 24, QFont.Weight.Bold))
        self.subtitle_label.setText("Your ADAS service is ready to use.")
        self.subtitle_label.setFont(QFont('Segoe UI', 14))
    
    def show_error(self, message: str):
        """Show error state"""
        self.progress_frame.setVisible(False)
        self.result_frame.setVisible(True)
        self.result_fade_anim.setStartValue(0)
        self.result_fade_anim.setEndValue(1)
        self.result_fade_anim.start()
        
        # Use a modern warning icon and tint it orange/red
        warn_icon_path = 'resources/icons/warning.svg'
        error_color = theme_manager.theme['error'] if 'error' in theme_manager.theme else '#ff6b6b'
        if os.path.exists(warn_icon_path):
            pixmap = self.colorize_svg_icon(warn_icon_path, error_color)
            self.result_icon.setPixmap(pixmap)
        else:
            self.result_icon.setPixmap(get_themed_icon('resources/icons/brake.svg').pixmap(48, 48))
        
        self.result_message.setText("Installation failed. Please try again.")
        self.result_message.setStyleSheet(f"color: {error_color};")
        
        self.cancel_button.setVisible(False)
        self.close_button.setVisible(True)
        
        self.title_label.setText("Installation Failed")
        self.title_label.setFont(QFont('Segoe UI', 24, QFont.Weight.Bold))
        self.subtitle_label.setText("There was an issue with the installation.")
        self.subtitle_label.setFont(QFont('Segoe UI', 14))
    
    def start_worker(self, url: str, main_window, on_finish_callback=None):
        """Start the Podman worker thread"""
        self.worker = PodmanWorker(url)
        self.worker.status_update.connect(self.set_status)
        
        def on_finish(success: bool, msg: str):
            if success:
                self.show_success("Downloaded and installed successfully!")
            else:
                self.show_error(f"Installation failed: {msg}")
            
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