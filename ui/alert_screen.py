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
        self.setMinimumWidth(650)
        self.setMaximumWidth(800)
        
        self.main_message = main_message
        self.advice_message = advice_message
        
        self._setup_ui()
        theme_manager.theme_changed.connect(self.update_styles)
        self.update_styles()
        
        # Adjust size based on content
        self.adjustSize()

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
        header_layout.setContentsMargins(15, 12, 15, 12)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        caution_label = QLabel('CAUTION ⚠️')
        caution_label.setObjectName("AlertHeaderText")
        caution_label.setWordWrap(False)
        
        header_layout.addWidget(caution_label)
        
        # Body
        body = QWidget()
        body.setObjectName("AlertBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(30, 25, 30, 25)
        body_layout.setSpacing(15)
        
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
        
        layout.addWidget(header)
        layout.addWidget(body)

    def update_styles(self):
        """Apply styles from the theme manager."""
        theme = theme_manager.theme
        border_radius = "16px"
        self.setStyleSheet(f"""
            #Container {{
                background-color: {theme['card_bg']};
                border: 2px solid {theme['alert_color']};
                border-radius: {border_radius};
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            }}
            #AlertHeader {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme['alert_color']}, stop:1 {theme['alert_color']}dd);
                border-top-left-radius: {border_radius};
                border-top-right-radius: {border_radius};
                min-height: 50px;
                padding: 8px;
            }}
            #AlertHeaderText {{
                font-size: 22px;
                font-weight: bold;
                color: {theme['alert_text_color']};
                background-color: transparent;
                letter-spacing: 1px;
            }}
            #AlertBody {{
                background-color: transparent;
                padding: 8px;
            }}
            #AlertMainText {{
                font-size: 36px;
                font-weight: bold;
                color: {theme['text']};
                padding: 20px 0 15px 0;
                line-height: 1.4;
                word-wrap: break-word;
            }}
            #AlertAdviceText {{
                font-size: 20px;
                color: {theme['text_secondary']};
                line-height: 1.5;
                padding: 0 10px 20px 10px;
                word-wrap: break-word;
            }}
        """)

    def set_message(self, main_message: str, advice_message: str):
        """Update the displayed messages."""
        self.main_label.setText(main_message)
        self.advice_label.setText(advice_message) 