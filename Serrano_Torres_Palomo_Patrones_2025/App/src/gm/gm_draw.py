import pygame as pg
from .renderer import GMRenderer


def draw(gm):
    """Wrapper thin function kept for compatibility: delegates to GMRenderer."""
    renderer = GMRenderer(gm)
    renderer.draw()
