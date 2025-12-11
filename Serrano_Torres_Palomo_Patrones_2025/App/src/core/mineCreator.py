from .structureCreator import *
from .mine import *

class MineCreator(StructureCreator):
    def createStructure(self,position,number):
        return Mine(position,number)