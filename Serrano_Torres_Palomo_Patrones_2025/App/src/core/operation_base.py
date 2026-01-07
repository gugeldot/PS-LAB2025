import pygame as pg
from settings import CELL_SIZE_PX
from .structure import Structure


class OperationModule(Structure):
    """Base operation module that handles connections and processing flow.

    Concrete operation logic (operate) must be implemented by subclasses.
    """
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
        self.color = (255, 218, 185)
        self.sprite = None
        # Allow subclasses to load their sprite during initialization
        try:
            self._load_sprite()
        except Exception:
            # Avoid breaking initialization if sprite loading fails
            pass

    # --- connection properties ---
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

    # --- connection helpers ---
    def connectInput(self, conveyor):
        """Automatic connection based on Y position (compatible with Merger logic)"""
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

    # --- sprite hook ---
    def _load_sprite(self):
        """Hook for subclasses to load a sprite. Default does nothing."""
        pass

    # --- life-cycle ---
    def update(self):
        self.process()

    def draw(self):
        cam = getattr(self.gameManager, 'camera', pg.Vector2(0, 0))
        draw_pos = (int(self.position.x - cam.x), int(self.position.y - cam.y))

        if self.sprite:
            sprite_rect = self.sprite.get_rect(center=draw_pos)
            self.gameManager.screen.blit(self.sprite, sprite_rect)
        else:
            pg.draw.circle(self.gameManager.screen, self.color, draw_pos, self.radius)
            font = pg.font.Font(None, 24)
            text = font.render(self.get_symbol(), True, (255, 255, 255))
            text_rect = text.get_rect(center=draw_pos)
            self.gameManager.screen.blit(text, text_rect)

    def get_symbol(self):
        return "?"

    # --- processing ---
    def process(self):
        # Verificar que tenemos ambos inputs y al menos un output
        if not self.input1 or not self.input2:
            return

        if not self.output:
            return

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
            # waiting for both
            pass

    def operate(self, a, b):
        raise NotImplementedError()
