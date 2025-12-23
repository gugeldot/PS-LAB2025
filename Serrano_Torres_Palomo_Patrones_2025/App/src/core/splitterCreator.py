from .structureCreator import *
from .splitter import *


class SplitterCreator(StructureCreator):
    def createStructure(self,position,gameManager):
        return SplitterModule(position,gameManager)