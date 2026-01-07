import pygame as pg
from .renderer import GMRenderer


def draw(gm):
    """Thin compatibility wrapper that delegates to GMRenderer.

    Keeps the original `gm_draw.draw(gm)` entrypoint unchanged.
    """
    renderer = GMRenderer(gm)
    renderer.draw()
