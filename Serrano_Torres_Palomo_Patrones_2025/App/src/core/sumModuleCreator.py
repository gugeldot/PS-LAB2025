from .sumModule import SumModule
from .structureCreator import *

class SumModuleCreator(StructureCreator):
    def createStructure(self,position,gameManager):
        return SumModule(position,gameManager)
    
    def getSpritePreview(self):
        return ((173, 216, 230))