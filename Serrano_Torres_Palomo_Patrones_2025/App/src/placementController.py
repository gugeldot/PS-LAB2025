import pygame as pg
from core.mineCreator import MineCreator
from settings import *
from utils.cursor_inspector import inspect_cell

class PlacementController:
    def __init__(self, gameManager,factory):
        self.gameManager = gameManager
        self.mouse= gameManager.mouse
        self.mousePosition= None
        
        self.factory = factory  #el creator

    def setFactory(self, factory):
        self.factory = factory

    def update(self,):
        #hacer metodo draw y dec comprobacion valido
        self.mousePosition = self.mouse.position 
        self.mouseCellConversion()

    def mouseCellConversion(self):
        mx, my = int(self.mousePosition.x), int(self.mousePosition.y)
        self.cellPosX = mx // CELL_SIZE_PX
        self.cellPosY = my // CELL_SIZE_PX

    def draw(self): 
        '''
        Esto dibuja la estructura en el cursor, como un preview
        '''
        #metodo basico de dibujar ciruclo
        pg.draw.circle(self.gameManager.screen, self.color, (int(self.mousePosition.x), int(self.mousePosition.y)), self.radius)
        font = pg.font.Font(None, 24)
        text = font.render(str(self.consumingNumber), True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.mousePosition.x, self.mousePosition.y))
        self.gameManager.screen.blit(text, text_rect)

    def buildStructure(self):
          if self.factory is not None and not self.checkStructureInCell():
                    #construir mina
                    structure=self.factory.createStructure((self.cellPosX, self.cellPosY), 1, self)
                    self.gameManager.structures.append(structure)
                    self.gameManager.map.placeStructure(self.cellPosX, self.cellPosY, structure)
                    print(f"------------------------Mina creada en ({self.cellPosX}, {self.cellPosY})")
                    
    def checkKeyEvent(self,event):
        #modo construccion
            if event.type == pg.KEYDOWN:
                    if event.key == pg.K_m:
                           self.setFactory(MineCreator())
                           self.buildStructure()

    def checkStructureInCell(self):
        #comprobar si es valido
       try:
                    map = self.gameManager.map
                    has_struct, info = inspect_cell(map,self.cellPosX, self.cellPosY)
                    self.has_structure = bool(has_struct)
                    print(f"Casilla no valida para construir {info}")
                    return self.has_structure
       except Exception as e:
                    self.has_structure = False
                    print("Error al consultar el mapa en el click:", e)
                    return self.has_structure
       return None

         