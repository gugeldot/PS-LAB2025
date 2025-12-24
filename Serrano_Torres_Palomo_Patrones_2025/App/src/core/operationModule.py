import pygame as pg
from settings import CELL_SIZE_PX
from .structure import Structure

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
        self.color = (255, 165, 0) # Orange for operations

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

    def update(self):
        self.process()

    def draw(self):
        pg.draw.circle(self.gameManager.screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
        # Draw operation symbol
        font = pg.font.Font(None, 24)
        text = font.render(self.get_symbol(), True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.position.x, self.position.y))
        self.gameManager.screen.blit(text, text_rect)

    def get_symbol(self):
        return "?"

    def process(self):
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

class MultiplyModule(OperationModule):
    def get_symbol(self):
        return "x"
    
    def operate(self, a, b):
        return a * b
