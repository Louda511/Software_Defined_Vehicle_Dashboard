"""
Alert dialog UI for displaying system warnings
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from ui.styles import theme_manager

class AlertScreen(QDialog):
    """A themed dialog for displaying alerts."""
    def __init__(self, main_message: str, advice_message: str, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.main_message = main_message
        self.advice_message = advice_message
        
        self._setup_ui()
        theme_manager.theme_changed.connect(self.update_styles)
        self.update_styles()

    def _setup_ui(self):
        """Setup the alert screen UI"""
        self.setObjectName("AlertScreen")
        container = QWidget()
        container.setObjectName("Container")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setObjectName("AlertHeader")
        header_layout = QHBoxLayout(header)
        caution_label = QLabel('CAUTION')
        caution_label.setObjectName("AlertHeaderText")
        caution_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(caution_label)
        
        # Body
        body = QWidget()
        body.setObjectName("AlertBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(30, 25, 30, 25)
        
        self.main_label = QLabel(self.main_message)
        self.main_label.setObjectName("AlertMainText")
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_label.setWordWrap(True)
        
        self.advice_label = QLabel(self.advice_message)
        self.advice_label.setObjectName("AlertAdviceText")
        self.advice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.advice_label.setWordWrap(True)

        # Button
        self.ok_button = QPushButton("OK")
        self.ok_button.setObjectName("OkButton")
        self.ok_button.clicked.connect(self.accept)
        
        body_layout.addWidget(self.main_label)
        body_layout.addWidget(self.advice_label)
        body_layout.addSpacing(20)
        body_layout.addWidget(self.ok_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(header)
        layout.addWidget(body)

    def update_styles(self):
        """Apply styles from the theme manager."""
        theme = theme_manager.theme
        border_radius = "12px"
        self.setStyleSheet(f"""
            #Container {{
                background-color: {theme['card_bg']};
                border: 2px solid {theme['alert_color']};
                border-radius: {border_radius};
            }}
            #AlertHeader {{
                background-color: {theme['alert_color']};
                border-top-left-radius: {border_radius};
                border-top-right-radius: {border_radius};
                min-height: 40px;
            }}
            #AlertHeaderText {{
                font-size: 16px;
                font-weight: bold;
                color: {theme['alert_text_color']};
                background-color: transparent;
            }}
            #AlertBody {{
                background-color: transparent;
            }}
            #AlertMainText {{
                font-size: 22px;
                font-weight: bold;
                color: {theme['text']};
                padding-bottom: 15px;
            }}
            #AlertAdviceText {{
                font-size: 16px;
                color: {theme['text_secondary']};
            }}
            #OkButton {{
                background-color: {theme['alert_btn_bg']};
                color: {theme['alert_btn_text']};
                border: 1px solid {theme['alert_btn_border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }}
            #OkButton:hover {{
                background-color: {theme['alert_btn_bg_hover']};
            }}
        """)

    def set_message(self, main_message: str, advice_message: str):
        """Update the displayed messages."""
        self.main_label.setText(main_message)
        self.advice_label.setText(advice_message) 