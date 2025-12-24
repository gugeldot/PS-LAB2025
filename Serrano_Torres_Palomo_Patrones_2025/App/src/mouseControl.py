import pygame as pg
from settings import *
import pathlib 
from utils.cursor_inspector import inspect_cell
class MouseControl:
    def __init__(self,gameManager):
        '''
        init del raton
        '''
        self.gameManager=gameManager
        self.position = pg.Vector2(0, 0)
        # booleano que indica si la última celda clicada tenía una estructura
        self.has_structure = False

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
            # calculate grid cell from current mouse pos, taking camera offset into account
            try:
                cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
            except Exception:
                cam = pg.Vector2(0, 0)
            mx, my = int(self.position.x + cam.x), int(self.position.y + cam.y)
            gx = mx // CELL_SIZE_PX
            gy = my // CELL_SIZE_PX

            if event.button == 1:  # Botón izquierdo
                # check map presence
                try:
                    m = self.gameManager.map
                    has_struct, info = inspect_cell(m, gx, gy)
                    self.has_structure = bool(has_struct)
                    print(f"Click izquierdo en celda ({gx}, {gy}) -> {info}")
                    return self.has_structure
                except Exception as e:
                    self.has_structure = False
                    print("Error al consultar el mapa en el click:", e)
                    return self.has_structure

            elif event.button == 2:  # Botón medio
                print("Botón medio presionado en", self.position)
                return None
            elif event.button == 3:  # Botón derecho
                print("Botón derecho presionado en", self.position)
                return None
        # si no es un evento de click devolvemos None
        return None