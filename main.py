import sys
import webbrowser
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QDialog, QDialogButtonBox, QScrollArea, QHBoxLayout, QFrame
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Dummy data for ADAS features
dummy_features = [
    {
        'name': 'Lane Keep Assist',
        'icon': 'resources/icons/lane.png',
        'short_desc': 'Keeps your car in lane.',
        'long_desc': 'Lane Keep Assist uses cameras to detect lane markings and gently steers the car to keep it centered in the lane.',
        'location': 'https://hub.docker.com/r/example/lane-keep-assist'
    },
    {
        'name': 'Adaptive Cruise Control',
        'icon': 'resources/icons/cruise.png',
        'short_desc': 'Automatic speed & distance.',
        'long_desc': 'Adaptive Cruise Control automatically adjusts your speed to maintain a safe distance from vehicles ahead.',
        'location': 'https://hub.docker.com/r/example/adaptive-cruise-control'
    },
    {
        'name': 'Automatic Emergency Braking',
        'icon': 'resources/icons/brake.png',
        'short_desc': 'Brakes in emergencies.',
        'long_desc': 'Automatic Emergency Braking detects imminent collisions and applies the brakes to prevent or reduce impact.',
        'location': 'https://hub.docker.com/r/example/automatic-emergency-braking'
    },
    {
        'name': 'Hello World',
        'icon': 'resources/icons/hello.png',
        'short_desc': 'The simplest Docker container.',
        'long_desc': 'This is the official Docker hello-world image. It is used to verify that Docker is installed and working correctly.',
        'location': 'https://hub.docker.com/_/alpine'
    },
]

class FeatureDialog(QDialog):
    def __init__(self, feature, parent=None):
        super().__init__(parent)
        self.setWindowTitle(feature['name'])
        self.setMinimumWidth(350)
        layout = QVBoxLayout()
        icon = QLabel()
        pixmap = QPixmap(feature['icon'])
        icon.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)
        desc = QLabel(feature['long_desc'])
        desc.setWordWrap(True)
        desc.setFont(QFont('Segoe UI', 11))
        layout.addWidget(desc)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        self.setLayout(layout)

class DownloadInstallDialog(QDialog):
    def __init__(self, image_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Downloading and Installing')
        self.setModal(True)
        self.setMinimumWidth(350)
        layout = QVBoxLayout()
        self.spinner = QLabel()
        self.spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner.setText('⏳')
        layout.addWidget(self.spinner)
        self.status_label = QLabel('Starting...')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        self.setLayout(layout)
        self.image_name = image_name
        self.worker = None  # Persistent reference to PodmanWorker

    def set_status(self, text):
        self.status_label.setText(text)

    def start_worker(self, url, main_window):
        self.worker = PodmanWorker(url)
        self.worker.status_update.connect(self.set_status)
        def on_finish(success, msg):
            self.set_status(msg)
            self.accept()
            main_window.show()
        self.worker.finished.connect(on_finish)
        self.worker.start()

class PodmanWorker(QThread):
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, image_url, parent=None):
        super().__init__(parent)
        self.image_url = image_url
        self.image_name = self.extract_image_name(image_url)

    def extract_image_name(self, url):
        # For Docker Hub, extract the image name from the URL
        # e.g., https://hub.docker.com/_/hello-world -> hello-world
        if '/_/' in url:
            return url.split('/_/')[-1]
        elif '/r/' in url:
            return url.split('/r/')[-1]
        return url.split('/')[-1]

    def run(self):
        import subprocess
        try:
            self.status_update.emit('Pulling image with Podman...')
            pull_cmd = ['podman', 'pull', self.image_name]
            subprocess.run(pull_cmd, check=True, capture_output=True)
            self.status_update.emit('Running container with Podman...')
            run_cmd = ['podman', 'run', '-d', '--rm', self.image_name, 'sleep', 'infinity']
            subprocess.run(run_cmd, check=True, capture_output=True)
            self.status_update.emit('Done!')
            self.finished.emit(True, 'Container ran successfully.')
        except subprocess.CalledProcessError as e:
            self.status_update.emit('Error occurred.')
            self.finished.emit(False, str(e))

class FeatureCard(QFrame):
    def __init__(self, feature, parent=None):
        super().__init__(parent)
        self.feature = feature
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet('''
            QFrame {
                border-radius: 12px;
                background: #23272e;
                border: 1px solid #444;
                padding: 12px;
            }
            QPushButton {
                border-radius: 8px;
                background: #3a3f4b;
                color: #fff;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background: #0078d7;
            }
            QLabel {
                color: #fff;
            }
        ''')
        layout = QVBoxLayout()
        icon = QLabel()
        pixmap = QPixmap(feature['icon'])
        icon.setPixmap(pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)
        name = QLabel(feature['name'])
        name.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name)
        short_desc = QLabel(feature['short_desc'])
        short_desc.setFont(QFont('Segoe UI', 10))
        short_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(short_desc)
        btn_layout = QHBoxLayout()
        info_btn = QPushButton('More Info')
        info_btn.clicked.connect(self.show_info)
        btn_layout.addWidget(info_btn)
        download_btn = QPushButton('Download')
        download_btn.clicked.connect(self.download_feature)
        btn_layout.addWidget(download_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    def show_info(self):
        dlg = FeatureDialog(self.feature, self)
        dlg.exec()
    def download_feature(self):
        url = self.feature.get('location')
        if url:
            main_window = self.window()
            main_window.hide()
            dlg = DownloadInstallDialog(url, main_window)
            dlg.start_worker(url, main_window)
            dlg.exec()

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ADAS App Store')
        self.setMinimumSize(800, 600)
        self.setStyleSheet('background: #181a20;')
        main_layout = QVBoxLayout()
        title = QLabel('ADAS App Store')
        title.setFont(QFont('Segoe UI', 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet('color: #fff; margin: 24px 0;')
        main_layout.addWidget(title)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        grid = QGridLayout()
        grid.setSpacing(24)
        for i, feature in enumerate(dummy_features):
            card = FeatureCard(feature)
            grid.addWidget(card, i // 3, i % 3)
        content.setLayout(grid)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

def main():
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 