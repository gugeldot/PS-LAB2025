"""Sprite loading helpers for assets.

Provides a small utility to load and scale images from the project's
Assets/Sprites folder. The function returns a :class:`pygame.Surface` or
``None`` if loading fails.
"""

import pathlib
import pygame as pg
from utils.app_paths import APP_ROOT as BASE_DIR


def load_sprite_from_assets(filename: str, size=(40, 40)):
    """Load a sprite from Assets/Sprites and scale it to ``size``.

    Returns a :class:`pygame.Surface` or ``None`` if the file is not found
    or loading fails. Errors are caught and logged as warnings to avoid
    breaking the game flow during startup.
    """
    try:
        sprite_path = BASE_DIR / "Assets" / "Sprites" / filename
        if sprite_path.exists():
            surf = pg.image.load(str(sprite_path)).convert_alpha()
            surf = pg.transform.scale(surf, size)
            return surf
        else:
            print(f"Warning: sprite not found at {sprite_path}")
    except Exception as e:
        print(f"Warning: Could not load sprite {filename}: {e}")
    return None
