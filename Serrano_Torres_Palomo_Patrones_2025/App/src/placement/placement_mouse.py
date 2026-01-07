import pygame as pg
from settings import CELL_SIZE_PX


def mouse_cell_conversion(controller):
    """Convert screen mouse position to grid cell and store on controller.
    This keeps the same behaviour as the previous PlacementController.mouseCellConversion
    but extracted so the logic can be tested or reused.
    """
    if controller.mousePosition is None:
        controller.mousePosition = controller.mouse.position
    try:
        cam = getattr(controller.gameManager, 'camera', None) or pg.Vector2(0, 0)
    except Exception:
        cam = pg.Vector2(0, 0)

    mx = int(controller.mousePosition.x + cam.x)
    my = int(controller.mousePosition.y + cam.y)

    controller.cellPosX = mx // CELL_SIZE_PX
    controller.cellPosY = my // CELL_SIZE_PX
