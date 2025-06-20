"""
Alert dialog UI for displaying system warnings
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from ui.styles import theme_manager

class AlertScreen(QDialog):
    """A themed dialog for displaying alerts."""
    def __init__(self, main_message: str, advice_message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Warning!')
        self.setModal(True)
        self.setMinimumWidth(450)
        
        self.main_message = main_message
        self.advice_message = advice_message
        
        self._setup_ui()
        theme_manager.theme_changed.connect(self.update_styles)
        self.update_styles()

    def _setup_ui(self):
        """Setup the alert screen UI"""
        self.setObjectName("AlertScreen")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setObjectName("AlertHeader")
        header_layout = QHBoxLayout()
        
        icon_label = QLabel('⚠️')
        icon_label.setObjectName("AlertIcon")
        
        caution_label = QLabel('CAUTION')
        caution_label.setObjectName("AlertHeaderText")
        
        header_layout.addStretch()
        header_layout.addWidget(icon_label)
        header_layout.addWidget(caution_label)
        header_layout.addStretch()
        header.setLayout(header_layout)
        
        # Body
        body = QWidget()
        body.setObjectName("AlertBody")
        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(20, 20, 20, 20)
        
        self.main_label = QLabel(self.main_message)
        self.main_label.setObjectName("AlertMainText")
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_label.setWordWrap(True)
        
        self.advice_label = QLabel(self.advice_message)
        self.advice_label.setObjectName("AlertAdviceText")
        self.advice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.advice_label.setWordWrap(True)

        body_layout.addWidget(self.main_label)
        body_layout.addWidget(self.advice_label)
        body.setLayout(body_layout)
        
        main_layout.addWidget(header)
        main_layout.addWidget(body)
        self.setLayout(main_layout)

    def update_styles(self):
        """Apply styles from the theme manager."""
        theme = theme_manager.theme
        border_radius = theme.get('border_radius', '8px')
        self.setStyleSheet(f"""
            #AlertScreen {{
                background-color: {theme['background']};
                border: 2px solid {theme['alert_color']};
                border-radius: {border_radius};
            }}
            #AlertHeader {{
                background-color: {theme['alert_color']};
                color: {theme['alert_text_color']};
                padding: 10px;
                border-top-left-radius: {border_radius};
                border-top-right-radius: {border_radius};
            }}
            #AlertIcon {{
                font-size: 24px;
                background: transparent;
            }}
            #AlertHeaderText {{
                font-size: 18px;
                font-weight: bold;
                color: {theme['alert_text_color']};
                background: transparent;
            }}
            #AlertBody {{
                background-color: {theme['background']};
                border-bottom-left-radius: {border_radius};
                border-bottom-right-radius: {border_radius};
            }}
            #AlertMainText {{
                font-size: 16px;
                font-weight: bold;
                color: {theme['text']};
                padding-bottom: 10px;
            }}
            #AlertAdviceText {{
                font-size: 14px;
                color: {theme['text']};
            }}
        """)

    def set_message(self, main_message: str, advice_message: str):
        """Update the displayed messages."""
        self.main_label.setText(main_message)
        self.advice_label.setText(advice_message) 