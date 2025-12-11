import pygame as pg

import gameManager
from .structure import *
from core.structure import Structure

class MergerModule(Structure):

    def __init__(self,position,gameManager):
        self.position = pg.Vector2(position)
        self.gameManager=gameManager

        #si son parte del composite entonces cambiar
        self.inConveyorSlot1 = None
        self.inConveyorSlot2 = None
        self.inConveyotSlot3 = None
        self.outConveyorSlot1= None

        self.radius = 15
        self.color = (0, 0, 255)  #azu

    def update(self):
        pass
    
    def draw(self):
        pg.draw.circle(self.gameManager.screen, self.color, (self.position.x, self.position.y), self.radius)
        
    def process(self):
        '''
        Procesa los numeros que le entran por los espacios y los combina
        '''
        pass