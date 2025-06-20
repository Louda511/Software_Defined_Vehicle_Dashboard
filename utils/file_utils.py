"""
Utility functions for file operations
"""
import json
import os
from typing import List, Set
from models.feature import Feature

INSTALLED_FILE = 'installed_images.json'


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
    with open('dummy_features.json', 'r') as f:
        data = json.load(f)
        return [Feature.from_dict(feature_data) for feature_data in data]


def extract_image_name(url: str) -> str:
    """Extracts the image name from various Docker Hub URL formats."""
    if not url:
        return ""
    
    # Handle URLs like https://hub.docker.com/_/hello-world
    if '/_/' in url:
        return url.split('/_/')[-1]
    
    # Handle URLs like https://hub.docker.com/r/example/my-image
    if '/r/' in url:
        return url.split('/r/')[-1]
        
    # Fallback for simple names or other URL formats
    return url.rstrip('/').split('/')[-1] 