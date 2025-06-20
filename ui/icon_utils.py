"""
Utilities for handling themed SVG icons.
"""
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, Qt, QSize
from .styles import theme_manager

def _get_themed_svg_data(icon_path: str) -> bytes:
    """Reads an SVG file and replaces its stroke color with the current theme's text color."""
    try:
        with open(icon_path, 'r', encoding='utf-8') as f:
            svg_data = f.read()
        
        # Replace hardcoded colors with the current theme's text color.
        # This makes the icons adapt to the day/night themes.
        themed_svg_data = svg_data.replace('stroke="white"', f'stroke="{theme_manager.theme["text"]}"')
        themed_svg_data = themed_svg_data.replace('stroke="#FFFFFF"', f'stroke="{theme_manager.theme["text"]}"')
        themed_svg_data = themed_svg_data.replace('fill="currentColor"', f'fill="{theme_manager.theme["text"]}"')
        
        return themed_svg_data.encode('utf-8')
    except FileNotFoundError:
        print(f"Warning: Icon SVG not found at {icon_path}")
        return b''

def get_themed_icon(icon_path: str) -> QIcon:
    """Loads a themed SVG icon as a QIcon."""
    themed_svg_bytes = _get_themed_svg_data(icon_path)
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

def get_themed_pixmap(icon_path: str, size: QSize) -> QPixmap:
    """Loads a themed SVG icon as a QPixmap of a specific size."""
    themed_svg_bytes = _get_themed_svg_data(icon_path)
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)

    if not themed_svg_bytes:
        return pixmap

    renderer = QSvgRenderer(QByteArray(themed_svg_bytes))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return pixmap 