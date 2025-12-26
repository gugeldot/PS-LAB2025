import pygame as pg
from core.mineCreator import MineCreator
from settings import *
from utils.cursor_inspector import inspect_cell

class PlacementController:
    def __init__(self, gameManager,factory):
        self.gameManager = gameManager
        self.mouse= gameManager.mouse
        self.mousePosition= None
        self.buildMode= False
        self.factory = factory  #el creator

    def setFactory(self, factory):
        self.factory = factory

    def update(self,):
        #hacer metodo draw y dec comprobacion valido
        self.mousePosition = self.mouse.position 
        

    def mouseCellConversion(self):
        mx, my = int(self.mousePosition.x), int(self.mousePosition.y)
        self.cellPosX = mx // CELL_SIZE_PX
        self.cellPosY = my // CELL_SIZE_PX

    def draw(self): 
        '''
        Esto dibuja la estructura en el cursor, como un preview
        '''
        #metodo basico de dibujar ciruclo
        offset= -15
        #cicrulo de color rosa (rojo desaturado)
        pg.draw.circle(self.gameManager.screen, (200, 128, 128), (int(self.mousePosition.x+offset), int(self.mousePosition.y+offset)), 15)
        font = pg.font.Font(None, 24)
        

    def buildStructure(self):
          if self.factory is not None and not self.checkStructureInCell():
                    #construir mina
                    structure=self.factory.createStructure((self.cellPosX, self.cellPosY), 1, self.gameManager)
                    self.gameManager.structures.append(structure)
                    self.gameManager.map.placeStructure(self.cellPosX, self.cellPosY, structure)
                    print(f"------------------------Mina creada en ({self.cellPosX}, {self.cellPosY})")
    
    def checkKeyEvent(self,event):
        #modo construccion
            if event.type == pg.KEYDOWN:
                    if event.key == pg.K_m:
                           self.setFactory(MineCreator())
                           self.buildMode= True
                        
    def checkClickEvent(self,event):
           if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botón izquierdo
                    self.mouseCellConversion()
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

         