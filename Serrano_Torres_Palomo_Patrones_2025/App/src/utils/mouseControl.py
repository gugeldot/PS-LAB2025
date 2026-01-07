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
        #  Ruta base del proyecto (carpeta `App`). Subimos un nivel más
        #  para que la ruta quede en '/.../App' en lugar de '/.../App/src'.
        BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent  # parent de src -> App

        #  Construir la ruta de cualquier recurso en Assets
        CURSOR_IMG_PATH = BASE_DIR / "Assets" / "Sprites" / "cursor.png"

        # Si por alguna razón el asset no existe en la ubicación esperada,
        # intentar una ruta alternativa (compatibilidad con setups que
        # coloquen Assets dentro de src). Esto evita fallos al arrancar.
        if not CURSOR_IMG_PATH.exists():
            alt = pathlib.Path(__file__).resolve().parent / "Assets" / "Sprites" / "cursor.png"
            if alt.exists():
                CURSOR_IMG_PATH = alt

        # Cargar la imagen
        self.cursor_img = pg.image.load(CURSOR_IMG_PATH).convert_alpha()
        self.cursor_img = pg.transform.scale(self.cursor_img, (MOUSE_WIDTH, MOUSE_HEIGHT)) #ajustar tamaño a tamaño especificado en setting
        self.cursor_offset = pg.Vector2(-25, -20)
    def update(self):
        '''
        '''
        self.position = pg.Vector2(pg.mouse.get_pos())
        
        
    def draw(self):
        '''
        Dibuja el cursor en la posicion
        '''
        
        self.gameManager.screen.blit(self.cursor_img, (self.position.x + self.cursor_offset.x, self.position.y + self.cursor_offset.y))
    
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