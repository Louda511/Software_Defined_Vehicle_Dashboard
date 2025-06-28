"""
Utilities for handling themed SVG icons.
"""
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, Qt, QSize
from .styles import theme_manager
import requests
import os
import base64
import re
from urllib.parse import urlparse

def decode_and_save_base64_image(base64_data: str, cache_dir: str = 'resources/cache') -> str:
    """Decode a base64 data URL and save it as a cached image"""
    try:
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Extract the base64 data from the data URL
        # Format: data:image/png;base64,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
        
        # Parse the data URL
        match = re.match(r'data:image/(\w+);base64,(.+)', base64_data)
        if not match:
            raise ValueError("Invalid base64 data URL format")
        
        image_type, base64_string = match.groups()
        
        # Generate a unique filename based on the content hash
        content_hash = str(hash(base64_string))[:8]
        filename = f"base64_{content_hash}.{image_type}"
        cache_path = os.path.join(cache_dir, filename)
        
        # Check if already cached
        if os.path.exists(cache_path):
            return cache_path
        
        # Decode and save the image
        image_data = base64.b64decode(base64_string)
        with open(cache_path, 'wb') as f:
            f.write(image_data)
        
        return cache_path
    except Exception as e:
        print(f"Failed to decode base64 image: {e}")
        return None

def download_and_cache_image(url: str, cache_dir: str = 'resources/cache') -> str:
    """Download an image from URL and cache it locally"""
    try:
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Generate cache filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename or '.' not in filename:
            filename = f"cached_{hash(url)}.png"
        
        cache_path = os.path.join(cache_dir, filename)
        
        # Check if already cached
        if os.path.exists(cache_path):
            return cache_path
        
        # Download the image
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Save to cache
        with open(cache_path, 'wb') as f:
            f.write(response.content)
        
        return cache_path
    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return None

def _get_svg_data_with_color(icon_path: str, color: str | None = None) -> bytes:
    """Reads an SVG file and replaces its color with the provided color or the theme's text color, unless it's weather-clear.svg."""
    # Do not recolor weather-clear.svg so it stays yellow
    if icon_path.endswith("weather-clear.svg"):
        try:
            with open(icon_path, 'r', encoding='utf-8') as f:
                return f.read().encode('utf-8')
        except FileNotFoundError:
            print(f"Warning: Icon SVG not found at {icon_path}")
            return b''
    if color is None:
        color = theme_manager.theme["text"]
    try:
        with open(icon_path, 'r', encoding='utf-8') as f:
            svg_data = f.read()
        themed_svg_data = svg_data.replace('stroke="white"', f'stroke="{color}"')
        themed_svg_data = themed_svg_data.replace('stroke="#FFFFFF"', f'stroke="{color}"')
        themed_svg_data = themed_svg_data.replace('fill="currentColor"', f'fill="{color}"')
        return themed_svg_data.encode('utf-8')
    except FileNotFoundError:
        print(f"Warning: Icon SVG not found at {icon_path}")
        return b''

def get_themed_icon(icon_path: str, color_override: str | None = None) -> QIcon:
    """Loads a themed SVG icon as a QIcon, with an optional color override."""
    # Handle base64 data URLs
    if icon_path.startswith('data:image/'):
        cached_path = decode_and_save_base64_image(icon_path)
        if cached_path:
            # Load as regular image (not SVG)
            pixmap = QPixmap(cached_path)
            if not pixmap.isNull():
                return QIcon(pixmap)
        # Fallback to default icon if decode fails
        return get_themed_icon('resources/icons/store.svg')
    
    # Handle remote URLs
    if icon_path.startswith('http'):
        cached_path = download_and_cache_image(icon_path)
        if cached_path:
            # Load as regular image (not SVG)
            pixmap = QPixmap(cached_path)
            if not pixmap.isNull():
                return QIcon(pixmap)
        # Fallback to default icon if download fails
        return get_themed_icon('resources/icons/store.svg')
    
    # Handle local SVG files
    themed_svg_bytes = _get_svg_data_with_color(icon_path, color_override)
    if not themed_svg_bytes:
        return QIcon()

    renderer = QSvgRenderer(QByteArray(themed_svg_bytes))
    size = renderer.defaultSize()
    if not size.isValid():
        return QIcon()
        
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)

def get_themed_pixmap(icon_path: str, size: QSize, color_override: str | None = None) -> QPixmap:
    """Loads a themed SVG icon as a QPixmap of a specific size."""
    themed_svg_bytes = _get_svg_data_with_color(icon_path, color_override)
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)

    if not themed_svg_bytes:
        return pixmap

    renderer = QSvgRenderer(QByteArray(themed_svg_bytes))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return pixmap 