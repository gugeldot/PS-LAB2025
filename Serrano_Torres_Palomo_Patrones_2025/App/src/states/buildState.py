"""Build state: handles placement/build interactions.

This module provides `BuildState`, a GameState used when the player is
in build mode. It delegates placement actions to a `PlacementController`.
"""

from .gameState import GameState
import pygame as pg


class BuildState(GameState):
    """State used for constructing structures via the placement controller.

    The state forwards input events and draw/update calls to the
    provided `placementController` to preserve the original behaviour.
    """

    def __init__(self, placementController):
        self.placementController = placementController

    def handleClickEvent(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.placementController.update()
            self.placementController.buildStructure()
    
    def update(self):
        self.placementController.update()
    
    def draw(self):
        self.placementController.draw()

    def setFactory(self, factory):
        self.placementController.setFactory(factory)