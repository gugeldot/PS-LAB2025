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

        self.inputConveyor1 = None
        self.inputConveyor2 = None
        self.outputConveyor = None

        self.radius = 15
        self.color = (0, 0, 255)

    def update(self):
        self.process()
    
    def draw(self):
        cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
        draw_pos = (int(self.position.x - cam.x), int(self.position.y - cam.y))
        pg.draw.circle(self.gameManager.screen, self.color, draw_pos, self.radius)
        
    def process(self):
        '''Combines numbers from two inputs into one output'''
        if self.outputConveyor is None:
            return
            
        if self.inputConveyor1 and not self.inputConveyor1.isEmpty():
            number = self.inputConveyor1.pop()
            if number is not None:
                self.outputConveyor.push(number)
        
        if self.inputConveyor2 and not self.inputConveyor2.isEmpty():
            number = self.inputConveyor2.pop()
            if number is not None:
                self.outputConveyor.push(number)
    
    @property
    def input1(self):
        return self.inputConveyor1
    
    @input1.setter
    def input1(self, value):
        self.inputConveyor1 = value

    @property
    def input2(self):
        return self.inputConveyor2
    
    @input2.setter
    def input2(self, value):
        self.inputConveyor2 = value

    @property
    def output(self):
        return self.outputConveyor
    
    @output.setter
    def output(self, value):
        self.outputConveyor = value

    def connectInput1(self, conveyor):
        self.input1 = conveyor
    
    def connectInput2(self, conveyor):
        self.input2 = conveyor
    
    def connectOutput(self, conveyor):
        self.output = conveyor