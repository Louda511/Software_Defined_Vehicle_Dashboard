#!/usr/bin/env python3
"""
Test script to verify the alert screen appearance
"""
import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from ui.alert_screen import AlertScreen

def test_alert_screen():
    """Test the alert screen with different messages"""
    alert = AlertScreen(
        "Drowsiness Detected!", 
        "Please stay alert and take a break if needed."
    )
    alert.show()
    alert.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = QWidget()
    layout = QVBoxLayout(window)
    
    btn_test = QPushButton("Test Alert Screen")
    btn_test.clicked.connect(test_alert_screen)
    layout.addWidget(btn_test)
    
    window.setWindowTitle("Alert Screen Test")
    window.resize(300, 100)
    window.show()
    
    print("Click 'Test Alert Screen' to see the new yellow warning design")
    
    sys.exit(app.exec()) 