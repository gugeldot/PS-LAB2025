from .gameState import GameState
from .conveyor_helpers import (
    handle_click_event as _handle_click_event,
    update as _update_helper,
    draw as _draw_helper,
    get_structure_at_grid as _get_structure_at_grid_helper,
)
import pygame as pg


class ConveyorBuildState(GameState):
    """Thin state object that delegates heavy logic to helpers in
    `conveyor_helpers.py` to keep the file small and readable while
    preserving the public API and behavior.
    """

    def __init__(self, gameManager, conveyorCreator):
        self.gameManager = gameManager
        self.conveyorCreator = conveyorCreator
        self.start_pos = None
        self.current_mouse_pos = None
        self.mouse = gameManager.mouse

    def handleClickEvent(self, event):
        _handle_click_event(self, event)

    def update(self):
        _update_helper(self)

    def draw(self):
        _draw_helper(self)

    def _get_structure_at_grid(self, grid_x, grid_y):
        return _get_structure_at_grid_helper(self, grid_x, grid_y)
