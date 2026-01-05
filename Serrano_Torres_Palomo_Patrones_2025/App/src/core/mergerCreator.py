from .structureCreator import *
from .mergerModule import *


class MergerCreator(StructureCreator):
    def createStructure(self,position,gameManager):
        return MergerModule(position,gameManager)
    
    def getSpritePreview(self):
        # color pastel similar to HUD palette for merger preview
        return (210, 180, 222)

    def getCost(self) -> int:
        return 20