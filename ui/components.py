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
from ui.dialogs import InfoDialog, DownloadInstallDialog
from utils.file_utils import extract_image_name, save_installed_images
from .widgets import ClockWidget, WeatherWidget
from .styles import theme_manager
from .icon_utils import get_themed_icon
from .top_bar import TopBar
from PyQt6.QtCore import pyqtSignal
from services.podman_service import PodmanWorker
import os


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
        self.setFixedSize(600, 200)
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        layout.addStretch()
        
        # Icon section
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(64, 64)
        layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(20) # Increase space between icon and title
        
        # Title
        title = QLabel(self.feature.name)
        title.setObjectName("FeatureTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        layout.addWidget(title)
        
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
        # First, try to use the icon field from the feature
        if self.feature.icon:
            # Check if it's a local file path
            if self.feature.icon.startswith('resources/icons/') or self.feature.icon.startswith('./'):
                # Remove ./ if present for consistency
                icon_path = self.feature.icon.replace('./', '')
                if os.path.exists(icon_path):
                    print(f"[DEBUG] Using local icon for {self.feature.name}: {icon_path}")
                    return icon_path
            # Check if it's a valid URL or external path
            elif self.feature.icon.startswith('http') or self.feature.icon.startswith('https'):
                print(f"[DEBUG] Using remote URL icon for {self.feature.name}: {self.feature.icon}")
                return self.feature.icon
            # Check if it's a base64 data URL
            elif self.feature.icon.startswith('data:image/'):
                print(f"[DEBUG] Using base64 icon for {self.feature.name}")
                return self.feature.icon
            # Check if it's a relative path that exists
            elif os.path.exists(self.feature.icon):
                print(f"[DEBUG] Using relative path icon for {self.feature.name}: {self.feature.icon}")
                return self.feature.icon
        
        # Fallback to keyword matching based on feature name
        feature_name = self.feature.name.lower()
        if 'adaptive cruise control' in feature_name:
            print(f"[DEBUG] Fallback to adaptive-cruise.svg for {self.feature.name}")
            return 'resources/icons/adaptive-cruise.svg'
        if 'lane' in feature_name:
            print(f"[DEBUG] Fallback to lane.svg for {self.feature.name}")
            return 'resources/icons/lane.svg'
        elif 'cruise' in feature_name:
            print(f"[DEBUG] Fallback to cruise.svg for {self.feature.name}")
            return 'resources/icons/cruise.svg'
        elif 'brake' in feature_name:
            print(f"[DEBUG] Fallback to brake.svg for {self.feature.name}")
            return 'resources/icons/brake.svg'
        elif 'hello' in feature_name:
            print(f"[DEBUG] Fallback to hello.svg for {self.feature.name}")
            return 'resources/icons/hello.svg'
        elif 'weather' in feature_name:
            print(f"[DEBUG] Fallback to weather.svg for {self.feature.name}")
            return 'resources/icons/weather.svg'
        else:
            print(f"[DEBUG] Fallback to store.svg for {self.feature.name}")
            return 'resources/icons/store.svg'

    def _update_icons(self):
        """Update the feature icon based on current theme"""
        icon_path = self._get_feature_icon()
        icon = get_themed_icon(icon_path)
        pixmap = icon.pixmap(64, 64)
        print(f"[DEBUG] Setting icon for {self.feature.name}: {icon_path}, pixmap isNull={pixmap.isNull()}")
        self.icon_label.setPixmap(pixmap)

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
        """Show detailed information about the feature in a dialog."""
        dialog = InfoDialog(self.feature, self)
        dialog.exec()

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
                save_installed_images(self.installed_images)
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
        self.settings_btn.setIcon(get_themed_icon('resources/icons/phone.svg'))
        self.store_btn.setIcon(get_themed_icon('resources/icons/apps.svg'))
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
        self.main_stack.setCurrentIndex(0)
        self.nav_bar.set_active_button('home')
        self.update_styles()
    
    def update_styles(self):
        """Update the dashboard's style from the theme manager"""
        self.setStyleSheet(theme_manager.get_stylesheet())

    def _setup_ui(self):
        """Setup the dashboard UI"""
        self.setWindowTitle('ADAS Dashboard')
        self.resize(1280, 720)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top Bar
        self.top_bar = TopBar()
        
        # Main content area
        self.main_stack = QStackedWidget()
        self.dashboard_view = QWidget()
        self.dashboard_layout = QHBoxLayout(self.dashboard_view)
        self.dashboard_layout.setContentsMargins(0, 0, 0, 0)
        self.dashboard_layout.setSpacing(0)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(40, 40, 40, 40)
        self.car_display = CarDisplay()
        left_layout.addWidget(self.car_display)
        self.dashboard_layout.addWidget(left_panel, 6) # Give more space to car
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 40, 40)
        
        self.clock = ClockWidget()
        right_layout.addWidget(self.clock, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.weather = WeatherWidget()
        right_layout.addWidget(self.weather, alignment=Qt.AlignmentFlag.AlignCenter)
        
        right_layout.addStretch()
        self.dashboard_layout.addWidget(right_panel, 4) # Less space to widgets
        
        self.main_stack.addWidget(self.dashboard_view)
        self.store_view = StoreView(self.features, self.installed_images, self)
        self.main_stack.addWidget(self.store_view)

        layout.addWidget(self.top_bar)
        layout.addWidget(self.main_stack, 1) # Add stretch factor
        self.nav_bar = NavBar(self)
        self.nav_bar.home_clicked.connect(self.show_dashboard)
        self.nav_bar.store_clicked.connect(self.show_store)
        
        # Assemble layout
        layout.addWidget(self.nav_bar)
        
        self.setLayout(layout)
        self.update_styles()

    def _slide_transition(self, next_index: int):
        current_widget = self.main_stack.currentWidget()
        next_widget = self.main_stack.widget(next_index)

        width = self.frameGeometry().width()
        
        self.main_stack.setCurrentIndex(next_index)
        
        # Slide from right
        next_widget.setGeometry(width, 0, width, self.height())
        anim = QPropertyAnimation(next_widget, b"geometry")
        anim.setDuration(300)
        anim.setStartValue(QRect(width, 0, width, self.height()))
        anim.setEndValue(QRect(0, 0, width, self.height()))
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.start()

    def show_location(self):
        print("Location button clicked")

    def show_settings(self):
        print("Settings button clicked")

    def show_store(self):
        """Show the app store view."""
        self.nav_bar.set_active_button('store')
        self.main_stack.setCurrentIndex(1)

    def show_dashboard(self):
        """Show the main dashboard view."""
        self.nav_bar.set_active_button('home')
        self.main_stack.setCurrentIndex(0)
    
    def closeEvent(self, event):
        """Handle application close event to clean up resources."""
        # Stop any running timers
        if hasattr(self.clock, 'timer'):
            self.clock.timer.stop()
        if hasattr(self.weather, 'timer'):
            self.weather.timer.stop()
        
        # Stop TopBar timers
        if hasattr(self.top_bar, 'weather_timer'):
            self.top_bar.weather_timer.stop()
        # Stop the unnamed timer in TopBar
        for child in self.top_bar.children():
            if hasattr(child, 'timeout') and hasattr(child, 'stop'):
                child.stop()
        
        # Accept the close event
        event.accept()