"""
Main entry point for the ADAS Dashboard
"""
import sys
from PyQt6.QtWidgets import QApplication
from utils.file_utils import load_features, load_installed_images
from ui.components import Dashboard
from warning_screen import WarningFileWatcher


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Load data
    features = load_features()
    installed_images = load_installed_images()
    
    # Create and show dashboard
    dashboard = Dashboard(features, installed_images)
    dashboard.show()
    
    # Integrate warning screen watcher
    watcher = WarningFileWatcher('resources/results.json', dashboard)
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main() 