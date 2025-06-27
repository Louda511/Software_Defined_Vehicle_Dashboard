"""
Main entry point for the ADAS Dashboard
"""
import sys
from PyQt6.QtWidgets import QApplication
from utils.file_utils import load_features, load_installed_images, save_features
from ui.components import Dashboard
from services.alert_service import AlertService
from services.api_service import fetch_features_from_api


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Try to fetch latest data from local server
    try:
        features_data = fetch_features_from_api("http://localhost:8000/")
        save_features(features_data)
    except Exception as e:
        # Silently fall back to cached data if server is unavailable
        pass
    
    # Load data (will use cached data if server fetch failed)
    features = load_features()
    installed_images = load_installed_images()
    
    # Create main window
    dashboard = Dashboard(features, installed_images)
    dashboard.show()
    
    # Initialize and start the alert service
    alert_service = AlertService('resources/results.json', dashboard)
    
    # Use app.exec() directly instead of sys.exit() for proper terminal return
    return app.exec()


if __name__ == '__main__':
    sys.exit(main()) 