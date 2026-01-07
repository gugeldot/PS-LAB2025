"""Global settings used by the game.

This module exposes constants used across the codebase including
screen resolution, frames-per-second target, cursor sizes and map
dimension defaults. It is intentionally small and contains only simple
constants so that Sphinx can include them in the generated documentation.
"""

import math

# General options

# Screen resolution
RESOLUTION = WIDTH, HEIGHT = 1280, 720

FPS = 60

# Cursor sizes (pixels)
MOUSE_HEIGHT = 80
MOUSE_WIDTH = 80


# Graphics: grid cell size in pixels (square cell)
CELL_SIZE_PX = 55

# Default map size (columns, rows)
DEFAULT_MAP_WIDTH = 25
DEFAULT_MAP_HEIGHT = 25