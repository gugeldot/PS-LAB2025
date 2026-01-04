import pathlib
import pygame as pg
from core import conveyor
from .module import *

class MulModule(Module):
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
        #  Ruta base del proyecto (un nivel arriba de src)
        BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent  # parent de src

        #  Construir la ruta de cualquier recurso en Assets
        IMG_PATH = BASE_DIR / "Assets" / "Sprites" / "mul-module.png"
        self.img = pg.image.load(IMG_PATH).convert_alpha()
        self.img = pg.transform.scale(self.img, (60, 60)) 

    def calcular(self):
        '''
        Suma los números de entrada y devuelve el resultado.
        '''
        number1 = self.inConveyor1.pop()
        number2 = self.inConveyor2.pop()
        if number1 is not None and number2 is not None:
            self.outConveyor.push(number1 * number2)
        return None
    
    def draw(self):
        self.gameManager.screen.blit(self.img, (self.position.x -30, self.position.y -30 ))
    
        '''
        pg.draw.rect(self.gameManager.screen, (173, 216, 230), (self.position.x, self.position.y, 17, 17))
        font = pg.font.Font(None, 24)
        text = font.render('+', True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.position.x, self.position.y))
        self.gameManager.screen.blit(text, text_rect)
        '''
        

    def setConveyor(self, conveyor, position):
        if position == 1:
            self.inConveyor1 = conveyor
        elif position == 2:
            self.inConveyor2 = conveyor
        elif position == 3:
            self.outConveyor = conveyor

    def getCost(self):
        return 15