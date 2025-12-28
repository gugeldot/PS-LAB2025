import pygame as pg
from settings import CELL_SIZE_PX
import pathlib
from .structure import *


class MergerModule(Structure):

    def __init__(self, position, gameManager):
        # position is grid coords (x,y)
        gx, gy = int(position[0]), int(position[1])
        px = gx * CELL_SIZE_PX + CELL_SIZE_PX // 2
        py = gy * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.grid_position = (gx, gy)
        self.position = pg.Vector2((px, py))
        self.gameManager = gameManager

        self.inputConveyor1 = None
        self.inputConveyor2 = None
        self.outputConveyor = None

        # Cargar sprite PNG
        try:
            # Subimos de src/core/ a App/ (tres niveles arriba)
            base_dir = pathlib.Path(__file__).resolve().parent.parent.parent
            sprite_path = base_dir / "Assets" / "Sprites" / "mergerSimple.png"
            self.original_sprite = pg.image.load(str(sprite_path)).convert_alpha()
            # Escalar a 45x45 pixels
            self.original_sprite = pg.transform.scale(self.original_sprite, (45, 45))
        except Exception as e:
            print(f"Warning: Could not load merger sprite: {e}")
            self.original_sprite = None

        self.radius = 22
        self.color = (210, 180, 222)  # Lavanda pastel

    def update(self):
        self.process()
    
    def draw(self):
        cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
        draw_pos = (int(self.position.x - cam.x), int(self.position.y - cam.y))
        
        if self.original_sprite:
            # Determinar rotación basada en conexiones
            rotation = self._calculate_rotation()
            
            # Rotar sprite si es necesario
            if rotation != 0:
                rotated_sprite = pg.transform.rotate(self.original_sprite, rotation)
            else:
                rotated_sprite = self.original_sprite
                
            # Centrar el sprite
            sprite_rect = rotated_sprite.get_rect(center=draw_pos)
            self.gameManager.screen.blit(rotated_sprite, sprite_rect)
        else:
            # Fallback: dibujar círculo si no hay sprite
            pg.draw.circle(self.gameManager.screen, self.color, draw_pos, self.radius)
    
    def _calculate_rotation(self):
        """Calcula la rotación necesaria basada en las conexiones actuales"""
        # SVG base: entradas izquierda y abajo, salida derecha
        # Necesitamos rotar para que coincida con las conexiones reales
        
        output_direction = self._get_connection_direction(self.outputConveyor, is_input=False)
        
        # Mapeo de direcciones a rotaciones
        # El SVG base tiene: salida=derecha(0°)
        if output_direction == "right":
            return 0  # No rotation needed
        elif output_direction == "left":
            return 180
        elif output_direction == "up":
            return -90
        elif output_direction == "down":
            return 90
        
        return 0  # Default no rotation
    
    def _get_connection_direction(self, conveyor, is_input):
        """Determina la dirección de una conexión basada en las posiciones"""
        if not conveyor:
            return None
            
        if is_input:
            # Para input, miramos de dónde viene (start del conveyor)
            other_pos = conveyor.start_pos
        else:
            # Para output, miramos hacia dónde va (end del conveyor)
            other_pos = conveyor.end_pos
            
        dx = other_pos.x - self.position.x
        dy = other_pos.y - self.position.y
        
        # Determinar dirección predominante
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "down" if dy > 0 else "up"
        
    def process(self):
        '''Combines numbers from two inputs into one output'''
        if self.outputConveyor is None:
            return
            
        if self.inputConveyor1 and not self.inputConveyor1.isEmpty():
            number = self.inputConveyor1.pop()
            if number is not None:
                self.outputConveyor.push(number)
        
        if self.inputConveyor2 and not self.inputConveyor2.isEmpty():
            number = self.inputConveyor2.pop()
            if number is not None:
                self.outputConveyor.push(number)
    
    @property
    def input1(self):
        return self.inputConveyor1
    
    @input1.setter
    def input1(self, value):
        self.inputConveyor1 = value

    @property
    def input2(self):
        return self.inputConveyor2
    
    @input2.setter
    def input2(self, value):
        self.inputConveyor2 = value

    @property
    def output(self):
        return self.outputConveyor
    
    @output.setter
    def output(self, value):
        self.outputConveyor = value

    def connectInput1(self, conveyor):
        self.input1 = conveyor
    
    def connectInput2(self, conveyor):
        self.input2 = conveyor
    
    def connectOutput(self, conveyor):
        self.output = conveyor