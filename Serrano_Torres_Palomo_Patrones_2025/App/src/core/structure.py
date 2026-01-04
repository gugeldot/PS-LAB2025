from abc import ABC, abstractmethod

class Structure(ABC):
    ''' Es una clase abstracta para el facotry method y eso '''
    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass

    def getCost(self):
        pass

    