from .mulModule import MulModule
from .structureCreator import *

class MulModuleCreator(StructureCreator):
    def createStructure(self,position,gameManager):
        return MulModule(position,gameManager)
    
    def getSpritePreview(self):
        return ((80, 170, 80))
    
    def getCost(self) -> int:
        return 15