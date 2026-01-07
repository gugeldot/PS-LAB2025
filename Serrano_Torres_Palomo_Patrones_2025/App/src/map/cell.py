from typing import Optional, Tuple


class Cell:
	"""Container for a single grid cell.

	This class stores the cell grid coordinates and an optional reference to a
	structure placed in the cell.

	Attributes:
		position (Tuple[int, int]): Grid coordinates (x, y).
		structure: Optional reference to a structure object placed in this cell.
	"""

	def __init__(self, position: Tuple[int, int]):
		self.position: Tuple[int, int] = (int(position[0]), int(position[1]))
		self.structure = None

	def isEmpty(self) -> bool:
		"""Return True if the cell has no structure."""
		return self.structure is None

	def setStructure(self, structure) -> None:
		"""Place ``structure`` into this cell.

		This will overwrite any existing structure. The caller may prefer to
		check :meth:`isEmpty` before calling this method.

		Args:
			structure: Any object representing a placed structure.
		"""
		self.structure = structure

	def removeStructure(self):
		"""Remove and return the structure currently in the cell, or ``None``.

		Returns:
			The removed structure instance, or ``None`` if the cell was empty.
		"""
		s = self.structure
		self.structure = None
		return s

	def getStructure(self):
		"""Return the structure currently stored in the cell, or ``None``."""
		return self.structure

