from .conveyor import Conveyor
from .structureCreator import StructureCreator


class ConveyorCreator(StructureCreator):
    """
    Creator para cintas transportadoras.
    Requiere dos posiciones: inicio y fin.
    """
    
    def createStructure(self, start_pos, gameManager, end_pos=None):
        """
        Crea una cinta transportadora entre dos puntos.
        start_pos: posición inicial (puede ser tuple de grid o pg.Vector2 de píxeles)
        end_pos: posición final (puede ser tuple de grid o pg.Vector2 de píxeles)
        """
        if end_pos is None:
            # Si no hay end_pos, usar start_pos como ambos (cinta de longitud 0)
            end_pos = start_pos
            
        # Convertir a Vector2 si son coordenadas de grid
        import pygame as pg
        from settings import CELL_SIZE_PX
        
        if isinstance(start_pos, tuple):
            start_x = start_pos[0] * CELL_SIZE_PX + CELL_SIZE_PX // 2
            start_y = start_pos[1] * CELL_SIZE_PX + CELL_SIZE_PX // 2
            start_pos = pg.Vector2(start_x, start_y)
        
        if isinstance(end_pos, tuple):
            end_x = end_pos[0] * CELL_SIZE_PX + CELL_SIZE_PX // 2
            end_y = end_pos[1] * CELL_SIZE_PX + CELL_SIZE_PX // 2
            end_pos = pg.Vector2(end_x, end_y)
            
        return Conveyor(start_pos, end_pos, gameManager)
    
    def getSpritePreview(self):
        """Color pastel para preview de cinta"""
        return (189, 195, 199)  # Gris plateado pastel
    
    def getCost(self) -> int:
        """Costo base de construir una cinta"""
        return 5  # Más barato que los operadores
