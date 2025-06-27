"""
Utility functions for file operations
"""
import json
import os
from typing import List, Set
from models.feature import Feature

INSTALLED_FILE = 'resources/installed_images.json'


def load_installed_images() -> Set[str]:
    """Load the set of installed image names from file"""
    if os.path.exists(INSTALLED_FILE):
        try:
            with open(INSTALLED_FILE, 'r') as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_installed_images(installed_set: Set[str]) -> None:
    """Save the set of installed image names to file"""
    with open(INSTALLED_FILE, 'w') as f:
        json.dump(list(installed_set), f)


def load_features() -> List[Feature]:
    """Load features from JSON file and convert to Feature objects"""
    with open('resources/dummy_features.json', 'r') as f:
        data = json.load(f)
        return [Feature.from_dict(feature_data) for feature_data in data]


def save_features(features: list) -> None:
    """
    Saves a list of features to the dummy_features.json file,
    adapting the format from the backend response.
    """
    adapted_features = []
    for feature in features:
        adapted_features.append({
            "name": feature.get("name"),
            "location": feature.get("location"),
            "description": feature.get("description"),
            "icon": feature.get("pictureUrl")  # Adapt pictureUrl to icon
        })
    
    with open('resources/dummy_features.json', 'w') as f:
        json.dump(adapted_features, f, indent=4)


def extract_image_name(url: str) -> str:
    """Extracts the image name from various Docker Hub URL formats."""
    if not url:
        return ""
    
    # Handle URLs like https://hub.docker.com/_/hello-world
    if '/_/' in url:
        return url.split('/_/')[-1]
    
    # Handle URLs like https://hub.docker.com/r/example/my-image
    if '/r/' in url:
        path = url.split('/r/')[-1]
        return path.split('/')[-1]
        
    # Fallback for simple names or other URL formats
    return url.rstrip('/').split('/')[-1]


def get_active_warning(json_path: str) -> str | None:
    """
    Returns the first active warning key from a JSON file if any, else None.
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        for key in ['drowsy', 'distracted', 'yawning']:
            if data.get(key, False) is True:
                return key
        return None
    except (json.JSONDecodeError, FileNotFoundError):
        # Suppress transient errors due to file being written
        return None
    except Exception as e:
        print(f"Error reading warning data: {e}")
        return None 


def get_active_warnings(json_path: str) -> List[str]:
    """
    Returns a list of all active warning keys from a JSON file.
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        active_warnings = []
        for key in ['drowsy', 'distracted', 'yawning']:
            if data.get(key, False) is True:
                active_warnings.append(key)
        return active_warnings
    except (json.JSONDecodeError, FileNotFoundError):
        # Suppress transient errors due to file being written
        return []
    except Exception as e:
        print(f"Error reading warning data: {e}")
        return [] 