"""
Podman service for managing container operations
"""
import os
from podman import PodmanClient
from PyQt6.QtCore import QThread, pyqtSignal
from utils.file_utils import extract_image_name, load_installed_images, save_installed_images

def get_podman_socket_path():
    """
    Detect the Podman socket path for host and container environments.
    Priority:
    1. PODMAN_SOCKET_PATH env var (for containerized use) - don't check existence
    2. /run/user/{uid}/podman/podman.sock (host user session)
    3. Fallbacks: /run/podman/podman.sock, /var/run/podman/podman.sock
    """
    # Use environment variable if provided (for containerized use)
    env_path = os.environ.get('PODMAN_SOCKET_PATH')
    if env_path:
        return f'unix://{env_path}'
    
    # Get current user ID for dynamic socket path detection
    current_uid = os.getuid()
    
    # Check user-specific socket first (most common for rootless Podman)
    user_sock = f'/run/user/{current_uid}/podman/podman.sock'
    if os.path.exists(user_sock):
        return f'unix://{user_sock}'
    
    # System-wide fallbacks
    for path in [
        '/run/podman/podman.sock',
        '/var/run/podman/podman.sock',
    ]:
        if os.path.exists(path):
            return f'unix://{path}'
    
    # If no socket found, return None and let the caller handle the error
    return None

class PodmanWorker(QThread):
    """Worker thread for Podman operations using Podman socket API"""
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, image_url: str, parent=None):
        super().__init__(parent)
        self.image_url = image_url
        self.image_name = extract_image_name(image_url)
        # For pulling: add docker.io/ prefix to ensure user images can be downloaded
        self.pull_image_name = f"docker.io/{self.image_name}" if not self.image_name.startswith('docker.io/') else self.image_name
        # Use a more robust container naming strategy
        self.container_name = f"adas-{self.image_name.replace('/', '-').replace(':', '-')}"

    def run(self):
        """Pull image, run container, and save installed image using Podman socket API."""
        try:
            socket_path = get_podman_socket_path()
            if not socket_path:
                current_uid = os.getuid()
                error_msg = f"""No Podman socket found for user {current_uid}.

Available solutions:
1. For user-level Podman: systemctl --user start podman.socket
2. For system-wide Podman: sudo systemctl start podman.socket  
3. Run setup script: ./setup_podman.sh
4. Set PODMAN_SOCKET_PATH environment variable

Expected socket locations:
- /run/user/{current_uid}/podman/podman.sock (user socket)
- /run/podman/podman.sock (system socket)
- /var/run/podman/podman.sock (alternative system socket)"""
                
                self.status_update.emit(error_msg)
                self.finished.emit(False, 'Podman socket not available')
                return

            self.status_update.emit('Connecting to Podman...')
            try:
                client = PodmanClient(base_url=socket_path)
                # Test connection
                client.ping()
            except Exception as e:
                self.status_update.emit(f'Failed to connect to Podman: {e}')
                self.finished.emit(False, f'Connection failed: {e}')
                return

            # Check if image is already pulled to avoid redundant pulls
            self.status_update.emit(f'Checking if image {self.image_name} is already available...')
            try:
                client.images.get(self.image_name)
                self.status_update.emit(f'Image {self.image_name} is already available.')
            except Exception:
                # Image not found, pull it with docker.io/ prefix
                self.status_update.emit(f'Pulling image: {self.pull_image_name}...')
                try:
                    client.images.pull(self.pull_image_name)
                    self.status_update.emit(f'Successfully pulled image: {self.pull_image_name}')
                except Exception as e:
                    self.status_update.emit(f'Failed to pull image: {e}')
                    self.finished.emit(False, f'Image pull failed: {e}')
                    return

            self.status_update.emit(f'Running container from {self.image_name}...')
            try:
                # Check if container already exists
                existing_container = client.containers.get(self.container_name)
                if existing_container.status == 'running':
                    self.status_update.emit(f"Container '{self.container_name}' is already running.")
                else:
                    existing_container.start()
                    self.status_update.emit(f"Started existing container '{self.container_name}'.")
            except Exception as e:
                # Container doesn't exist, create and run it using original image name
                try:
                    client.containers.run(
                        self.image_name,
                        detach=True,
                        remove=False,  # Don't auto-remove so we can manage it
                        name=self.container_name,
                        command=['sleep', 'infinity']
                    )
                    self.status_update.emit(f"Created and started container '{self.container_name}'.")
                except Exception as e:
                    self.status_update.emit(f'Failed to create container: {e}')
                    self.finished.emit(False, f'Container creation failed: {e}')
                    return

            # Save the installed image to the JSON file
            try:
                installed_images = load_installed_images()
                # Handle both set and list types for backward compatibility
                if hasattr(installed_images, 'add'):
                    installed_images.add(self.image_name)
                elif isinstance(installed_images, list):
                    if self.image_name not in installed_images:
                        installed_images.append(self.image_name)
                save_installed_images(installed_images)
                self.status_update.emit(f'Saved {self.image_name} to installed images.')
            except Exception as e:
                self.status_update.emit(f'Warning: Failed to save installed image info: {e}')
                # Don't fail the whole operation for this

            self.status_update.emit('Done!')
            self.finished.emit(True, 'Container ran successfully.')

        except Exception as e:
            self.status_update.emit('An unexpected error occurred.')
            self.finished.emit(False, str(e)) 