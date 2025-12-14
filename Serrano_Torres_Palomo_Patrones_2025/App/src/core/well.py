import pygame as pg
from .structure import *
from settings import CELL_SIZE_PX


class Well(Structure):
    def __init__(self, position, consumingNumber, gameManager):
        '''
        Inicializa el pozo usando coordenadas de grilla (x,y). La posición
        pixel se calcula a partir de CELL_SIZE_PX y el centro de la celda.
        '''
        gx, gy = int(position[0]), int(position[1])
        px = gx * CELL_SIZE_PX + CELL_SIZE_PX // 2
        py = gy * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.grid_position = (gx, gy)
        self.position = pg.Vector2((px, py))
        self.consumingNumber = consumingNumber
        self.gameManager = gameManager
        self.radius = 15
        self.color = (0, 150, 0)        # verde oscuro

    def update(self):
        '''
        '''
        pass
    
    def consume(self, conveyor):
        number = conveyor.pop()
        if number is not None and number == self.consumingNumber:
            print(f"Well consumed {number}! ✓")

    def draw(self):
        '''
        Dibuja la mina en la pantalla
        '''
        pg.draw.circle(self.gameManager.screen, self.color, (self.position.x, self.position.y), self.radius)
        # Dibujar el numero en el centro de la mina
        font = pg.font.Font(None, 24)
        text = font.render(str(self.consumingNumber), True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.position.x, self.position.y))
        self.gameManager.screen.blit(text, text_rect)