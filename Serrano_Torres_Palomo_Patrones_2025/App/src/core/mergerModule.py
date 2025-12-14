import pygame as pg
from settings import CELL_SIZE_PX
from .structure import *


class MergerModule(Structure):

    def __init__(self, position, gameManager):
        # position is grid coords (x,y)
        gx, gy = int(position[0]), int(position[1])
        px = gx * CELL_SIZE_PX + CELL_SIZE_PX // 2
        py = gy * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.grid_position = (gx, gy)
        self.position = pg.Vector2((px, py))
        self.gameManager = gameManager

        # las in son las entradas y out la salida (mirar sprites del concept art)
        self.inConveyorSlot1 = None
        self.inConveyorSlot2 = None
        self.inConveyotSlot3 = None
        self.outConveyorSlot1 = None

        self.radius = 15
        self.color = (0, 0, 255)  # azul

    def update(self):
        pass
    
    def draw(self):
        pg.draw.circle(self.gameManager.screen, self.color, (self.position.x, self.position.y), self.radius)
        
    def process(self):
        '''
        Procesa los numeros que le entran por los espacios y los combina
        '''
        pass