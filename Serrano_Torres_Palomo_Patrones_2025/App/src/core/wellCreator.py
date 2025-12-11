from .structureCreator import *
from .well import *


class WellCreator(StructureCreator):
    def createStructure(self,position,consumingNumber,gameManager):
        return Well(position,consumingNumber,gameManager)