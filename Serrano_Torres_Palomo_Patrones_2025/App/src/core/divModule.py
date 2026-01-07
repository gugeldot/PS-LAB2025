"""Division module: performs division between two inputs.

Note: may be a placeholder if division module is not fully implemented.
"""

import pygame as pg
import pathlib
from core import conveyor
from .module import *
from utils.app_paths import APP_ROOT as BASE_DIR


class DivModule(Module):
    def __init__(self, position, gameManager):
        self.gameManager = gameManager
        self.position = position
        gx, gy = int(position[0]), int(position[1])
        px = gx * CELL_SIZE_PX + CELL_SIZE_PX // 2
        py = gy * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.grid_position = (gx, gy)
        self.position = pg.Vector2((px, py))
        self.radius = 15
        self.color = (100, 150, 50)
        self.inConveyor1 = None #dividendo
        self.inConveyor2 = None #divisor
        self.outConveyor = None #para el cociente
        self.outConveyor2 = None #para el resto
        # BASE_DIR provided by utils.app_paths
        IMG_PATH = BASE_DIR / "Assets" / "Sprites" / "div_module_minimal.png"
        try:
            self.img = pg.image.load(str(IMG_PATH)).convert_alpha()
            self.img = pg.transform.scale(self.img, (40, 40))
        except Exception as e:
            print(f"Warning: Could not load div_module_minimal.png: {e}")
            self.img = None

    def calcular(self):
        '''
        Divide the first input by the second input and returns the result.
        '''
        number1 = self.inConveyor1.pop()
        number2 = self.inConveyor2.pop()
        if number1 is not None and number2 is not None:
            if number2 != 0:
                self.outConveyor.push(number1 / number2)
                self.outConveyor2.push(number1 % number2)
        return None
    
    def draw(self):
        cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
        draw_pos = (int(self.position.x - cam.x), int(self.position.y - cam.y))
        
        if self.img:
            sprite_rect = self.img.get_rect(center=draw_pos)
            self.gameManager.screen.blit(self.img, sprite_rect)
        else:
            # Fallback: dibujar círculo si no hay sprite
            pg.draw.circle(self.gameManager.screen, self.color, draw_pos, self.radius)

    def setConveyor(self, conveyor, position):
        if position == 1:
            self.inConveyor1 = conveyor
        elif position == 2:
            self.inConveyor2 = conveyor
        elif position == 3:
            self.outConveyor = conveyor
        elif position ==4:
            self.outConveyor2= conveyor
    def getCost(self):
        return 15
    