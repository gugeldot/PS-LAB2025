
class StructureCreator:

    def createStructure(self,x,y,gameManager):
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def getSpritePreview(self):
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def getCost(self) -> int:
        #  por defecto es gratis
        return 0