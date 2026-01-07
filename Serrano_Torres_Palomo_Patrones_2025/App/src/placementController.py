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
        # Convert screen mouse position to world coordinates by adding camera offset,
        # then compute the grid cell indices. This ensures placing/destroying respects
        # the current camera scroll.
        try:
            cam = getattr(self.gameManager, 'camera', None) or pg.Vector2(0, 0)
        except Exception:
            cam = pg.Vector2(0, 0)

        mx = int(self.mousePosition.x + cam.x)
        my = int(self.mousePosition.y + cam.y)

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
        # If the mouse isn't over a valid map cell, don't allow placement
        try:
            map_obj = getattr(self.gameManager, 'map', None)
            if map_obj is None:
                print("No map available for placement")
                return False
            if self.cellPosX is None or self.cellPosY is None:
                print("Cursor not over a valid cell - placement aborted")
                return False
            if not (0 <= self.cellPosX < map_obj.width and 0 <= self.cellPosY < map_obj.height):
                print(f"Cursor outside map bounds ({self.cellPosX},{self.cellPosY}) - placement aborted")
                return False
        except Exception:
            # If any error occurs when checking map bounds, abort placement for safety
            print("Error validating map cell for placement - aborting")
            return False

        if self.factory is not None and not self.checkStructureInCell() and self.checkCost():
            #construir mina
            structure=self.factory.createStructure((self.cellPosX, self.cellPosY), self.gameManager)
            self.gameManager.structures.append(structure)
            self.gameManager.map.placeStructure(self.cellPosX, self.cellPosY, structure)
            # Prefer using gm.build_costs mapping if present so displayed
            # button costs are authoritative. Fall back to creator.getCost().
            cost = None
            try:
                costs_map = getattr(self.gameManager, 'build_costs', None) or {}
                cname = self.factory.__class__.__name__.lower() if self.factory is not None else ''
                if costs_map:
                    if 'sum' in cname:
                        cost = int(costs_map.get('sum', self.factory.getCost()))
                    elif 'mul' in cname or 'multiply' in cname:
                        cost = int(costs_map.get('mul', self.factory.getCost()))
                    elif 'div' in cname:
                        cost = int(costs_map.get('div', self.factory.getCost()))
                    elif 'splitter' in cname:
                        cost = int(costs_map.get('splitter', self.factory.getCost()))
                    elif 'merger' in cname:
                        cost = int(costs_map.get('merger', self.factory.getCost()))
                    elif 'conveyor' in cname or 'convey' in cname:
                        cost = int(costs_map.get('conveyor', self.factory.getCost()))
                if cost is None:
                    # fallback to creator-defined cost
                    cost = int(self.factory.getCost())
            except Exception:
                try:
                    cost = int(self.factory.getCost())
                except Exception:
                    cost = 0

            try:
                self.gameManager.spendPoints(cost)
            except Exception:
                pass
            print(f"------------------------Mina creada en ({self.cellPosX}, {self.cellPosY})")
            # Volver a modo normal tras construir
            try:
                self.gameManager.setState(self.gameManager.normalState)
            except Exception:
                pass
    
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
                # Determine refund using gm.build_costs mapping when available
                refund = None
                try:
                    costs_map = getattr(self.gameManager, 'build_costs', None) or {}
                    sname = structure.__class__.__name__.lower()
                    if costs_map:
                        if 'sum' in sname:
                            refund = int(costs_map.get('sum', structure.getCost()))
                        elif 'mul' in sname or 'multiply' in sname:
                            refund = int(costs_map.get('mul', structure.getCost()))
                        elif 'div' in sname:
                            refund = int(costs_map.get('div', structure.getCost()))
                        elif 'splitter' in sname:
                            refund = int(costs_map.get('splitter', structure.getCost()))
                        elif 'merger' in sname:
                            refund = int(costs_map.get('merger', structure.getCost()))
                        elif 'conveyor' in sname or 'convey' in sname:
                            refund = int(costs_map.get('conveyor', structure.getCost()))
                    if refund is None:
                        refund = int(structure.getCost())
                except Exception:
                    try:
                        refund = int(structure.getCost())
                    except Exception:
                        refund = 0

                # Give the refund (matches displayed build cost)
                self.gameManager.addPoints(refund)
                print(f"Estructura en {structure.grid_position} destruida. Reembolso: {refund} pts")
                return True
            else:
                print("Estructura no encontrada en la lista.")
                return False
        else:
            print("No hay estructura en la celda seleccionada")
            return False
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

         