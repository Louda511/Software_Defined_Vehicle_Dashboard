"""
Podman service for managing container operations
"""
import os
import podman
from PyQt6.QtCore import QThread, pyqtSignal
from utils.file_utils import extract_image_name, load_installed_images, save_installed_images

def get_podman_socket_path():
    """
    Detect the Podman socket path for host and container environments.
    Priority:
    1. PODMAN_SOCKET_PATH env var (for containerized use)
    2. /run/user/{uid}/podman/podman.sock (host user session)
    3. Fallbacks: /run/podman/podman.sock, /var/run/podman/podman.sock
    """
    env_path = os.environ.get('PODMAN_SOCKET_PATH')
    if env_path and os.path.exists(env_path):
        return f'unix://{env_path}'
    user_sock = f'/run/user/{os.getuid()}/podman/podman.sock'
    if os.path.exists(user_sock):
        return f'unix://{user_sock}'
    for path in [
        '/run/podman/podman.sock',
        '/var/run/podman/podman.sock',
    ]:
        if os.path.exists(path):
            return f'unix://{path}'
    return None

class PodmanWorker(QThread):
    """Worker thread for Podman operations using Podman socket API"""
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, image_url: str, parent=None):
        super().__init__(parent)
        self.image_url = image_url
        self.image_name = extract_image_name(image_url)

    def run(self):
        """Pull image, run container, and save installed image using Podman socket API."""
        try:
            socket_path = get_podman_socket_path()
            if not socket_path:
                self.status_update.emit('No Podman socket found. Set PODMAN_SOCKET_PATH or ensure Podman is running.')
                self.finished.emit(False, 'Podman socket not available')
                return

            self.status_update.emit('Connecting to Podman...')
            client = podman.PodmanClient(base_url=socket_path)

            self.status_update.emit(f'Pulling image: {self.image_name}...')
            client.images.pull(self.image_name)

            self.status_update.emit(f'Running container from {self.image_name}...')
            try:
                existing_container = client.containers.get(self.image_name)
                if existing_container.status == 'running':
                    self.status_update.emit(f"Container '{self.image_name}' is already running.")
                else:
                    existing_container.start()
            except podman.errors.NotFound:
                client.containers.run(
                    self.image_name,
                    detach=True,
                    remove=True,
                    name=self.image_name,
                    command=['sleep', 'infinity']
                )

            # Save the installed image to the JSON file
            installed_images = load_installed_images()
            installed_images.add(self.image_name)
            save_installed_images(installed_images)

            self.status_update.emit('Done!')
            self.finished.emit(True, 'Container ran successfully.')

        except podman.errors.APIError as e:
            self.status_update.emit('Podman API Error occurred.')
            self.finished.emit(False, f"API Error: {e}")
        except Exception as e:
            self.status_update.emit('An unexpected error occurred.')
            self.finished.emit(False, str(e)) 