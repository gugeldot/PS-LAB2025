import pygame as pg
from .structure import *
from settings import CELL_SIZE_PX


class Mine(Structure):
    def __init__(self, position,  gameManager, number=None):
        '''
        Inicializa la mina usando coordenadas de grilla (x,y). La posición
        pixel se calcula a partir de CELL_SIZE_PX y el centro de la celda.
        '''
        # position expected as grid coords (x, y)
        gx, gy = int(position[0]), int(position[1])
        px = gx * CELL_SIZE_PX + CELL_SIZE_PX // 2
        py = gy * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.grid_position = (gx, gy)
        self.position = pg.Vector2((px, py))
        self.number = number
        self.gameManager = gameManager
        self.radius = 15
        self.color = (255, 0, 0)  # rojo

    def update(self):
        '''
        '''
        pass
    
    def produce(self, conveyor):
        # Use an effective upgraded number if present, else the base `number`.
        val = getattr(self, '_effective_number', self.number)
        conveyor.push(val)

    def draw(self):
        '''
        Dibuja la mina en la pantalla
        '''
        pg.draw.circle(self.gameManager.screen, self.color, (self.position.x, self.position.y), self.radius)
        # Dibujar el numero en el centro de la mina; show effective upgraded number if present
        effective = getattr(self, '_effective_number', getattr(self, '_base_number', self.number))
        font = pg.font.Font(None, 24)
        text = font.render(str(effective), True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.position.x, self.position.y))
        self.gameManager.screen.blit(text, text_rect)
                                                    