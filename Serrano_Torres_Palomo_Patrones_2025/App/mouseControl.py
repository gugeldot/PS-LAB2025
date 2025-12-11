import pygame as pg
from settings import *

class MouseControl:
    def __init__(self,gameManager):
        '''
        init del raton
        '''
        self.gameManager=gameManager
        self.pos = pg.Vector2(0, 0)
        self.rel = pg.Vector2(0, 0)
        pg.mouse.set_visible(False)
        self.cursor_img = pg.image.load("Resources/Sprites/cursor.png").convert_alpha()  # convert_alpha() para transparencia
        self.cursor_img = pg.transform.scale(self.cursor_img, (MOUSE_WIDTH, MOUSE_HEIGHT)) #ajustar tamaño a tamaño especificado en setting
    def update(self):
        '''
        '''
        self.pos = pg.Vector2(pg.mouse.get_pos())
        self.rel = pg.Vector2(pg.mouse.get_rel())
        
    def draw(self):
        '''
        '''
        #pg.draw.circle(self.gameManager.screen, (255, 0, 0), (int(self.pos.x), int(self.pos.y)), 5)
        cursor_offset = (self.cursor_img.get_width()//2, self.cursor_img.get_height()//2)
        self.gameManager.screen.blit(self.cursor_img, (self.pos.x - cursor_offset[0], self.pos.y - cursor_offset[1]))
    
    def checkClickEvent(self,event):
        '''
        Detecta clicks del mouse
        '''
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botón izquierdo
                print("Botón izquierdo presionado en", self.pos)
            elif event.button == 2:  # Botón medio
                print("Botón medio presionado en", self.pos)
            elif event.button == 3:  # Botón derecho
                print("Botón derecho presionado en", self.pos)