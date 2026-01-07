import pygame as pg
from core.mineCreator import MineCreator
from settings import *
from utils.cursor_inspector import inspect_cell
from utils.placement_mouse import mouse_cell_conversion
from utils.placement_draw import draw_preview, draw_destroy
from utils.placement_finance import compute_cost, compute_refund
from utils.placement_popup import notify_destroy_not_allowed
from utils.placement_inspect import get_structure_in_cell, check_structure_in_cell

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
        # delegate to helper that keeps conversion behaviour isolated
        mouse_cell_conversion(self)

    def draw(self): 
        '''
        Esto dibuja la estructura en el cursor, como un preview
        '''
        draw_preview(self)

    def drawDestroy(self):
        '''
        Los bordes de la pantalla se vuelven rojos con distinta opacidad segun la distancia al centro de la pantalla
        '''
        draw_destroy(self)


            

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
            # compute and spend cost using helper (keeps behaviour intact)
            cost = compute_cost(self)
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
                    # delegate popup/restore behaviour to helper
                    notify_destroy_not_allowed(self, structure)
                    return False
            
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
        return get_structure_in_cell(self)
    
    def checkStructureInCell(self):
        #comprobar si es valido
        return check_structure_in_cell(self)

         