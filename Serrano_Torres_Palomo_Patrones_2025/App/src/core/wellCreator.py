from .structureCreator import *
from .well import *

class WellCreator(StructureCreator):
    def createStructure(self,position,consumingNumber):
        return Well(position,consumingNumber)