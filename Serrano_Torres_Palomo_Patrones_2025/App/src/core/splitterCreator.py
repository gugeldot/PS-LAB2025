from .structureCreator import *
from .splitterModule import *


class SplitterCreator(StructureCreator):
    def createStructure(self,position,gameManager):
        return SplitterModule(position,gameManager)