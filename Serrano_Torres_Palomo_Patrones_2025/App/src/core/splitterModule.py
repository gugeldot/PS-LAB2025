import pygame as pg
from settings import CELL_SIZE_PX
import pathlib
from .structure import *


class SplitterModule(Structure):

    def __init__(self, position, gameManager):
        gx, gy = int(position[0]), int(position[1])
        px = gx * CELL_SIZE_PX + CELL_SIZE_PX // 2
        py = gy * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.grid_position = (gx, gy)
        self.position = pg.Vector2((px, py))
        self.gameManager = gameManager

        self.inputConveyor = None
        self.outputConveyor1 = None
        self.outputConveyor2 = None
        self.alternate = False

        # Cargar sprite PNG
        try:
            # Subimos de src/core/ a App/ (dos niveles arriba)
            base_dir = pathlib.Path(__file__).resolve().parent.parent.parent
            sprite_path = base_dir / "Assets" / "Sprites" / "splitterSimple.png"
            self.original_sprite = pg.image.load(str(sprite_path)).convert_alpha()
            # Escalar a 45x45 pixels
            self.original_sprite = pg.transform.scale(self.original_sprite, (45, 45))
        except Exception as e:
            print(f"Warning: Could not load splitter sprite: {e}")
            self.original_sprite = None

        self.radius = 22
        self.color = (174, 214, 241)  # Azul cielo pastel

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
        # SVG base: entrada izquierda, salidas derecha y arriba
        # Necesitamos rotar para que coincida con las conexiones reales
        
        input_direction = self._get_connection_direction(self.inputConveyor, is_input=True)
        output1_direction = self._get_connection_direction(self.outputConveyor1, is_input=False)
        output2_direction = self._get_connection_direction(self.outputConveyor2, is_input=False)
        
        # Mapeo de direcciones a rotaciones
        # El SVG base tiene: entrada=izquierda(180°), salida1=derecha(0°), salida2=arriba(90°)
        if input_direction == "left":
            return 0  # No rotation needed
        elif input_direction == "right":
            return 180
        elif input_direction == "up":
            return 90
        elif input_direction == "down":
            return -90
        
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
        '''Splits numbers from input alternating between two outputs'''
        if self.inputConveyor is None:
            return
        
        # Only process if a number has reached the end of the input conveyor
        number = self.inputConveyor.pop()
        if number is None:
            return
        
        if self.alternate:
            if self.outputConveyor1:
                self.outputConveyor1.push(number)
                print(f"Splitter: sent {number} to output1 (upper)")
        else:
            if self.outputConveyor2:
                self.outputConveyor2.push(number)
                print(f"Splitter: sent {number} to output2 (lower)")
        
        self.alternate = not self.alternate
    
    @property
    def input(self):
        return self.inputConveyor
    
    @input.setter
    def input(self, value):
        self.inputConveyor = value

    @property
    def output1(self):
        return self.outputConveyor1
    
    @output1.setter
    def output1(self, value):
        self.outputConveyor1 = value

    @property
    def output2(self):
        return self.outputConveyor2
    
    @output2.setter
    def output2(self, value):
        self.outputConveyor2 = value

    def connectInput(self, conveyor):
        self.input = conveyor
    
    def connectOutput1(self, conveyor):
        self.output1 = conveyor
    
    def connectOutput2(self, conveyor):
        self.output2 = conveyor