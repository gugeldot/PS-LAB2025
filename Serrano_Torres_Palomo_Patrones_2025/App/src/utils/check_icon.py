"""Utilities to verify the application icon resource.

These helpers are convenience scripts used during development to check
that the expected icon image exists at `App/Assets/icon.png` and that
``pygame`` can load it. They print diagnostic information to stdout.

Note: they are not used at runtime by the game; they are small dev tools.
"""

import pygame as pg
import pathlib
from utils.app_paths import APP_ROOT as BASE_DIR


def check_icon():
    """Check and report the application's icon availability.

    This function prints the resolved path, whether the file exists and
    attempts to load it using ``pygame.image.load``. Errors are caught and
    printed instead of propagated (suitable for a small dev script).
    """
    icon_path = BASE_DIR / "Assets" / "icon.png"

    print(f"[ICON CHECK] icon path: {icon_path}")
    print(f"[ICON CHECK] exists: {icon_path.exists()}")

    try:
        # pg.image.load can work without opening a window if SDL_image supports it
        img = pg.image.load(str(icon_path))
        print(f"[ICON CHECK] loaded: {type(img)}")
    except Exception as e:
        print(f"[ICON CHECK] failed to load icon: {e}")


if __name__ == '__main__':
    check_icon()
