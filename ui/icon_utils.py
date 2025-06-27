"""
Utilities for handling themed SVG icons.
"""
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, Qt, QSize
from .styles import theme_manager

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