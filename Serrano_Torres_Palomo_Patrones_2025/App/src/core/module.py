import pygame as pg
from settings import CELL_SIZE_PX
from .structure import *

class Module(Structure):
    def __init__(self, position, gameManager):
        '''
        
        '''
        gx, gy = int(position[0]), int(position[1])
        px = gx * CELL_SIZE_PX + CELL_SIZE_PX // 2
        py = gy * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.grid_position = (gx, gy)
        self.position = pg.Vector2((px, py))
        self.gameManager = gameManager
        self.radius = 15
        self.color = (50, 60, 150)

    def update(self):
        '''
        '''
        pass

    def draw(self):
        pg.draw.circle(self.gameManager.screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
    
    def calcular(self):
        '''
        '''
        pass