"""
Main entry point for the ADAS Dashboard
"""
import sys
from PyQt6.QtWidgets import QApplication
from utils.file_utils import load_features, load_installed_images
from ui.components import Dashboard
from services.alert_service import AlertService


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Load data
    features = load_features()
    installed_images = load_installed_images()
    
    # Create main window
    dashboard = Dashboard(features, installed_images)
    dashboard.show()
    
    # Initialize and start the alert service
    alert_service = AlertService('resources/results.json', dashboard)
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main() 