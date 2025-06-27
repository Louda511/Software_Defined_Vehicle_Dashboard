"""
A modern, top-aligned status bar for the dashboard.
"""
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt, QTimer, QTime
from .styles import theme_manager
from .icon_utils import get_themed_icon
from .widgets import NetworkStatusWidget
from utils.weather import fetch_current_weather
import requests
import pytz
from datetime import datetime

class TopBar(QFrame):
    """
    A top-aligned status bar containing a clock and weather information.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TopBar")
        self._setup_ui()

        # Timer to update the clock every second
        timer = QTimer(self)
        timer.timeout.connect(self._update_time)
        timer.start(1000)
        
        self._update_time()

        # Timer to update weather every 10 minutes
        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self._update_weather)
        self.weather_timer.start(10 * 60 * 1000)
        self._update_weather()

        theme_manager.theme_changed.connect(self._update_styles)
        self._update_styles()

    def _setup_ui(self):
        """Setup the top bar UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Clock on the left
        self.time_label = QLabel("00:00")
        self.time_label.setObjectName("TopBarTimeLabel")
        
        # Weather on the right
        weather_widget = QWidget()
        weather_layout = QHBoxLayout(weather_widget)
        weather_layout.setContentsMargins(0, 0, 0, 0)
        weather_layout.setSpacing(10)
        
        self.weather_icon = QLabel()
        self.weather_icon.setObjectName("TopBarWeatherIcon")
        
        self.temp_label = QLabel("21°")
        self.temp_label.setObjectName("TopBarTempLabel")
        
        weather_layout.addWidget(self.weather_icon)
        weather_layout.addWidget(self.temp_label)
        
        # Network status
        self.network_widget = NetworkStatusWidget()
        
        # Main layout
        layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        layout.addWidget(self.network_widget)
        layout.addWidget(weather_widget, alignment=Qt.AlignmentFlag.AlignRight)
        
    def _update_time(self):
        """Updates the time label."""
        cairo_tz = pytz.timezone("Africa/Cairo")
        now_cairo = datetime.now(cairo_tz)
        self.time_label.setText(now_cairo.strftime("%I:%M %p"))

    def _update_weather(self):
        data = fetch_current_weather("Cairo")  # Change location as needed
        if not data or "current" not in data:
            self._set_yellow_sun_icon()
            return
        current = data["current"]
        temp_c = current["temp_c"]
        condition = current["condition"]["text"].lower()
        icon_url = current["condition"]["icon"]
        self.temp_label.setText(f"{int(round(temp_c))}°")
        # Try to use the API icon
        try:
            if icon_url.startswith("//"):
                icon_url = "https:" + icon_url
            response = requests.get(icon_url, timeout=5)
            response.raise_for_status()
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.weather_icon.setPixmap(pixmap.scaled(32, 32))
        except Exception as e:
            print(f"Failed to load top bar weather icon from API: {e}")
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
            self.weather_icon.setPixmap(get_themed_icon(fallback_icon).pixmap(32, 32))

    def _set_yellow_sun_icon(self):
        self.weather_icon.setPixmap(get_themed_icon("resources/icons/weather-clear.svg").pixmap(32, 32))

    def _update_styles(self):
        """Updates the icons and styles based on the current theme."""
        self._update_weather()
        self.network_widget.set_color(QColor(theme_manager.theme['text'])) 