"""Drawing helpers for placement UI.

This small module extracts drawing code used by the placement flow so the
visual logic can be tested and documented separately. Provides `draw_preview`
and `draw_destroy` helpers which operate on a `PlacementController`-like
object (expects `gameManager`, `mousePosition` and `factory`).
"""

import pygame as pg


def draw_preview(controller):
    """Draw a small preview/indicator at the mouse cursor using the factory sprite.
    Matches the previous PlacementController.draw behaviour.
    """
    offset = -15
    try:
        sprite = controller.factory.getSpritePreview()
    except Exception:
        sprite = (255, 0, 255)
    pg.draw.circle(controller.gameManager.screen, sprite, (int(controller.mousePosition.x + offset), int(controller.mousePosition.y + offset)), 15)


def draw_destroy(controller):
    """Draw the red translucent overlay used when destroy-mode is active.
    """
    s = pg.Surface((controller.gameManager.screen.get_width(), controller.gameManager.screen.get_height()), pg.SRCALPHA)
    s.fill((255, 0, 0, 50))
    controller.gameManager.screen.blit(s, (0, 0))
