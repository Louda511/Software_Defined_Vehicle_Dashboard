"""
Custom widgets for the ADAS Dashboard
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QWidget, QGridLayout
from PyQt6.QtCore import QTimer, Qt, QSize
from PyQt6.QtGui import QPixmap, QFont
from datetime import datetime
from .styles import theme_manager
from .icon_utils import get_themed_pixmap, get_themed_icon
from services.podman_service import PodmanWorker


class CarDisplay(QLabel):
    """A widget to display the car image, scaled to fit."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CarDisplay")
        self._setup_ui()

    def _setup_ui(self):
        """Setup the car display UI"""
        pixmap = QPixmap('resources/images/car_display.png')
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        self.setMinimumSize(1, 1)

    def resizeEvent(self, event):
        """Handle resizing to keep aspect ratio."""
        pixmap = self.pixmap()
        if not pixmap:
            return
        
        scaled_pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled_pixmap)
        super().resizeEvent(event)


class ClockWidget(QFrame):
    """A modern digital clock widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ClockWidget")
        
        self.time_label = QLabel()
        self.time_label.setObjectName("TimeLabel")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.date_label = QLabel()
        self.date_label.setObjectName("DateLabel")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout = QVBoxLayout()
        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)
        self.setLayout(layout)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        self.update_time()

    def update_time(self):
        """Update the clock display"""
        current_time = datetime.now()
        self.time_label.setText(current_time.strftime("%H:%M"))
        self.date_label.setText(current_time.strftime("%A, %B %d"))


class WeatherWidget(QFrame):
    """A widget to display weather information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WeatherWidget")
        self._setup_ui()
        theme_manager.theme_changed.connect(self._update_icons)

    def _setup_ui(self):
        """Setup the weather widget UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Main weather display
        main_layout = QHBoxLayout()
        
        self.weather_icon = QLabel()
        self.weather_icon.setFixedSize(64, 64)
        main_layout.addWidget(self.weather_icon)
        
        temp_layout = QVBoxLayout()
        temp_layout.setSpacing(0)
        
        self.main_temp_label = QLabel("18°")
        self.main_temp_label.setObjectName("MainTempLabel")
        temp_layout.addWidget(self.main_temp_label)
        
        self.condition_label = QLabel("Partly Cloudy")
        self.condition_label.setObjectName("ConditionLabel")
        temp_layout.addWidget(self.condition_label)
        
        main_layout.addLayout(temp_layout)
        layout.addLayout(main_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("Separator")
        layout.addWidget(separator)

        # Additional details
        details_layout = QGridLayout()
        details_layout.setSpacing(15)
        
        # Feels Like
        self.feels_like_icon = QLabel()
        self.feels_like_label = QLabel("Feels like 16°")
        details_layout.addWidget(self.feels_like_icon, 0, 0)
        details_layout.addWidget(self.feels_like_label, 0, 1)

        # Wind
        self.wind_icon = QLabel()
        self.wind_label = QLabel("12 km/h")
        details_layout.addWidget(self.wind_icon, 0, 2)
        details_layout.addWidget(self.wind_label, 0, 3)
        
        # Humidity
        self.humidity_icon = QLabel()
        self.humidity_label = QLabel("82%")
        details_layout.addWidget(self.humidity_icon, 1, 0)
        details_layout.addWidget(self.humidity_label, 1, 1)
        
        layout.addLayout(details_layout)
        self.setLayout(layout)
        self._update_icons()

    def _update_icons(self):
        """Update icons based on theme."""
        self.weather_icon.setPixmap(get_themed_icon('resources/icons/weather-clear.svg').pixmap(64, 64))
        self.feels_like_icon.setPixmap(get_themed_icon('resources/icons/sun.svg').pixmap(24, 24))
        self.wind_icon.setPixmap(get_themed_icon('resources/icons/wind.svg').pixmap(24, 24))
        self.humidity_icon.setPixmap(get_themed_icon('resources/icons/rainy.svg').pixmap(24, 24))


class Dashboard(QWidget):
    """Main dashboard widget with clock and store access"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Dashboard")
        self._setup_ui()

    def _setup_ui(self):
        """Setup the dashboard UI"""
        layout = QVBoxLayout()
        
        # Clock widget
        self.clock_widget = ClockWidget()
        layout.addWidget(self.clock_widget)
        
        # Weather widget
        self.weather_widget = WeatherWidget()
        layout.addWidget(self.weather_widget)
        
        self.setLayout(layout) 