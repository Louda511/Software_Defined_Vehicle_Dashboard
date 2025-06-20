"""
Podman service for managing container operations
"""
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal
from utils.file_utils import extract_image_name


class PodmanWorker(QThread):
    """Worker thread for Podman operations"""
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, image_url: str, parent=None):
        super().__init__(parent)
        self.image_url = image_url
        self.image_name = extract_image_name(image_url)

    def run(self):
        """Execute Podman pull and run commands"""
        try:
            self.status_update.emit('Pulling image with Podman...')
            pull_cmd = ['podman', 'pull', self.image_name]
            subprocess.run(pull_cmd, check=True, capture_output=True)
            
            self.status_update.emit('Running container with Podman...')
            run_cmd = [
                'podman', 'run', '-d', '--rm', 
                '--name', self.image_name, 
                self.image_name, 'sleep', 'infinity'
            ]
            subprocess.run(run_cmd, check=True, capture_output=True)
            
            self.status_update.emit('Done!')
            self.finished.emit(True, 'Container ran successfully.')
        except subprocess.CalledProcessError as e:
            self.status_update.emit('Error occurred.')
            self.finished.emit(False, str(e)) 