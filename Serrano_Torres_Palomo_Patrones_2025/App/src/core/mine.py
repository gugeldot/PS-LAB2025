"""Mine structure.

Implements :class:`Mine`, a producer structure that emits numbers at a fixed
production interval. The class stores both grid and pixel coordinates and
renders itself on the game surface.
"""

import pygame as pg
from .structure import Structure
from settings import CELL_SIZE_PX


class Mine(Structure):
    """A Mine that produces numeric values into an output conveyor.

    Parameters
    ----------
    position: tuple[int,int]
        Grid coordinates (x, y) where the mine will be placed.
    number: int
        Base numeric value produced by this mine (upgrades may change
        the effective value).
    gameManager: object
        Reference to the GameManager instance used for timing and rendering.
    """

    def __init__(self, position, number, gameManager):
        # position expected as grid coords (x, y)
        gx, gy = int(position[0]), int(position[1])
        px = gx * CELL_SIZE_PX + CELL_SIZE_PX // 2
        py = gy * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.grid_position = (gx, gy)
        self.position = pg.Vector2((px, py))
        self.number = number
        self.gameManager = gameManager
        self.radius = 15
        self.color = (255, 0, 0)
        self.outputConveyor = None

    def update(self):
        """Periodic update called from the main loop (placeholder)."""
        pass

    def connectOutput(self, conveyor):
        """Connect a conveyor to this mine's output."""
        self.outputConveyor = conveyor

    def produce(self, conveyor):
        """Push the mine's value into the provided conveyor.

        Uses an upgraded effective value when available.
        """
        val = getattr(self, '_effective_number', self.number)
        conveyor.push(val)

    def draw(self):
        """Render the mine and the current number on screen."""
        cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
        draw_pos = (int(self.position.x - cam.x), int(self.position.y - cam.y))
        pg.draw.circle(self.gameManager.screen, self.color, draw_pos, self.radius)
        effective = getattr(self, '_effective_number', getattr(self, '_base_number', self.number))
        font = pg.font.Font(None, 24)
        text = font.render(str(effective), True, (255, 255, 255))
        text_rect = text.get_rect(center=draw_pos)
        self.gameManager.screen.blit(text, text_rect)
