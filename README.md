# ADAS App Store - Modular Structure

This project has been refactored into a modular structure for better maintainability and organization.

## Multi-User Support and Dynamic User ID Detection

The application now supports multiple users with automatic user ID detection and dynamic Podman socket path resolution. This eliminates the need for hardcoded user IDs and makes the application work seamlessly across different user accounts.

### Key Improvements

1. **Dynamic User ID Detection**: The application automatically detects the current user's ID using `os.getuid()`
2. **Automatic Socket Path Detection**: Podman socket paths are automatically detected based on the user's environment
3. **Multi-User Container Support**: Docker Compose and container scripts now work for any user ID
4. **Improved Error Handling**: Better error messages with specific solutions for different scenarios

### Socket Detection Priority

The application detects Podman sockets in the following order:
1. `PODMAN_SOCKET_PATH` environment variable (for containerized use)
2. `/run/user/{uid}/podman/podman.sock` (user-specific socket)
3. `/run/podman/podman.sock` (system-wide socket)
4. `/var/run/podman/podman.sock` (alternative system socket)

### Testing User Detection

Run the test script to verify your setup:

```bash
python test_user_detection.py
```

This will show:
- Your current user ID
- Available Podman sockets
- Socket detection status

### Troubleshooting

If you encounter issues with Podman socket detection:

1. **For user-level Podman**:
   ```bash
   systemctl --user start podman.socket
   systemctl --user start podman
   ```

2. **For system-wide Podman**:
   ```bash
   sudo systemctl start podman.socket
   sudo systemctl start podman
   ```

3. **Run the setup script**:
   ```bash
   ./setup_podman.sh
   ```

4. **Check socket status**:
   ```bash
   ls -la /run/user/$(id -u)/podman/podman.sock
   ```

## Project Structure

```
Software_Defined_Vehicle_Dashboard/
├── models/                 # Data models
│   ├── __init__.py
│   └── feature.py         # Feature data model
├── ui/                    # User interface components
│   ├── __init__.py
│   ├── components.py      # Main UI components (Dashboard, FeatureCard)
│   └── dialogs.py         # Dialog components
├── services/              # Business logic services
│   ├── __init__.py
│   └── podman_service.py  # Podman container operations
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── file_utils.py      # File operations and data loading
├── main.py               # Original monolithic file (kept for reference)
├── main_new.py           # New modular main entry point
├── warning_screen.py     # Warning screen functionality
├── resources/              # Project resources (icons, data)
│   ├── dummy_features.json   # Feature data
│   └── installed_images.json # Installed images tracking
└── requirements.txt      # Python dependencies
```

## Module Descriptions

### Models (`models/`)
- **`feature.py`**: Contains the `Feature` dataclass that represents application features with proper type hints and serialization methods.

### UI Components (`ui/`)
- **`components.py`**: Contains the main UI components:
  - `FeatureCard`: Individual feature display card
  - `Dashboard`: Main application window
- **`dialogs.py`**: Contains dialog components:
  - `FeatureDialog`: Detailed feature information dialog
  - `DownloadInstallDialog`: Download progress dialog

### Services (`services/`)
- **`podman_service.py`**: Contains the `PodmanWorker` class that handles container operations in a background thread.

### Utils (`utils/`)
- **`file_utils.py`**: Contains utility functions for:
  - Loading and saving installed images
  - Loading features from JSON
  - Extracting image names from URLs

## Benefits of Modular Structure

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Maintainability**: Easier to find and modify specific functionality
3. **Reusability**: Components can be reused across different parts of the application
4. **Testability**: Individual modules can be tested in isolation
5. **Type Safety**: Better type hints and data validation
6. **Documentation**: Each module is well-documented with docstrings

## Usage

To run the application with the new modular structure:

```bash
python main.py
```

To run the original monolithic version:

```bash
python main.py
```

## Running the Application in a Container

You can run this application in a container using Podman (or Docker) with full GUI support.

### 1. Build the Image

```bash
podman build -t adas-dashboard .
```

### 2. Run the Container (with GUI/X11 support)

```bash
xhost +local:docker  # Allow X11 connections (only needed once per session)
podman run --rm \
    --name adas-dashboard \
    --env DISPLAY=$DISPLAY \
    --env QT_X11_NO_MITSHM=1 \
    --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
    --volume .:/app \
    --network host \
    --interactive \
    --tty \
    adas-dashboard
```

### 3. Using the Provided Script (Recommended)

A script is provided for convenience:

```bash
./run-container.sh
```

This script will:
- Set up X11 permissions
- Build the image (if needed)
- Run the container with the correct settings

### 4. Using Docker Compose (Optional)

You can also use Docker Compose:

```bash
docker-compose up --build
```

Or in detached mode:

```bash
docker-compose up -d --build
```

### Notes
- Make sure you are running in a graphical environment (not over SSH without X11 forwarding).
- The container will display the GUI on your host system.
- For troubleshooting and more details, see `README-Container.md`.

## Migration Notes

The original `main.py` file has been preserved for reference. The new modular structure maintains the same functionality while providing better organization and maintainability.

All imports have been updated to use the new module structure, and the code has been enhanced with:
- Type hints for better IDE support
- Comprehensive docstrings
- Better error handling
- Cleaner separation of UI, business logic, and data models 