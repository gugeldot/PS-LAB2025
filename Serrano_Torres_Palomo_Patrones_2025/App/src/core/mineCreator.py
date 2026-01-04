from .structureCreator import *
from .mine import *

class MineCreator(StructureCreator):
    def createStructure(self,position,number,gameManager):
        return Mine(position,number,gameManager)
    
    def getSpritePreview(self):
        return ((200, 128, 128))