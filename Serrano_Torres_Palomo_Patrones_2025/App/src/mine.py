import pygame as pg
from structure import *

class Mine(Structure):
    def __init__(self, position, number):
        '''
        Inicializa la mina en la posicion dada
        '''
        self.position = pg.Vector2(position)
        self.number = number
        self.radius = 15
        self.color = (255, 0, 0)  #rojo

    def update(self):
        '''
        '''
        pass  

    def draw(self, screen):
        '''
        Dibuja la mina en la pantalla
        '''
        pg.draw.circle(screen, self.color, (self.position.x, self.position.y), self.radius)
        # Dibujar el numero en el centro de la mina
        font = pg.font.Font(None, 24)
        text = font.render(str(self.number), True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.position.x, self.position.y))
        screen.blit(text, text_rect)
                                                    