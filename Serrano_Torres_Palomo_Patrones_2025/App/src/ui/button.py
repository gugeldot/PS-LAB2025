"""Small button drawing helpers used by the HUD UI.

This module provides utilities to draw rounded buttons using the HUD's
font and color palette while avoiding circular imports with the HUD module.
The primary public functions are ``draw_button`` and ``_draw_rounded_rect``.
"""

import importlib
import pygame as pg
from typing import Optional


def _draw_rounded_rect(surface, rect, color, radius, border=0):
    """Draw a rounded rectangle.

    This lightweight wrapper avoids importing the HUD module and exposes a
    single place to draw rounded rectangles with an optional border width.
    Parameters
    - surface: pygame Surface to draw on
    - rect: pygame.Rect describing the area
    - color: fill color or border color
    - radius: corner radius in pixels
    - border: optional border width (0 = filled)
    """
    if border > 0:
        pg.draw.rect(surface, color, rect, border, border_radius=radius)
    else:
        pg.draw.rect(surface, color, rect, border_radius=radius)


def draw_button(hud, screen, rect, label, mouse_pos, can_use=True, sublabel: Optional[str]=None, accent=False, special_style=False):
    """Draw a button using the HUD instance for fonts and Colors.

    hud: the HUD instance (used to access fonts and Colors)
    """
    # Resolve Colors from the HUD module to avoid circular imports.
    Colors = None
    try:
        mod_name = hud.__class__.__module__
        mod = importlib.import_module(mod_name)
        Colors = getattr(mod, 'Colors', None)
    except Exception:
        Colors = None

    # Fallback palette if Colors cannot be resolved (keeps visible text)
    if Colors is None:
        class _C:
            BUTTON_DISABLED = (127, 140, 141)
            TEXT_SECONDARY = (149, 165, 166)
            SUBMENU_HOVER = (41, 128, 185)
            SUBMENU_BUTTON = (52, 152, 219)
            SUBMENU_TEXT = (255, 255, 255)
            BUTTON_HOVER = (149, 175, 192)
            TEXT_PRIMARY = (44, 62, 80)
            BUTTON_DEFAULT = (178, 190, 195)
            WARNING = (253, 203, 110)
            BUTTON_ACTIVE = (130, 204, 221)

        Colors = _C

    is_hover = rect.collidepoint(mouse_pos)

    # Determine color
    if not can_use:
        color = Colors.BUTTON_DISABLED
        text_color = Colors.TEXT_SECONDARY
    elif accent:
        color = Colors.SUBMENU_HOVER if is_hover else Colors.SUBMENU_BUTTON
        text_color = Colors.SUBMENU_TEXT
    elif is_hover:
        color = Colors.BUTTON_HOVER
        text_color = Colors.TEXT_PRIMARY
    else:
        color = Colors.BUTTON_DEFAULT
        text_color = Colors.TEXT_PRIMARY

    if special_style:
        color = Colors.WARNING if is_hover else Colors.BUTTON_ACTIVE
        text_color = Colors.TEXT_PRIMARY

    # Draw background
    _draw_rounded_rect(screen, rect, color, 10)

    # Hover elevation
    if is_hover and can_use:
        shadow_rect = rect.copy()
        shadow_rect.y += 2
        _draw_rounded_rect(screen, shadow_rect, (0, 0, 0, 30), 10)

    # Main text
    try:
        text_surf = hud.font_small.render(label, True, text_color)
        text_rect = text_surf.get_rect(center=(rect.centerx, rect.centery - (5 if sublabel else 0)))
        screen.blit(text_surf, text_rect)
    except Exception:
        # best-effort: draw minimal text using default font
        try:
            f = pg.font.Font(None, 20)
            ts = f.render(label, True, (0, 0, 0))
            screen.blit(ts, (rect.x + 6, rect.y + 6))
        except Exception:
            pass

    # Sublabel
    if sublabel:
        try:
            sublabel_color = Colors.SUBMENU_TEXT if accent else Colors.TEXT_SECONDARY
            sublabel_surf = pg.font.Font(None, 18).render(sublabel, True, sublabel_color)
            sublabel_rect = sublabel_surf.get_rect(center=(rect.centerx, rect.centery + 12))
            screen.blit(sublabel_surf, sublabel_rect)
        except Exception:
            pass
