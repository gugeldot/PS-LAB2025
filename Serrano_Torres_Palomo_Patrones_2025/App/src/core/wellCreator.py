from .structureCreator import *
from .well import *


class WellCreator(StructureCreator):
    def createStructure(self,position,gameManager,consumingNumber):
        return Well(position,gameManager,consumingNumber)
    def getSpritePreview(self):
        #verde desaturado
        return ((128, 200, 128))