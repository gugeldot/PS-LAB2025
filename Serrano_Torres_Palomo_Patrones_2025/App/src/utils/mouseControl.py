"""Mouse input helper used by the UI.

This module exposes :class:`MouseControl`, a thin wrapper that tracks the
mouse position, draws a custom cursor sprite and helps translate clicks to
grid coordinates. It uses :func:`inspect_cell` to check if a clicked grid
cell contains a structure.
"""

import pygame as pg
from settings import *
import pathlib
from utils.cursor_inspector import inspect_cell


class MouseControl:
    """Mouse helper that manages cursor image, position and click handling.

    Public API
    - update(): refresh internal mouse position
    - draw(): blit the custom cursor image to the screen
    - checkClickEvent(event): handle a pygame event and return context or None
    """

    def __init__(self, gameManager):
        """Initialize mouse helper bound to a GameManager instance.

        The constructor attempts to resolve the cursor sprite inside the
        project's Assets folder with a fallback path for alternative layouts.
        """
        self.gameManager = gameManager
        self.position = pg.Vector2(0, 0)
        # boolean indicating if the last clicked cell had a structure
        self.has_structure = False

        pg.mouse.set_visible(False)
        # Base path for App/ (two levels up from this file)
        BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

        # Construct cursor image path
        CURSOR_IMG_PATH = BASE_DIR / "Assets" / "Sprites" / "cursor.png"

        # Fallback if asset is in an alternate location
        if not CURSOR_IMG_PATH.exists():
            alt = pathlib.Path(__file__).resolve().parent / "Assets" / "Sprites" / "cursor.png"
            if alt.exists():
                CURSOR_IMG_PATH = alt

        # Load and resize the cursor image
        self.cursor_img = pg.image.load(CURSOR_IMG_PATH).convert_alpha()
        self.cursor_img = pg.transform.scale(self.cursor_img, (MOUSE_WIDTH, MOUSE_HEIGHT))
        self.cursor_offset = pg.Vector2(-25, -20)

    def update(self):
        """Update internal mouse position from pygame state."""
        self.position = pg.Vector2(pg.mouse.get_pos())

    def draw(self):
        """Draw the custom cursor image to the GameManager screen."""
        self.gameManager.screen.blit(
            self.cursor_img, (self.position.x + self.cursor_offset.x, self.position.y + self.cursor_offset.y)
        )

    def checkClickEvent(self, event):
        """Handle a pygame event and return context for click events.

        Returns
        - True/False if left-click (indicates whether a structure was present)
        - None for non-left clicks or if the event is not a mouse button event
        """
        if event.type == pg.MOUSEBUTTONDOWN:
            # calculate grid cell from current mouse pos, taking camera offset into account
            try:
                cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
            except Exception:
                cam = pg.Vector2(0, 0)
            mx, my = int(self.position.x + cam.x), int(self.position.y + cam.y)
            gx = mx // CELL_SIZE_PX
            gy = my // CELL_SIZE_PX

            if event.button == 1:  # left button
                # check map presence
                try:
                    m = self.gameManager.map
                    has_struct, info = inspect_cell(m, gx, gy)
                    self.has_structure = bool(has_struct)
                    print(f"Left click on cell ({gx}, {gy}) -> {info}")
                    return self.has_structure
                except Exception as e:
                    self.has_structure = False
                    print("Error consulting the map on click:", e)
                    return self.has_structure

            elif event.button == 2:  # middle
                print("Middle button pressed at", self.position)
                return None
            elif event.button == 3:  # right
                print("Right button pressed at", self.position)
                return None
        # not a click event
        return None