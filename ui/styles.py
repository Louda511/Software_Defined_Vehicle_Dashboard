"""
Modern UI styles for the ADAS Dashboard
"""
from PyQt6.QtCore import QObject, pyqtSignal

# A softer, more comfortable dark theme inspired by popular code editors.
NIGHT_THEME = {
    'background': '#1A1B26',      # Soft, deep navy/charcoal
    'card_bg': '#292B3D',         # A slightly lighter, complementary color
    'accent': '#89B4FA',          # Soft, pastel-like blue for highlights
    'accent_hover': '#7AA3E8',    # Slightly darker blue for hover states
    'text': '#C0CAF5',            # Light, slightly blue-tinted gray (easy on the eyes)
    'text_secondary': '#A9B1D6',  # Mid-tone for secondary text
    'border': '#414868',          # A visible but not jarring border
    'success': '#198754',
    'alert_color': '#E06B74',      # A soft red for alerts
    'alert_text_color': '#1A1B26'  # Use the main background for high contrast
}

# A clean, low-contrast day theme for reduced glare.
DAY_THEME = {
    'background': '#F4F5F7',      # Soft, neutral light gray
    'card_bg': '#FFFFFF',         # Clean white for cards
    'accent': '#3D84E6',          # A professional, standard blue
    'accent_hover': '#2B6CB0',    # Darker blue for hover states
    'text': '#2D3748',            # Dark charcoal (softer than pure black)
    'text_secondary': '#718096',  # Medium gray for secondary info
    'border': '#E2E8F0',          # A very light, subtle border
    'success': '#28a745',
    'alert_color': '#E53935',      # A standard, clear red for alerts
    'alert_text_color': '#FFFFFF'  # White text for high contrast
}


class ThemeManager(QObject):
    """Manages color themes for the application"""
    theme_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._themes = {'night': NIGHT_THEME, 'day': DAY_THEME}
        self._current_theme_name = 'day'
        self.theme = DAY_THEME

    def set_theme(self, name: str):
        """Set the current theme by name ('day' or 'night')"""
        if name in self._themes and name != self._current_theme_name:
            self._current_theme_name = name
            self.theme = self._themes[name]
            self.theme_changed.emit()

    def toggle_theme(self):
        """Toggle between day and night themes"""
        if self._current_theme_name == 'day':
            self.theme = NIGHT_THEME
            self._current_theme_name = 'night'
        else:
            self.theme = DAY_THEME
            self._current_theme_name = 'day'
        self.theme_changed.emit()

    def is_day_mode(self) -> bool:
        """Returns True if the current theme is 'day'."""
        return self._current_theme_name == 'day'

    def get_stylesheet(self) -> str:
        """Get the full stylesheet for the application for the current theme."""
        return f"""
            /* Global Styles */
            QWidget {{
                font-family: 'Ubuntu', 'Cantarell', 'DejaVu Sans', 'Verdana', sans-serif;
                color: {self.theme['text']};
            }}
            
            /* Main Dashboard */
            QWidget#Dashboard, #StoreView, QScrollArea > QWidget > QWidget {{
                background-color: {self.theme['background']};
            }}

            /* Navigation Bar */
            QFrame#NavBar {{
                background-color: {self.theme['card_bg']};
                border-top: 1px solid {self.theme['border']};
                padding: 8px 16px;
            }}
            #NavBar QPushButton {{
                border-radius: 12px;
                background-color: transparent;
                border: none;
                padding: 8px;
            }}
            #NavBar QPushButton:hover {{
                background-color: {self.theme['accent']};
            }}
            #NavBar QPushButton[active="true"] {{
                background-color: {self.theme['accent']};
            }}

            /* Feature Cards */
            QFrame#FeatureCard {{
                border-radius: 12px;
                background-color: {self.theme['card_bg']};
                border: 1px solid {self.theme['border']};
                padding: 20px;
                margin: 8px;
            }}

            QFrame#FeatureCard:hover {{
                border-color: {self.theme['accent']};
            }}

            #FeatureCard #FeatureTitle {{
                font-size: 18px;
                font-weight: bold;
            }}

            #FeatureCard #FeatureDesc {{
                font-size: 14px;
                color: {self.theme['text_secondary']};
            }}

            #FeatureCard QPushButton {{
                padding: 6px 10px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
                min-width: 120px;
            }}
            
            #FeatureCard #InfoButton {{
                background-color: {self.theme['background']};
                color: {self.theme['text']};
                border: 1px solid {self.theme['border']};
            }}
            
            #FeatureCard #InfoButton:hover {{
                background-color: {self.theme['border']};
            }}

            #FeatureCard #DownloadButton {{
                background-color: {self.theme['accent']};
                color: white;
            }}
            
            #FeatureCard #DownloadButton:hover {{
                background-color: {self.theme['accent_hover']};
            }}

            #FeatureCard #InstalledButton {{
                background-color: {self.theme['success']};
                color: white;
            }}

            /* Clock Widget */
            QFrame#ClockWidget {{
                background-color: transparent;
                border: none;
                margin-bottom: 20px;
            }}
            #ClockWidget #TimeLabel {{
                font-size: 84px;
                font-weight: 300;
            }}
            #ClockWidget #DateLabel {{
                font-size: 24px;
                font-weight: 300;
                color: {self.theme['text_secondary']};
            }}
            
            /* Weather Widget */
            QFrame#WeatherWidget {{
                border-radius: 16px;
                background-color: {self.theme['card_bg']};
                border: 1px solid {self.theme['border']};
                padding: 24px;
                margin-top: 20px;
            }}
            #WeatherWidget #MainTempLabel {{
                font-size: 48px;
                font-weight: bold;
            }}
            #WeatherWidget #ConditionLabel {{
                font-size: 20px;
            }}
            #WeatherWidget #Separator {{
                background-color: {self.theme['border']};
                height: 1px;
            }}
            #WeatherWidget QLabel {{
                font-size: 16px;
                color: {self.theme['text_secondary']};
            }}

            /* Car Display */
            QLabel#CarDisplay {{
                background-color: transparent;
            }}

            /* Scroll Area */
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            /* Feature Info View */
            #FeatureInfoView {{
                background-color: {self.theme['background']};
            }}
            #FeatureInfoView #BackButton {{
                font-size: 16px;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 8px;
                border: 1px solid {self.theme['border']};
            }}
            #FeatureInfoView #BackButton:hover {{
                background-color: {self.theme['accent']};
                color: white;
            }}
            #FeatureInfoView #InfoTitle {{
                font-size: 24px;
                font-weight: bold;
            }}
            #FeatureInfoView #InfoDownloadButton {{
                font-size: 16px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 8px;
                background-color: {self.theme['accent']};
                color: white;
            }}
            #FeatureInfoView #InfoDownloadButton:hover {{
                background-color: {self.theme['accent_hover']};
            }}
            #FeatureInfoView #DescLabel {{
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 8px;
            }}
            #FeatureInfoView #LongDescLabel {{
                font-size: 16px;
            }}
        """

theme_manager = ThemeManager()

STORE_BUTTON_STYLE = f'''
QPushButton {{
    border-radius: 40px;
    background: {NIGHT_THEME['card_bg']};
    border: 2px solid {NIGHT_THEME['accent']};
    padding: 10px;
}}

QPushButton:hover {{
    background: {NIGHT_THEME['accent']};
}}
''' 