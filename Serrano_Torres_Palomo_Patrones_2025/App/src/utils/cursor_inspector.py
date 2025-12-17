"""Herramientas para inspeccionar celdas desde el cursor.

Proporciona una función modular que puede ser reutilizada por el cursor u
otros componentes para chequear si una celda contiene una estructura y
producir una cadena informativa.
"""
from typing import Tuple


def inspect_cell(map_obj, gx: int, gy: int) -> Tuple[bool, str]:
    """Inspecciona la celda (gx, gy) en `map_obj`.

    Args:
        map_obj: objeto mapa que expone `getCell(x, y)`.
        gx, gy: coordenadas de la celda en la grilla.

    Returns:
        (has_structure, info)
        - has_structure: True si hay una estructura en la celda.
        - info: cadena con información breve (por ejemplo 'Empty', 'Fuera del mapa' o el tipo de estructura).
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
