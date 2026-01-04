from typing import Optional, Tuple


class Cell:
	"""Simple container for a map cell.

	Attributes:
		position: tuple[int, int] - grid coordinates (x, y)
		structure: optional reference to a Structure placed in the cell
	"""

	def __init__(self, position: Tuple[int, int]):
		# store as tuple (x, y)
		self.position: Tuple[int, int] = (int(position[0]), int(position[1]))
		self.structure = None

	def isEmpty(self) -> bool:
		"""Return True when the cell has no structure."""
		return self.structure is None

	def setStructure(self, structure) -> None:
		"""Place a structure in the cell. Overwrites any existing structure.

		Note: the caller should check `isEmpty()` if overwriting is undesired.
		"""
		self.structure = structure

	def removeStructure(self):
		"""Remove and return the structure currently in the cell (or None)."""
		s = self.structure
		self.structure = None
		return s
	def getStructure(self):
		"""Return the structure currently in the cell (or None)."""
		return self.structure

