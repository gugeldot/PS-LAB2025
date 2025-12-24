import pygame as pg
from settings import CELL_SIZE_PX
from .structure import *


class SplitterModule(Structure):

    def __init__(self, position, gameManager):
        gx, gy = int(position[0]), int(position[1])
        px = gx * CELL_SIZE_PX + CELL_SIZE_PX // 2
        py = gy * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.grid_position = (gx, gy)
        self.position = pg.Vector2((px, py))
        self.gameManager = gameManager

        self.inputConveyor = None
        self.outputConveyor1 = None
        self.outputConveyor2 = None
        self.alternate = False

        self.radius = 15
        self.color = (135, 206, 250)

    def update(self):
        self.process()
    
    def draw(self):
        cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
        draw_pos = (int(self.position.x - cam.x), int(self.position.y - cam.y))
        pg.draw.circle(self.gameManager.screen, self.color, draw_pos, self.radius)
        
    def process(self):
        '''Splits numbers from input alternating between two outputs'''
        if self.inputConveyor is None:
            return
        
        # Only process if a number has reached the end of the input conveyor
        number = self.inputConveyor.pop()
        if number is None:
            return
        
        if self.alternate:
            if self.outputConveyor1:
                self.outputConveyor1.push(number)
                print(f"Splitter: sent {number} to output1 (upper)")
        else:
            if self.outputConveyor2:
                self.outputConveyor2.push(number)
                print(f"Splitter: sent {number} to output2 (lower)")
        
        self.alternate = not self.alternate
    
    def connectInput(self, conveyor):
        self.inputConveyor = conveyor
    
    def connectOutput1(self, conveyor):
        self.outputConveyor1 = conveyor
    
    def connectOutput2(self, conveyor):
        self.outputConveyor2 = conveyor