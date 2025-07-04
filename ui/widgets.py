"""
Custom widgets for the ADAS Dashboard
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QWidget, QGridLayout
from PyQt6.QtCore import QTimer, Qt, QSize, QTime
from PyQt6.QtGui import QPixmap, QFont, QPainter, QColor
from datetime import datetime
from .styles import theme_manager
from .icon_utils import get_themed_pixmap, get_themed_icon
from services.podman_service import PodmanWorker
from utils.weather import fetch_current_weather
import requests
from io import BytesIO
import pytz


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
        cairo_tz = pytz.timezone("Africa/Cairo")
        now_cairo = datetime.now(cairo_tz)
        self.time_label.setText(now_cairo.strftime("%I:%M %p"))
        self.date_label.setText(now_cairo.strftime("%A, %B %d"))


class WeatherWidget(QFrame):
    """A widget to display weather information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WeatherWidget")
        self._setup_ui()
        theme_manager.theme_changed.connect(self._update_icons)
        self._update_weather()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_weather)
        self.timer.start(10 * 60 * 1000)  # Update every 10 minutes

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
        self._update_weather()

    def _update_weather(self):
        data = fetch_current_weather("Cairo")  # You can change location as needed
        if not data or "current" not in data:
            return
        current = data["current"]
        condition = current["condition"]["text"].lower()
        temp_c = current["temp_c"]
        feelslike_c = current["feelslike_c"]
        wind_kph = current["wind_kph"]
        humidity = current["humidity"]
        icon_url = current["condition"]["icon"]

        # Try to use the API icon
        try:
            if icon_url.startswith("//"):
                icon_url = "https:" + icon_url
            response = requests.get(icon_url, timeout=5)
            response.raise_for_status()
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.weather_icon.setPixmap(pixmap.scaled(64, 64))
        except Exception as e:
            print(f"Failed to load weather icon from API: {e}")
            # Fallback to local SVG based on condition
            if "snow" in condition:
                fallback_icon = 'resources/icons/snowy.svg'
            elif "fog" in condition or "mist" in condition:
                fallback_icon = 'resources/icons/foggy.svg'
            elif "cloud" in condition:
                fallback_icon = 'resources/icons/cloudy.svg'
            elif "rain" in condition:
                fallback_icon = 'resources/icons/rainy.svg'
            elif "clear" in condition or "sun" in condition:
                fallback_icon = 'resources/icons/weather-clear.svg'
            else:
                fallback_icon = 'resources/icons/weather-clear.svg'  # Default fallback
            self.weather_icon.setPixmap(get_themed_icon(fallback_icon).pixmap(64, 64))

        self.main_temp_label.setText(f"{int(round(temp_c))}°")
        self.condition_label.setText(current["condition"]["text"])
        self.feels_like_label.setText(f"Feels like {int(round(feelslike_c))}°")
        self.wind_label.setText(f"{wind_kph} km/h")
        self.humidity_label.setText(f"{humidity}%")


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


class SignalBarsWidget(QWidget):
    """A widget that draws mobile signal strength bars."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(32, 24)
        self._bar_color = QColor("#000000")

    def set_color(self, color: QColor):
        """Sets the color of the signal bars."""
        if self._bar_color != color:
            self._bar_color = color
            self.update()  # Trigger a repaint

    def paintEvent(self, event):
        """Paints the signal bars."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._bar_color)

        bar_width = 5
        max_height = self.height()
        spacing = 3

        # Bar heights as a percentage of max_height
        height_percentages = [0.4, 0.6, 0.8, 1.0]

        for i, percentage in enumerate(height_percentages):
            bar_height = int(max_height * percentage)
            x = i * (bar_width + spacing)
            y = max_height - bar_height
            painter.drawRect(x, y, bar_width, bar_height)

    def sizeHint(self):
        return QSize(32, 24)


class NetworkStatusWidget(QWidget):
    """A widget that displays network status including signal bars and type."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.signal_bars = SignalBarsWidget()
        self.network_type_label = QLabel("5G")
        self.network_type_label.setObjectName("NetworkTypeLabel")

        layout.addWidget(self.signal_bars)
        layout.addWidget(self.network_type_label)

    def set_color(self, color: QColor):
        """Sets the color for all elements in the widget."""
        self.signal_bars.set_color(color)
        self.network_type_label.setStyleSheet(f"color: {color.name()};") 