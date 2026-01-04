from .structureCreator import *
from .splitterModule import *


class SplitterCreator(StructureCreator):
    def createStructure(self,position,gameManager):
        return SplitterModule(position,gameManager)
    
    def getSpritePreview(self):
        # color pastel similar to HUD palette for splitter preview
        return (174, 214, 241)

    def getCost(self) -> int:
        return 20