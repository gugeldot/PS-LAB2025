import json
import os
from typing import Optional, Tuple, Dict
import pygame as pg

from patterns.singleton import Singleton
from settings import CELL_SIZE_PX
from .cell import Cell


class Map(Singleton):
	"""Grid map that stores Cell objects and allows placement/removal/updating

	Attributes:
		width: number of columns (x)
		height: number of rows (y)
		cells: 2D list of Cell instances indexed as cells[y][x]

	The class inherits from the project's basic Singleton base so only one
	Map instance will exist when constructed via Map(width, height).
	"""

	def __init__(self, width: int = 10, height: int = 10):
		# guard to avoid reinitializing singleton instance
		if getattr(self, "_initialized", False):
			return

		self.width = int(width)
		self.height = int(height)
		# create grid cells[y][x]
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
		"""Place `structure` into cell (x, y) if empty.

		Returns True if placement succeeded, False otherwise.
		"""
		cell = self.getCell(x, y)
		if cell is None:
			return False
		if not cell.isEmpty():
			return False

		cell.setStructure(structure)
		# record grid coordinates on the structure without overwriting
		# its pixel `position` (many structures use a Vector2 for pixel coords).
		try:
			# prefer a dedicated attribute `grid_position` if available
			if hasattr(structure, "grid_position"):
				structure.grid_position = (x, y)
			# fallback: only set `position` if structure expects grid coords
			elif getattr(structure, "expects_grid_position", False):
				structure.position = (x, y)
		except Exception:
			# ignore if setting attributes is not supported
			pass

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
							# keep map update robust: ignore structure exceptions
							pass

	# --- simple persistence helpers ---
	def to_dict(self) -> Dict:
		"""Serialize map layout to a JSON-friendly dict.

		This method stores basic information about placed structures (class
		name and a few common attributes). It's intentionally conservative: it
		won't try to fully serialize complex objects (pygame surfaces, game
		manager, etc.). Use creator mappings with load_from_file to restore
		structure instances.
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
		os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
		with open(filepath, "w", encoding="utf-8") as fh:
			json.dump(self.to_dict(), fh, indent=2)

	@classmethod
	def load_from_file(cls, filepath: str, creators: Dict[str, object] = None, gameManager=None):
		"""Load map data from file and (optionally) re-create structures.

		creators: mapping from structure class name (str) to a creator object
				  with a `createStructure(...)` method compatible with the
				  project's creators (see core/*Creator.py). The method will
				  be used with a best-effort set of args depending on the
				  available saved fields.
		gameManager: optional game manager passed to creators when required.
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
						# pass through locked flag if present in the save
						locked_flag = entry.get('locked', False)
						struct = creator.createStructure((x, y), entry["consumingNumber"], gameManager, locked=locked_flag)
					else:
						# fallback: try simple creator signatures
						try:
							struct = creator.createStructure((x, y), gameManager)
						except TypeError:
							try:
								struct = creator.createStructure((x, y))
							except TypeError:
								struct = None

					if struct is not None:
						m.placeStructure(x, y, struct)

		# Load conveyors if present and gameManager is provided
		conveyors_data = data.get("conveyors", [])
		print(f"[Map.load_from_file] Found {len(conveyors_data)} conveyors in save file")
		if conveyors_data and gameManager:
			from core.conveyor import Conveyor
			conveyors_list = []
			for conv_data in conveyors_data:
				start_grid = conv_data.get("start")
				end_grid = conv_data.get("end")
				travel_time = conv_data.get("travel_time", 2000)
				
				if start_grid and end_grid:
					# Convert grid coords to centered pixel positions (like structures do)
					start_pos = pg.Vector2(
						start_grid[0] * CELL_SIZE_PX + CELL_SIZE_PX // 2,
						start_grid[1] * CELL_SIZE_PX + CELL_SIZE_PX // 2
					)
					end_pos = pg.Vector2(
						end_grid[0] * CELL_SIZE_PX + CELL_SIZE_PX // 2,
						end_grid[1] * CELL_SIZE_PX + CELL_SIZE_PX // 2
					)
					
					# Create conveyor with gameManager
					conv = Conveyor(start_pos, end_pos, gameManager)
					conv.travel_time = travel_time if travel_time else 2000
					conveyors_list.append(conv)
					print(f"[Map.load_from_file] Created conveyor from {start_grid} to {end_grid}")
			
			# Store conveyors in gameManager
			gameManager.conveyors = conveyors_list
			print(f"[Map.load_from_file] Stored {len(conveyors_list)} conveyors in gameManager")

		return m

	def reconnect_structures(self, conveyors, game_manager=None):
		"""Re-establish connections between structures and conveyors.

		This is a port of the previous GameManager._reconnect_structures() logic,
		adapted to operate on the Map instance and a list of conveyors. If a
		`game_manager` is provided, the function will also set `game_manager.mine`,
		`game_manager.final_conveyor` and `game_manager.well` when they can be
		determined from the map/conveyors.
		"""

		def find_structure_at(grid_x, grid_y):
			if 0 <= grid_y < len(self.cells) and 0 <= grid_x < len(self.cells[grid_y]):
				cell = self.cells[grid_y][grid_x]
				if not cell.isEmpty():
					return cell.structure
			return None

		# Limpiar conexiones previas en todas las estructuras del mapa
		for row in self.cells:
			for cell in row:
				if not cell.isEmpty():
					struct = cell.structure
					# Limpiar inputs
					if hasattr(struct, 'input1'): struct.input1 = None
					if hasattr(struct, 'input2'): struct.input2 = None
					if hasattr(struct, 'inputConveyor1'): struct.inputConveyor1 = None
					if hasattr(struct, 'inputConveyor2'): struct.inputConveyor2 = None
					# Limpiar outputs
					if hasattr(struct, 'output'): struct.output = None
					if hasattr(struct, 'outputConveyor'): struct.outputConveyor = None

		# Recopilar conexiones de cintas
		struct_connections = {}
		for conv in conveyors:
			start_grid_x = int(conv.start_pos.x) // CELL_SIZE_PX
			start_grid_y = int(conv.start_pos.y) // CELL_SIZE_PX
			end_grid_x = int(conv.end_pos.x) // CELL_SIZE_PX
			end_grid_y = int(conv.end_pos.y) // CELL_SIZE_PX

			start_struct = find_structure_at(start_grid_x, start_grid_y)
			end_struct = find_structure_at(end_grid_x, end_grid_y)

			if start_struct:
				if start_struct not in struct_connections:
					struct_connections[start_struct] = {'inputs': [], 'outputs': []}
				struct_connections[start_struct]['outputs'].append(conv)

			if end_struct:
				if end_struct not in struct_connections:
					struct_connections[end_struct] = {'inputs': [], 'outputs': []}
				struct_connections[end_struct]['inputs'].append(conv)

		# Ahora conectar según el tipo de estructura
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

		# Conectar cintas entre sí cuando coinciden posiciones
		for conv in conveyors:
			for other_conv in conveyors:
				if conv != other_conv:
					if (int(conv.end_pos.x) == int(other_conv.start_pos.x) and
						int(conv.end_pos.y) == int(other_conv.start_pos.y)):
						grid_x = int(conv.end_pos.x) // CELL_SIZE_PX
						grid_y = int(conv.end_pos.y) // CELL_SIZE_PX
						struct = find_structure_at(grid_x, grid_y)
						if struct is None:
							conv.connectOutput(other_conv)

		# If a game_manager was provided, set some convenient references
		if game_manager is not None:
			# find a Mine structure if present
			for row in self.cells:
				for cell in row:
					if not cell.isEmpty() and cell.structure.__class__.__name__ == 'Mine':
						game_manager.mine = cell.structure
						break
				if hasattr(game_manager, 'mine') and game_manager.mine:
					break

			# determine final_conveyor and well
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

