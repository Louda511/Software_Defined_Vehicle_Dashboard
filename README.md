# ADAS App Store - Modular Structure

This project has been refactored into a modular structure for better maintainability and organization.

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

## Migration Notes

The original `main.py` file has been preserved for reference. The new modular structure maintains the same functionality while providing better organization and maintainability.

All imports have been updated to use the new module structure, and the code has been enhanced with:
- Type hints for better IDE support
- Comprehensive docstrings
- Better error handling
- Cleaner separation of UI, business logic, and data models 