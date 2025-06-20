"""
A modern, top-aligned status bar for the dashboard.
"""
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt, QTimer, QTime
from .styles import theme_manager
from .icon_utils import get_themed_icon
from .widgets import NetworkStatusWidget

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
        current_time = QTime.currentTime()
        self.time_label.setText(current_time.toString("hh:mm"))

    def _update_styles(self):
        """Updates the icons and styles based on the current theme."""
        icon = get_themed_icon("resources/icons/partly-cloudy.svg")
        self.weather_icon.setPixmap(icon.pixmap(32, 32))
        self.network_widget.set_color(QColor(theme_manager.theme['text'])) 