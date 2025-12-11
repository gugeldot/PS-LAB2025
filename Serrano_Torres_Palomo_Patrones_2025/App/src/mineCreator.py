from structureCreator import *
from mine import *

class MineCreator(StructureCreator):
    def createStructure(self,x,y,number):
        return Mine((x,y),number)