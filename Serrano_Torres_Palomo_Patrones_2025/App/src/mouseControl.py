import pygame as pg
from settings import *
import pathlib 
class MouseControl:
    def __init__(self,gameManager):
        '''
        init del raton
        '''
        self.gameManager=gameManager
        self.position = pg.Vector2(0, 0)
       
        pg.mouse.set_visible(False)
        
        #  Ruta base del proyecto (un nivel arriba de src)
        BASE_DIR = pathlib.Path(__file__).resolve().parent.parent  # parent de src

        #  Construir la ruta de cualquier recurso en Assets
        CURSOR_IMG_PATH = BASE_DIR / "Assets" / "Sprites" / "cursor.png"

        # Cargar la imagen
        self.cursor_img = pg.image.load(CURSOR_IMG_PATH).convert_alpha()
        self.cursor_img = pg.transform.scale(self.cursor_img, (MOUSE_WIDTH, MOUSE_HEIGHT)) #ajustar tamaño a tamaño especificado en setting
    
    def update(self):
        '''
        '''
        self.position = pg.Vector2(pg.mouse.get_pos())
        
        
    def draw(self):
        '''
        Dibuja el cursor en la posicion
        '''
        cursor_offset = (self.cursor_img.get_width()//2, self.cursor_img.get_height()//2) #para ajustarlo a la pantalla segun el centro o algo asi
        self.gameManager.screen.blit(self.cursor_img, (self.position.x - cursor_offset[0], self.position.y - cursor_offset[1]))
    
    def checkClickEvent(self,event):
        '''
        Detecta clicks del mouse
        '''
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botón izquierdo
                print("Botón izquierdo presionado en", self.position)
            elif event.button == 2:  # Botón medio
                print("Botón medio presionado en", self.position)
            elif event.button == 3:  # Botón derecho
                print("Botón derecho presionado en", self.position)