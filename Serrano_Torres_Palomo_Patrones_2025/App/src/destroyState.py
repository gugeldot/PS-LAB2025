from gameState import GameState
import pygame as pg

class DestroyState(GameState):
    def __init__(self, placementController):
        self.placementController = placementController

    def handleClickEvent(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.placementController.update()
            self.placementController.destroyStructure()
    
    def update(self):
        self.placementController.update()
    
    def draw(self):
        self.placementController.drawDestroy()