import pygame as pg
from settings import CELL_SIZE_PX
from .structure import Structure
import pathlib

class OperationModule(Structure):
    def __init__(self, position, gameManager):
        gx, gy = int(position[0]), int(position[1])
        px = gx * CELL_SIZE_PX + CELL_SIZE_PX // 2
        py = gy * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.grid_position = (gx, gy)
        self.position = pg.Vector2((px, py))
        self.gameManager = gameManager

        self._inputConveyor1 = None
        self._inputConveyor2 = None
        self._outputConveyor = None

        self.radius = 15
        self.color = (255, 218, 185)  # Melocotón pastel (naranja suave)
        
        # Cargar sprite PNG
        self.sprite = None
        self._load_sprite()

    @property
    def input1(self):
        return self._inputConveyor1
    
    @input1.setter
    def input1(self, value):
        self._inputConveyor1 = value

    @property
    def input2(self):
        return self._inputConveyor2
    
    @input2.setter
    def input2(self, value):
        self._inputConveyor2 = value

    @property
    def output(self):
        return self._outputConveyor
    
    @output.setter
    def output(self, value):
        self._outputConveyor = value

    def connectInput(self, conveyor):
        '''Automatic connection based on Y position (compatible with Merger logic)'''
        if conveyor.start_pos.y < self.position.y:
            self.connectInput1(conveyor)
        else:
            self.connectInput2(conveyor)

    def connectInput1(self, conveyor):
        print(f"OperationModule at {self.grid_position}: connected input1")
        self.input1 = conveyor
    
    def connectInput2(self, conveyor):
        print(f"OperationModule at {self.grid_position}: connected input2")
        self.input2 = conveyor
    
    def connectOutput(self, conveyor):
        print(f"OperationModule at {self.grid_position}: connected output")
        self.output = conveyor
    
    def _load_sprite(self):
        '''Cargar sprite PNG del módulo. Cada subclase debe sobreescribir para cargar su imagen'''
        pass

    def update(self):
        self.process()

    def draw(self):
        cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
        draw_pos = (int(self.position.x - cam.x), int(self.position.y - cam.y))
        
        # Si tenemos sprite, dibujarlo
        if self.sprite:
            sprite_rect = self.sprite.get_rect(center=draw_pos)
            self.gameManager.screen.blit(self.sprite, sprite_rect)
        else:
            # Fallback: dibujar círculo si no hay sprite
            pg.draw.circle(self.gameManager.screen, self.color, draw_pos, self.radius)
            # Draw operation symbol
            font = pg.font.Font(None, 24)
            text = font.render(self.get_symbol(), True, (255, 255, 255))
            text_rect = text.get_rect(center=draw_pos)
            self.gameManager.screen.blit(text, text_rect)

    def get_symbol(self):
        return "?"

    def process(self):
        # Verificar que tenemos ambos inputs y al menos un output
        if not self.input1 or not self.input2:
            return
        
        if not self.output:
            return
        
        # Check if both inputs have an item ready at the end of the conveyor
        ready1 = hasattr(self.input1, 'isReady') and self.input1.isReady()
        ready2 = hasattr(self.input2, 'isReady') and self.input2.isReady()

        if ready1 and ready2:
            print(f"OperationModule: both inputs ready! Popping values...")
            val1 = self.input1.pop()
            val2 = self.input2.pop()
            
            if val1 is not None and val2 is not None:
                result = self.operate(val1, val2)
                print(f"OperationModule: {val1} {self.get_symbol()} {val2} = {result}. Pushing to output.")
                self.output.push(result)
        elif ready1 or ready2:
            # Optional: print status if only one is ready to help debugging
            # print(f"OperationModule: waiting... ready1={ready1}, ready2={ready2}")
            pass

    def operate(self, a, b):
        raise NotImplementedError()

class SumModule(OperationModule):
    def get_symbol(self):
        return "+"
    
    def operate(self, a, b):
        return a + b
    
    def _load_sprite(self):
        '''Cargar sprite PNG de sum_module_minimal'''
        try:
            base_dir = pathlib.Path(__file__).resolve().parent.parent.parent
            sprite_path = base_dir / "Assets" / "Sprites" / "sum_module_minimal.png"
            if sprite_path.exists():
                self.sprite = pg.image.load(str(sprite_path)).convert_alpha()
                self.sprite = pg.transform.scale(self.sprite, (40, 40))
            else:
                print(f"Warning: sum_module_minimal.png not found at {sprite_path}")
        except Exception as e:
            print(f"Warning: Could not load sum_module_minimal sprite: {e}")

class MultiplyModule(OperationModule):
    def get_symbol(self):
        return "x"
    
    def operate(self, a, b):
        return a * b
    
    def _load_sprite(self):
        '''Cargar sprite PNG de mul_module_minimal'''
        try:
            base_dir = pathlib.Path(__file__).resolve().parent.parent.parent
            sprite_path = base_dir / "Assets" / "Sprites" / "mul_module_minimal.png"
            if sprite_path.exists():
                self.sprite = pg.image.load(str(sprite_path)).convert_alpha()
                self.sprite = pg.transform.scale(self.sprite, (40, 40))
            else:
                print(f"Warning: mul_module_minimal.png not found at {sprite_path}")
        except Exception as e:
            print(f"Warning: Could not load mul_module_minimal sprite: {e}")

class DivModule(OperationModule):
    def get_symbol(self):
        return "÷"
    
    def operate(self, a, b):
        if b != 0:
            return a // b  # División entera
        return 0
    
    def _load_sprite(self):
        '''Cargar sprite PNG de div_module_minimal'''
        try:
            base_dir = pathlib.Path(__file__).resolve().parent.parent.parent
            sprite_path = base_dir / "Assets" / "Sprites" / "div_module_minimal.png"
            if sprite_path.exists():
                self.sprite = pg.image.load(str(sprite_path)).convert_alpha()
                self.sprite = pg.transform.scale(self.sprite, (40, 40))
            else:
                print(f"Warning: div_module_minimal.png not found at {sprite_path}")
        except Exception as e:
            print(f"Warning: Could not load div_module_minimal sprite: {e}")
