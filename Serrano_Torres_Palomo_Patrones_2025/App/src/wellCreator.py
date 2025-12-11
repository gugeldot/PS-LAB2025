from structureCreator import *
from well import *

class MineCreator(StructureCreator):
    def createStructure(self,x,y,consumingNumber):
        return Well((x,y),consumingNumber)