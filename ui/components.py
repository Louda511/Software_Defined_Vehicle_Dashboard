"""
UI components for the ADAS App Store
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, 
    QScrollArea, QHBoxLayout, QFrame, QStackedWidget, QDialog, 
    QDialogButtonBox
)
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt, QSize, QThread, QPropertyAnimation, QEasingCurve, QRect, QTimer
from models.feature import Feature
from ui.dialogs import FeatureDialog, DownloadInstallDialog
from utils.file_utils import extract_image_name, save_installed_images
from .widgets import ClockWidget, WeatherWidget
from .styles import theme_manager
from .icon_utils import get_themed_icon
from PyQt6.QtCore import pyqtSignal
from services.podman_service import PodmanWorker


class FeatureCard(QFrame):
    """A card widget for displaying feature information"""
    
    def __init__(self, feature: Feature, installed_images: set, parent=None):
        super().__init__(parent)
        self.feature = feature
        self.installed_images = installed_images
        self._setup_ui()
        self._check_installed_state()
        theme_manager.theme_changed.connect(self._update_icons)

    def _setup_ui(self):
        """Setup the feature card UI"""
        self.setObjectName("FeatureCard")
        self.setFixedSize(600, 220)
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        layout.addStretch()
        
        # Icon section
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(64, 64)
        layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add extra space after icon
        layout.addSpacing(8)
        
        # Title
        title = QLabel(self.feature.name)
        title.setObjectName("FeatureTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # Description
        desc = QLabel(self.feature.short_desc)
        desc.setObjectName("FeatureDesc")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        button_layout.addStretch()
        self.info_btn = QPushButton("Info")
        self.info_btn.setObjectName("InfoButton")
        self.info_btn.clicked.connect(self.show_info)
        button_layout.addWidget(self.info_btn)
        
        self.download_btn = QPushButton("Download")
        self.download_btn.setObjectName("DownloadButton")
        self.download_btn.clicked.connect(self.download_feature)
        button_layout.addWidget(self.download_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        layout.addStretch()
        
        self.setLayout(layout)
        self._update_icons()

    def _get_feature_icon(self) -> str:
        """Get the appropriate icon path for the feature"""
        feature_name = self.feature.name.lower()
        if 'lane' in feature_name:
            return 'resources/icons/lane.svg'
        elif 'cruise' in feature_name:
            return 'resources/icons/cruise.svg'
        elif 'hello' in feature_name:
            return 'resources/icons/hello.svg'
        else:
            # Default icon
            return 'resources/icons/store.svg'

    def _update_icons(self):
        """Update the feature icon based on current theme"""
        icon_path = self._get_feature_icon()
        self.icon_label.setPixmap(get_themed_icon(icon_path).pixmap(64, 64))

    def _check_installed_state(self):
        """Check if this feature is already installed"""
        if self.feature.image_name in self.installed_images:
            self.set_installed()

    def set_installed(self):
        """Mark the feature as installed"""
        self.download_btn.setText("Installed")
        self.download_btn.setEnabled(False)
        self.download_btn.setObjectName("InstalledButton")

    def show_info(self):
        """Show detailed information about the feature in full-screen view"""
        main_window = self.window()
        if hasattr(main_window, 'show_info_view'):
            main_window.show_info_view(self.feature)

    def download_feature(self):
        """Download and install the feature"""
        if not self.feature.location:
            return
            
        main_window = self.window()
        main_window.hide()
        
        dialog = DownloadInstallDialog(self.feature.image_name, main_window)
        
        def after_install(success: bool):
            if success:
                self.installed_images.add(self.feature.image_name)
                self.set_installed()
        
        dialog.start_worker(self.feature.location, main_window, after_install)
        dialog.exec()


class StoreView(QWidget):
    """Store view with feature cards"""
    
    def __init__(self, features: list, installed_images: set, dashboard=None):
        super().__init__()
        self.setObjectName("StoreView")
        self.features = features
        self.installed_images = installed_images
        self.dashboard = dashboard
        self._cards = []  # To hold card widgets for animation
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the store view UI"""
        layout = QVBoxLayout()
        title = QLabel('ADAS App Store')
        font = QFont()
        font.setPointSize(20)
        font.setWeight(QFont.Weight.Bold)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("margin: 12px 0;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        grid = QGridLayout()
        grid.setSpacing(24)
        for i, feature in enumerate(self.features):
            card = FeatureCard(feature, self.installed_images)
            grid.addWidget(card, i // 2, i % 2)
            self._cards.append(card)
        
        # Align grid to the top to prevent stretching on large screens
        grid.setAlignment(Qt.AlignmentFlag.AlignTop)

        content.setLayout(grid)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.setLayout(layout)


class NavBar(QFrame):
    """A centered navigation bar with evenly distributed icons."""
    
    home_clicked = pyqtSignal()
    store_clicked = pyqtSignal()
    location_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NavBar")
        self._setup_ui()
        theme_manager.theme_changed.connect(self._update_icons)
        self._update_icons()

    def _setup_ui(self):
        """Setup the navigation bar UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 8, 16, 8)
        
        # Add stretchable space to ensure even distribution
        layout.addStretch()
        
        self.home_btn = QPushButton()
        self.home_btn.setIconSize(QSize(32, 32))
        self.home_btn.setFixedSize(48, 48)
        self.home_btn.clicked.connect(self.home_clicked.emit)
        layout.addWidget(self.home_btn)

        layout.addStretch()

        self.location_btn = QPushButton()
        self.location_btn.setIconSize(QSize(32, 32))
        self.location_btn.setFixedSize(48, 48)
        self.location_btn.clicked.connect(self.location_clicked.emit)
        layout.addWidget(self.location_btn)

        layout.addStretch()

        self.settings_btn = QPushButton()
        self.settings_btn.setIconSize(QSize(32, 32))
        self.settings_btn.setFixedSize(48, 48)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(self.settings_btn)

        layout.addStretch()

        self.store_btn = QPushButton()
        self.store_btn.setIconSize(QSize(32, 32))
        self.store_btn.setFixedSize(48, 48)
        self.store_btn.clicked.connect(self.store_clicked.emit)
        layout.addWidget(self.store_btn)

        layout.addStretch()

        self.theme_btn = QPushButton()
        self.theme_btn.setIconSize(QSize(32, 32))
        self.theme_btn.setFixedSize(48, 48)
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)

        layout.addStretch()
        self.setLayout(layout)

    def toggle_theme(self):
        """Toggle the theme."""
        theme_manager.toggle_theme()

    def set_active_button(self, active_name: str):
        """Set the visual state of the active navigation button."""
        self.home_btn.setProperty("active", active_name == 'home')
        self.location_btn.setProperty("active", active_name == 'location')
        self.settings_btn.setProperty("active", active_name == 'settings')
        self.store_btn.setProperty("active", active_name == 'store')
        
        # To refresh the style, we can unpolish and polish the widget
        style = self.style()
        if style:
            for btn in [self.home_btn, self.location_btn, self.settings_btn, self.store_btn]:
                style.unpolish(btn)
                style.polish(btn)

    def _update_icons(self):
        """Update icons based on the current theme."""
        self.home_btn.setIcon(get_themed_icon('resources/icons/home.svg'))
        self.location_btn.setIcon(get_themed_icon('resources/icons/location.svg'))
        self.settings_btn.setIcon(get_themed_icon('resources/icons/settings.svg'))
        self.store_btn.setIcon(get_themed_icon('resources/icons/store.svg'))
        self.theme_btn.setIcon(
            get_themed_icon('resources/icons/night-mode.svg') if theme_manager.is_day_mode() 
            else get_themed_icon('resources/icons/sun.svg')
        )


class CarDisplay(QLabel):
    """Car image display with glow effect"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CarDisplay")
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the car display"""
        pixmap = QPixmap('resources/images/car_display.png')
        if pixmap.isNull():
            print("Warning: Car display image not found at 'resources/images/car_display.png'")
            # Optional: Create a placeholder pixmap
            pixmap = QPixmap(400, 400)
            pixmap.fill(Qt.GlobalColor.darkGray)

        scaled_pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled_pixmap)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class Dashboard(QWidget):
    """Main dashboard widget with clock and store access"""
    
    def __init__(self, features: list, installed_images: set):
        super().__init__()
        self.setObjectName("Dashboard")
        self.features = features
        self.installed_images = installed_images
        self._setup_ui()
        theme_manager.theme_changed.connect(self.update_styles)
        # Set initial state without triggering a transition
        self.stack.setCurrentIndex(0)
        self.navbar.set_active_button('home')
        self.update_styles()
    
    def update_styles(self):
        """Update the dashboard's style from the theme manager"""
        self.setStyleSheet(theme_manager.get_stylesheet())

    def _setup_ui(self):
        """Setup the dashboard UI"""
        self.setWindowTitle('ADAS Dashboard')
        self.resize(1280, 720)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        
        self.navbar = NavBar(self)
        # Connect navigation signals
        self.navbar.home_clicked.connect(self.show_dashboard)
        self.navbar.store_clicked.connect(self.show_store)
        self.navbar.location_clicked.connect(self.show_location)
        self.navbar.settings_clicked.connect(self.show_settings)
        
        self.stack = QStackedWidget()
        dashboard_view = QWidget()
        dashboard_layout = QHBoxLayout(dashboard_view)
        dashboard_layout.setContentsMargins(0, 0, 0, 0)
        dashboard_layout.setSpacing(0)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(40, 40, 40, 40)
        car_display = CarDisplay()
        left_layout.addWidget(car_display)
        dashboard_layout.addWidget(left_panel, 6) # Give more space to car
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 40, 40)
        
        clock = ClockWidget()
        right_layout.addWidget(clock, alignment=Qt.AlignmentFlag.AlignCenter)
        
        weather = WeatherWidget()
        right_layout.addWidget(weather, alignment=Qt.AlignmentFlag.AlignCenter)
        
        right_layout.addStretch()
        dashboard_layout.addWidget(right_panel, 4) # Less space to widgets
        
        self.stack.addWidget(dashboard_view)
        self.store_view = StoreView(self.features, self.installed_images, self)
        self.stack.addWidget(self.store_view)

        # Add stack first, then navbar to place it at the bottom
        main_layout.addWidget(self.stack)
        main_layout.addWidget(self.navbar)

    def show_info_view(self, feature: Feature):
        """Show the full-screen info view for a feature"""
        # Create info view if it doesn't exist or update with new feature
        if not hasattr(self, 'info_view'):
            self.info_view = FeatureInfoView(feature, self)
            self.stack.addWidget(self.info_view)
        else:
            # Update existing info view with new feature
            self.info_view.feature = feature
            self.info_view._setup_ui()
        
        self.stack.setCurrentWidget(self.info_view)
        self.navbar.set_active_button('store')  # Keep store as active since we're viewing a feature
        self.update_styles()

    def _slide_transition(self, next_index: int):
        current_index = self.stack.currentIndex()
        if current_index == next_index:
            return

        current_widget = self.stack.currentWidget()
        next_widget = self.stack.widget(next_index)

        if not current_widget or not next_widget:
            # Fallback for safety, though this shouldn't happen in normal operation
            self.stack.setCurrentIndex(next_index)
            return

        width = self.stack.width()
        height = self.stack.height()
        
        # Position the next widget to slide in from the correct direction
        if next_index > current_index:
            next_widget.setGeometry(width, 0, width, height)
        else:
            next_widget.setGeometry(-width, 0, width, height)

        self.stack.setCurrentIndex(next_index)

        # Animate current widget (now next_widget) into view
        anim = QPropertyAnimation(next_widget, b"geometry", self)
        anim.setDuration(300)
        anim.setStartValue(next_widget.geometry())
        anim.setEndValue(QRect(0, 0, width, height))
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def show_location(self):
        """Show location view (placeholder for now)"""
        self.show_dashboard()

    def show_settings(self):
        """Show settings view (placeholder for now)"""
        # For now, just show dashboard
        self.show_dashboard()

    def show_store(self):
        """Switch to store view with slide transition"""
        self._slide_transition(1)
        self.navbar.set_active_button('store')
        self.update_styles()

    def show_dashboard(self):
        """Switch to dashboard view with slide transition"""
        self._slide_transition(0)
        self.navbar.set_active_button('home')
        self.update_styles()


class FeatureInfoView(QWidget):
    """Modern full-screen feature information view"""
    
    def __init__(self, feature: Feature, parent=None):
        super().__init__(parent)
        self.feature = feature
        self._setup_ui()
        theme_manager.theme_changed.connect(self._update_icons)

    def _setup_ui(self):
        """Setup the full-screen info view UI"""
        self.setObjectName("FeatureInfoView")
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton("← Back")
        back_btn.setObjectName("BackButton")
        back_btn.clicked.connect(self.go_back)
        header_layout.addWidget(back_btn)
        
        header_layout.addStretch()
        
        # Title
        title = QLabel(self.feature.name)
        title.setObjectName("InfoTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Placeholder for symmetry
        placeholder = QWidget()
        placeholder.setFixedSize(back_btn.sizeHint())
        header_layout.addWidget(placeholder)
        
        layout.addLayout(header_layout)
        
        # Main content
        content_layout = QHBoxLayout()
        content_layout.setSpacing(40)
        
        # Left panel - Icon and basic info
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Large icon
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(200, 200)
        left_layout.addWidget(self.icon_label)
        
        # Download button
        self.download_btn = QPushButton("Download & Install")
        self.download_btn.setObjectName("InfoDownloadButton")
        self.download_btn.clicked.connect(self.download_feature)
        left_layout.addWidget(self.download_btn)
        
        left_layout.addStretch()
        left_panel.setLayout(left_layout)
        content_layout.addWidget(left_panel, 1)
        
        # Right panel - Detailed information
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Description
        desc_label = QLabel("Description")
        desc_label.setObjectName("InfoSectionTitle")
        right_layout.addWidget(desc_label)
        
        desc_text = QLabel(self.feature.long_desc)
        desc_text.setObjectName("InfoDescription")
        desc_text.setWordWrap(True)
        desc_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        right_layout.addWidget(desc_text)
        
        right_layout.addSpacing(20)
        
        # Technical details
        tech_label = QLabel("Technical Details")
        tech_label.setObjectName("InfoSectionTitle")
        right_layout.addWidget(tech_label)
        
        tech_text = QLabel(f"Image: {self.feature.image_name}\nLocation: {self.feature.location or 'Not specified'}")
        tech_text.setObjectName("InfoTechDetails")
        tech_text.setWordWrap(True)
        right_layout.addWidget(tech_text)
        
        right_layout.addStretch()
        right_panel.setLayout(right_layout)
        content_layout.addWidget(right_panel, 2)
        
        layout.addLayout(content_layout)
        self.setLayout(layout)
        self._update_icons()

    def _get_feature_icon(self) -> str:
        """Get the appropriate icon path for the feature"""
        feature_name = self.feature.name.lower()
        if 'lane' in feature_name:
            return 'resources/icons/lane.svg'
        elif 'cruise' in feature_name:
            return 'resources/icons/cruise.svg'
        elif 'hello' in feature_name:
            return 'resources/icons/hello.svg'
        else:
            return 'resources/icons/store.svg'

    def _update_icons(self):
        """Update the feature icon based on current theme"""
        icon_path = self._get_feature_icon()
        self.icon_label.setPixmap(get_themed_icon(icon_path).pixmap(200, 200))

    def go_back(self):
        """Return to the previous view"""
        main_window = self.window()
        if hasattr(main_window, 'show_store'):
            main_window.show_store()

    def download_feature(self):
        """Download and install the feature"""
        if not self.feature.location:
            return
            
        main_window = self.window()
        main_window.hide()
        
        dialog = DownloadInstallDialog(self.feature.image_name, main_window)
        
        def after_install(success: bool):
            if success:
                # Update installed state if needed
                pass
        
        dialog.start_worker(self.feature.location, main_window, after_install)
        dialog.exec() 