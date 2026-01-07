"""Placement inspection helpers.

Utilities to check whether a structure exists at the current mouse/grid
position maintained by a `PlacementController`-like object. These helpers
wrap `utils.cursor_inspector.inspect_cell` and preserve existing fallbacks.
"""

from utils.cursor_inspector import inspect_cell


def get_structure_in_cell(controller):
    try:
        map_obj = controller.gameManager.map
        has_struct = inspect_cell(map_obj, controller.cellPosX, controller.cellPosY)
        if has_struct:
            return map_obj.getCell(controller.cellPosX, controller.cellPosY).getStructure()
        else:
            return None
    except Exception as e:
        print("Error al consultar el mapa en el click:", e)
        return None


def check_structure_in_cell(controller):
    try:
        map_obj = controller.gameManager.map
        has_struct, info = inspect_cell(map_obj, controller.cellPosX, controller.cellPosY)
        controller.has_structure = bool(has_struct)
        print(f"Casilla esta {info}")
        return controller.has_structure
    except Exception as e:
        controller.has_structure = False
        print("Error al consultar el mapa en el click:", e)
        return controller.has_structure
