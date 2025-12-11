from .structureCreator import *
from .mine import *

class MineCreator(StructureCreator):
    def createStructure(self,position,number,gameManager):
        return Mine(position,number,gameManager)