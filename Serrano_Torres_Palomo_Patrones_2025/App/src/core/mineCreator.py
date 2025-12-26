from .structureCreator import *
from .mine import *

class MineCreator(StructureCreator):
    def createStructure(self,position,gameManager,number):
        return Mine(position,gameManager,number)
    
    def getSpritePreview(self):
        return ((200, 128, 128))