import pygame as pg
from Serrano_Torres_Palomo_Patrones_2025.App.src.core import conveyor
from module import *

class SumModule(Module):
    def __init__(self, position, gameManager):
        self.gameManager = gameManager
        self.position = position
        gx, gy = int(position[0]), int(position[1])
        px = gx * CELL_SIZE_PX + CELL_SIZE_PX // 2
        py = gy * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.grid_position = (gx, gy)
        self.position = pg.Vector2((px, py))
        self.radius = 15
        self.color = (150, 100, 50)  # Color específico para SumModule
        self.inConveyor1 = None
        self.inConveyor2 = None
        self.outConveyor = None


    def calcular(self):
        '''
        Suma los números de entrada y devuelve el resultado.
        '''
        number1 = self.inConveyor1.pop()
        number2 = self.inConveyor2.pop()
        if number1 is not None and number2 is not None:
            self.outConveyor.push(number1 + number2)
        return None
    
    def setConveyor(self, conveyor, position):
        if position == 1:
            self.inConveyor1 = conveyor
        elif position == 2:
            self.inConveyor2 = conveyor
        elif position == 3:
            self.outConveyor = conveyor