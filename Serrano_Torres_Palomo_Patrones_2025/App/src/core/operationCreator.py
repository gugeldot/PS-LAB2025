from .structureCreator import StructureCreator
from .operationModule import SumModule, MultiplyModule

class SumCreator(StructureCreator):
    def createStructure(self, position, gameManager):
        return SumModule(position, gameManager)

class MultiplyCreator(StructureCreator):
    def createStructure(self, position, gameManager):
        return MultiplyModule(position, gameManager)
