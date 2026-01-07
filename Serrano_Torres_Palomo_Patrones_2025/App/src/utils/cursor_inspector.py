"""Cursor inspection utilities.

This module provides a small helper used to inspect a grid cell at a
given grid coordinate and returns whether a structure is present plus a
brief informational string. It is used by the mouse/cursor helpers and
other UI components.
"""
from typing import Tuple


def inspect_cell(map_obj, gx: int, gy: int) -> Tuple[bool, str]:
    """Inspect the map cell at grid coordinates (gx, gy).

    Parameters
    - map_obj: an object exposing a ``getCell(x, y)`` method.
    - gx, gy: grid coordinates (integers).

    Returns
    A tuple (has_structure, info):
    - has_structure: True if a structure exists in the cell.
    - info: short string describing the cell ('Empty', 'Out of bounds' or the
      structure class name and optional attributes).
    """
    try:
        cell = map_obj.getCell(gx, gy)
    except Exception as e:
        return False, f"Error al acceder al mapa: {e}"

    if cell is None:
        return False, "Fuera del mapa"

    if hasattr(cell, 'isEmpty') and cell.isEmpty():
        return False, "Empty"

    # si llegamos aquí, asumimos que existe una estructura
    s = getattr(cell, 'structure', None)
    if s is None:
        # estructura no encontrada, tratar como vacío
        return False, "Empty"

    info = s.__class__.__name__
    if hasattr(s, 'number'):
        info += f" number={getattr(s, 'number')}"
    if hasattr(s, 'consumingNumber'):
        info += f" consumingNumber={getattr(s, 'consumingNumber')}"
    if hasattr(s, 'grid_position'):
        info += f" grid={getattr(s, 'grid_position')}"

    return True, info
