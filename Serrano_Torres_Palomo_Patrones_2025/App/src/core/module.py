"""Base module class used by operation modules (sum, mul, div, etc.).

This module defines :class:`Module`, a convenience subclass of
``Structure`` that places common behaviour and drawing for modules used in
the game grid.
"""

import pygame as pg
from settings import CELL_SIZE_PX
from .structure import Structure


class Module(Structure):
    """Generic module base class.

    Subclasses should override :meth:`calcular` to implement their specific
    operation.
    """

    def __init__(self, position, gameManager):
        gx, gy = int(position[0]), int(position[1])
        px = gx * CELL_SIZE_PX + CELL_SIZE_PX // 2
        py = gy * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.grid_position = (gx, gy)
        self.position = pg.Vector2((px, py))
        self.gameManager = gameManager
        self.radius = 15
        self.color = (50, 60, 150)

    def update(self):
        """Per-frame update (placeholder in base class)."""
        pass

    def draw(self):
        """Draw the module as a circle on the game surface."""
        cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
        draw_pos = (int(self.position.x - cam.x), int(self.position.y - cam.y))
        pg.draw.circle(self.gameManager.screen, self.color, draw_pos, self.radius)

    def calcular(self):
        """Compute the module-specific operation. Subclasses must override."""
        pass

    def getCost(self):
        """Optional: return module build cost."""
        pass