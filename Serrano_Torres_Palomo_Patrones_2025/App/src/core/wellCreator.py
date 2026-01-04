from .structureCreator import *
from .well import *


class WellCreator(StructureCreator):
    def createStructure(self, position, consumingNumber, gameManager, locked: bool = False):
        # Accept an optional `locked` flag when restoring from saves.
        return Well(position, consumingNumber, gameManager, locked=locked)
    def getSpritePreview(self):
        #verde desaturado
        return ((128, 200, 128))