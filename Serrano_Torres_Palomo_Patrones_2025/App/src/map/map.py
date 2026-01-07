import json
import os
import logging
from typing import Optional, Tuple, Dict, Any
import pygame as pg

from patterns.singleton import Singleton
from settings import CELL_SIZE_PX
from .cell import Cell

_logger = logging.getLogger(__name__)



class Map(Singleton):
	"""Grid that stores cells and provides helpers to place and reconnect structures.

	Attributes:
		width (int): Number of columns (x).
		height (int): Number of rows (y).
		cells (list[list[Cell]]): 2D list of Cell instances indexed as cells[y][x].
	"""

	def __init__(self, width: int = 10, height: int = 10):
		# Avoid reinitializing the singleton instance
		if getattr(self, "_initialized", False):
			return

		self.width = int(width)
		self.height = int(height)
		self.cells = [[Cell((x, y)) for x in range(self.width)] for y in range(self.height)]

		self._initialized = True

	def isInsideBounds(self, x: int, y: int) -> bool:
		return 0 <= x < self.width and 0 <= y < self.height

	def getCell(self, x: int, y: int) -> Optional[Cell]:
		"""Return the Cell at grid coordinates (x, y) or None if out of bounds."""
		if not self.isInsideBounds(x, y):
			return None
		return self.cells[y][x]

	def placeStructure(self, x: int, y: int, structure) -> bool:
		"""Place ``structure`` into the cell at ``(x, y)`` if it is empty.

		If placement succeeds the method attempts to record grid coordinates on
		the structure using a best-effort approach (``grid_position`` attribute
		preferred, or ``position`` when the structure signals it expects grid
		coordinates).

		Returns:
			bool: True if placement succeeded, False otherwise.
		"""
		cell = self.getCell(x, y)
		if cell is None or not cell.isEmpty():
			return False

		cell.setStructure(structure)
		try:
			if hasattr(structure, "grid_position"):
				structure.grid_position = (x, y)
			elif getattr(structure, "expects_grid_position", False):
				structure.position = (x, y)
		except Exception:
			# keep robust if the structure rejects attribute assignment
			_logger.debug("Could not set grid position on structure %s", type(structure))

		return True

	def removeStructure(self, x: int, y: int):
		"""Remove and return the structure at (x, y) or None if empty/out of bounds."""
		cell = self.getCell(x, y)
		if cell is None:
			return None
		return cell.removeStructure()

	def update(self) -> None:
		"""Call update() on every structure placed in the map (if available)."""
		for row in self.cells:
			for cell in row:
				if not cell.isEmpty():
					s = cell.structure
					if hasattr(s, "update"):
						try:
							s.update()
						except Exception:
							_logger.exception("Exception while updating structure %s", type(s))

	# --- simple persistence helpers ---
	def to_dict(self) -> Dict:
		"""Serialize map layout to a JSON-friendly dictionary.

		The representation is intentionally conservative and stores only simple
		attributes needed to later reconstruct instances via creator objects.
		"""
		grid = []
		for row in self.cells:
			row_data = []
			for cell in row:
				if cell.isEmpty():
					row_data.append(None)
				else:
					s = cell.structure
					entry = {"class": s.__class__.__name__}
					# common numeric attributes used by current structures
					if hasattr(s, "number"):
						entry["number"] = getattr(s, "number")
					if hasattr(s, "consumingNumber"):
						entry["consumingNumber"] = getattr(s, "consumingNumber")
					# support serializing locked state for structures that expose it (e.g., Well)
					if hasattr(s, "locked"):
						try:
							entry["locked"] = bool(getattr(s, "locked"))
						except Exception:
							entry["locked"] = False
					row_data.append(entry)
			grid.append(row_data)

		return {"width": self.width, "height": self.height, "grid": grid}

	def save_to_file(self, filepath: str) -> None:
		"""Save the current map layout to ``filepath`` as JSON."""
		os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
		with open(filepath, "w", encoding="utf-8") as fh:
			json.dump(self.to_dict(), fh, indent=2)

	@classmethod
	def load_from_file(cls, filepath: str, creators: Dict[str, object] = None, gameManager=None) -> "Map":
		"""Load a map from ``filepath`` and optionally recreate structures.

		Args:
			filepath: Path to the JSON file previously produced by :meth:`to_dict`.
			creators: Optional mapping from structure class name to a creator
				object exposing a ``createStructure(...)`` method used to
				reconstruct instances.
			gameManager: Optional game manager passed through to creators when
				required by their signature.

		Returns:
			Map: A Map instance populated according to the file contents.
		"""
		with open(filepath, "r", encoding="utf-8") as fh:
			data = json.load(fh)

		m = cls(int(data.get("width", 0)), int(data.get("height", 0)))
		grid = data.get("grid", [])
		for y, row in enumerate(grid):
			for x, entry in enumerate(row):
				if not entry:
					continue
				cls_name = entry.get("class")
				if creators and cls_name in creators:
					creator = creators[cls_name]
					# Best-effort argument dispatch for known attributes
					if cls_name == "Mine" and "number" in entry:
						struct = creator.createStructure((x, y), entry["number"], gameManager)
					elif cls_name == "Well" and "consumingNumber" in entry:
						locked_flag = entry.get('locked', False)
						struct = creator.createStructure((x, y), entry["consumingNumber"], gameManager, locked=locked_flag)
					else:
						# fallback: try a few common creator signatures
						struct = None
						try:
							struct = creator.createStructure((x, y), gameManager)
						except TypeError:
							try:
								struct = creator.createStructure((x, y))
							except TypeError:
								struct = None

					if struct is not None:
						m.placeStructure(x, y, struct)

		# Load conveyors if present and a gameManager is available
		conveyors_data = data.get("conveyors", [])
		_logger.debug("Found %d conveyors in save file", len(conveyors_data))
		if conveyors_data and gameManager:
			from core.conveyor import Conveyor  # local import to avoid cycles
			conveyors_list = []
			for conv_data in conveyors_data:
				start_grid = conv_data.get("start")
				end_grid = conv_data.get("end")
				travel_time = conv_data.get("travel_time", 2000)

				if start_grid and end_grid:
					start_pos = pg.Vector2(
						start_grid[0] * CELL_SIZE_PX + CELL_SIZE_PX // 2,
						start_grid[1] * CELL_SIZE_PX + CELL_SIZE_PX // 2,
					)
					end_pos = pg.Vector2(
						end_grid[0] * CELL_SIZE_PX + CELL_SIZE_PX // 2,
						end_grid[1] * CELL_SIZE_PX + CELL_SIZE_PX // 2,
					)

					conv = Conveyor(start_pos, end_pos, gameManager)
					conv.travel_time = travel_time if travel_time else 2000
					conveyors_list.append(conv)
					_logger.debug("Created conveyor from %s to %s", start_grid, end_grid)

			gameManager.conveyors = conveyors_list
			_logger.debug("Stored %d conveyors in gameManager", len(conveyors_list))

		return m

	def reconnect_structures(self, conveyors, game_manager=None):
		"""Re-establish connections between structures and conveyors.

		This method collects conveyors, determines which structures are at the
		conveyor endpoints and connects inputs/outputs on structures using the
		available connect* helper methods exposed by structure instances.

		Args:
			conveyors: Iterable of conveyor-like objects having ``start_pos`` and
				``end_pos`` Vector2 attributes.
			game_manager: Optional game manager instance. When provided some
				convenience references (mine, final_conveyor, well) will be set on
				the manager when they can be determined.
		"""

		def find_structure_at(grid_x: int, grid_y: int):
			if 0 <= grid_y < len(self.cells) and 0 <= grid_x < len(self.cells[grid_y]):
				cell = self.cells[grid_y][grid_x]
				if not cell.isEmpty():
					return cell.structure
			return None

		# Clear previous input/output references on structures
		for row in self.cells:
			for cell in row:
				if not cell.isEmpty():
					struct = cell.structure
					if hasattr(struct, 'input1'):
						struct.input1 = None
					if hasattr(struct, 'input2'):
						struct.input2 = None
					if hasattr(struct, 'inputConveyor1'):
						struct.inputConveyor1 = None
					if hasattr(struct, 'inputConveyor2'):
						struct.inputConveyor2 = None
					if hasattr(struct, 'output'):
						struct.output = None
					if hasattr(struct, 'outputConveyor'):
						struct.outputConveyor = None

		# Collect conveyors per structure
		struct_connections: Dict[Any, Dict[str, list]] = {}
		for conv in conveyors:
			start_grid_x = int(conv.start_pos.x) // CELL_SIZE_PX
			start_grid_y = int(conv.start_pos.y) // CELL_SIZE_PX
			end_grid_x = int(conv.end_pos.x) // CELL_SIZE_PX
			end_grid_y = int(conv.end_pos.y) // CELL_SIZE_PX

			start_struct = find_structure_at(start_grid_x, start_grid_y)
			end_struct = find_structure_at(end_grid_x, end_grid_y)

			if start_struct:
				struct_connections.setdefault(start_struct, {'inputs': [], 'outputs': []})
				struct_connections[start_struct]['outputs'].append(conv)

			if end_struct:
				struct_connections.setdefault(end_struct, {'inputs': [], 'outputs': []})
				struct_connections[end_struct]['inputs'].append(conv)

		# Connect structures based on their types and available connection methods
		for struct, connections in struct_connections.items():
			struct_type = struct.__class__.__name__.lower()
			inputs = connections['inputs']
			outputs = connections['outputs']

			if 'mine' in struct_type:
				if outputs and hasattr(struct, 'connectOutput'):
					struct.connectOutput(outputs[0])

			elif 'well' in struct_type:
				if inputs and hasattr(struct, 'connectInput'):
					struct.connectInput(inputs[0])

			elif any(x in struct_type for x in ['sum', 'mul', 'div', 'operation']):
				if len(inputs) >= 1 and hasattr(struct, 'connectInput1'):
					struct.connectInput1(inputs[0])
				if len(inputs) >= 2 and hasattr(struct, 'connectInput2'):
					struct.connectInput2(inputs[1])
				if outputs and hasattr(struct, 'connectOutput'):
					struct.connectOutput(outputs[0])

			elif 'merger' in struct_type:
				if len(inputs) >= 1 and hasattr(struct, 'connectInput1'):
					struct.connectInput1(inputs[0])
				if len(inputs) >= 2 and hasattr(struct, 'connectInput2'):
					struct.connectInput2(inputs[1])
				if outputs and hasattr(struct, 'connectOutput'):
					struct.connectOutput(outputs[0])

			elif 'splitter' in struct_type:
				if inputs and hasattr(struct, 'connectInput'):
					struct.connectInput(inputs[0])
				if len(outputs) >= 1 and hasattr(struct, 'connectOutput1'):
					struct.connectOutput1(outputs[0])
				if len(outputs) >= 2 and hasattr(struct, 'connectOutput2'):
					struct.connectOutput2(outputs[1])

		# Connect conveyors to each other when endpoints match and there is no structure
		for conv in conveyors:
			for other_conv in conveyors:
				if conv is other_conv:
					continue
				if (int(conv.end_pos.x) == int(other_conv.start_pos.x) and
					int(conv.end_pos.y) == int(other_conv.start_pos.y)):
					grid_x = int(conv.end_pos.x) // CELL_SIZE_PX
					grid_y = int(conv.end_pos.y) // CELL_SIZE_PX
					struct = find_structure_at(grid_x, grid_y)
					if struct is None:
						conv.connectOutput(other_conv)

		# When provided, set some convenient references on the game manager
		if game_manager is not None:
			# find a Mine structure if present
			for row in self.cells:
				for cell in row:
					if not cell.isEmpty() and cell.structure.__class__.__name__ == 'Mine':
						game_manager.mine = cell.structure
						break
				if hasattr(game_manager, 'mine') and game_manager.mine:
					break

			game_manager.final_conveyor = None
			game_manager.well = None
			for conv in conveyors:
				end_grid_x = int(conv.end_pos.x) // CELL_SIZE_PX
				end_grid_y = int(conv.end_pos.y) // CELL_SIZE_PX
				if 0 <= end_grid_y < len(self.cells) and 0 <= end_grid_x < len(self.cells[end_grid_y]):
					cell = self.cells[end_grid_y][end_grid_x]
					if not cell.isEmpty() and cell.structure.__class__.__name__ == 'Well':
						game_manager.final_conveyor = conv
						game_manager.well = cell.structure
						break

