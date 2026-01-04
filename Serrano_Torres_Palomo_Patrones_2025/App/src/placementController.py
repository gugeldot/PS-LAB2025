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
        if self.mousePosition is None:
            self.mousePosition = self.mouse.position 
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
        pg.draw.circle(self.gameManager.screen, self.factory.getSpritePreview(), (int(self.mousePosition.x+offset), int(self.mousePosition.y+offset)), 15)
        font = pg.font.Font(None, 24)

    def drawDestroy(self):
        '''
        Los bordes de la pantalla se vuelven rojos con distinta opacidad segun la distancia al centro de la pantalla
        '''
        s = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        s.fill((255, 0, 0, 50))  # semitransparente
        self.gameManager.screen.blit(s, (0, 0))


            

    def buildStructure(self):
        self.mouseCellConversion()
        if self.factory is not None and not self.checkStructureInCell() and self.checkCost():
            #construir mina
            structure=self.factory.createStructure((self.cellPosX, self.cellPosY), self.gameManager)
            self.gameManager.structures.append(structure)
            self.gameManager.map.placeStructure(self.cellPosX, self.cellPosY, structure)
            self.gameManager.spendPoints(self.factory.getCost())
            print(f"------------------------Mina creada en ({self.cellPosX}, {self.cellPosY})")
    
    def destroyStructure(self):
        #eliminar estructura del mapa y de la lista de estructuras
        self.mouseCellConversion()
        if self.cellPosX is None or self.cellPosY is None :
                print("Posicion del raton no valida para destruir.")
                return
        if self.checkStructureInCell():
            structure= self.getStructureInCell()
            
            # Verificar si la estructura es una mina o un pozo
            if structure and hasattr(structure, '__class__'):
                structure_type = structure.__class__.__name__.lower()
                if 'mine' in structure_type or 'well' in structure_type:
                    print(f"No se puede destruir {structure.__class__.__name__} en {structure.grid_position}.")
                    return
            
            structure= self.gameManager.map.removeStructure(self.cellPosX, self.cellPosY)
            if structure in self.gameManager.structures:
                    self.gameManager.structures.remove(structure)
                    self.gameManager.addPoints(structure.getCost())  # Reembolsar la mitad del coste
                    print(f"Estructura en {structure.grid_position} destruida.")
            else:
                    print("Estructura no encontrada en la lista.")

    def checkCost(self):
        #comprobar si tiene recursos suficientes
        return self.gameManager.canAffordBuilding(self.factory)
    def getStructureInCell(self):
        #obtener estructura en la celda
        try:
                    map = self.gameManager.map
                    has_struct= inspect_cell(map,self.cellPosX, self.cellPosY)
                    if has_struct:
                        structure = map.getCell(self.cellPosX, self.cellPosY).getStructure()
                        return structure
                    else:
                        return None
        except Exception as e:
                    print("Error al consultar el mapa en el click:", e)
                    return None
        return None
    
    def checkStructureInCell(self):
        #comprobar si es valido
       try:
                    map = self.gameManager.map
                    has_struct, info = inspect_cell(map,self.cellPosX, self.cellPosY)
                    self.has_structure = bool(has_struct)
                    print(f"Casilla esta {info}")
                    return self.has_structure
       except Exception as e:
                    self.has_structure = False
                    print("Error al consultar el mapa en el click:", e)
                    return self.has_structure
       return None

         