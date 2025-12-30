from .structureCreator import *
from .well import *


class WellCreator(StructureCreator):
    def createStructure(self, position, consumingNumber=None, gameManager=None, locked=False):
        """Create a Well instance. Accepts an optional `locked` kwarg used when
        restoring from save files.
        """
        try:
            return Well(position, consumingNumber, gameManager, locked=locked)
        except TypeError:
            # Fallback for older Well signature
            w = Well(position, consumingNumber, gameManager)
            try:
                w.locked = bool(locked)
            except Exception:
                pass
            return w