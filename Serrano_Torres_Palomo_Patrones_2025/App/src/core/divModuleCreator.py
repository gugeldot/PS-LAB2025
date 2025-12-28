from .divModule import DivModule
from .structureCreator import *

class DivModuleCreator(StructureCreator):
    def createStructure(self, position, gameManager):
        return DivModule(position, gameManager)
    
    def getSpritePreview(self):
        return ((230, 173, 216))
    
    def getCost(self) -> int:
        return 15