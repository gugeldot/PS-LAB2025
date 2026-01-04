from .structureCreator import *
from .mergerModule import *


class MergerCreator(StructureCreator):
    def createStructure(self,position,gameManager):
        return MergerModule(position,gameManager)
    
    def getCost(self) -> int:
        return 20