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
            # calculate grid cell from current mouse pos
            mx, my = int(self.position.x), int(self.position.y)
            gx = mx // CELL_SIZE_PX
            gy = my // CELL_SIZE_PX

            if event.button == 1:  # Botón izquierdo
                # check map presence
                try:
                    m = self.gameManager.map
                    cell = m.getCell(gx, gy)
                    if cell is None:
                        print(f"Click izquierdo en celda ({gx}, {gy}) -> Fuera del mapa")
                    else:
                        if cell.isEmpty():
                            print(f"Click izquierdo en celda ({gx}, {gy}) -> Empty")
                        else:
                            s = cell.structure
                            # report basic info about the structure
                            info = s.__class__.__name__
                            if hasattr(s, 'number'):
                                info += f" number={getattr(s, 'number')}"
                            if hasattr(s, 'consumingNumber'):
                                info += f" consumingNumber={getattr(s, 'consumingNumber')}"
                            # try to include grid_position if available
                            if hasattr(s, 'grid_position'):
                                info += f" grid={getattr(s, 'grid_position')}"
                            print(f"Click izquierdo en celda ({gx}, {gy}) -> {info}")
                except Exception as e:
                    print("Error al consultar el mapa en el click:", e)

            elif event.button == 2:  # Botón medio
                print("Botón medio presionado en", self.position)
            elif event.button == 3:  # Botón derecho
                print("Botón derecho presionado en", self.position)