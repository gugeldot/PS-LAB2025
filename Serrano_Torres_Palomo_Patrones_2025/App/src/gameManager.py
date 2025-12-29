import pygame as pg
import sys
import pathlib
import os
import json
import random
from collections import deque

from settings import *
from mouseControl import MouseControl
from patterns.singleton import Singleton
from ui.hud import HUD, Colors
from core.mine import Mine
from core.well import Well
from core.mineCreator import MineCreator
from core.wellCreator import WellCreator
from core.mergerCreator import MergerCreator
from core.splitterCreator import SplitterCreator
from core.operationCreator import SumCreator, MultiplyCreator
from core.conveyor import Conveyor
from map.map import Map
from patterns.decorator import SpeedUpgrade, EfficiencyUpgrade


class GameManager(Singleton):
    _initialized = False

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        pg.init()
        self.screen = pg.display.set_mode(RESOLUTION)
        pg.display.set_caption("Jueguito")

        # timing
        self.clock = pg.time.Clock()
        self.delta_time = 1
        # camera offset in pixels for panning a large map
        self.camera = pg.Vector2(0, 0)
        self.camera_speed = 400  # pixels per second when moving with WASD

        # save paths (App/saves/map.json)
        base_dir = pathlib.Path(__file__).resolve().parent
        app_dir = base_dir.parent
        self.save_dir = app_dir / "saves"
        self.save_file = self.save_dir / "map.json"

        # UI: Inicializar HUD
        self.hud = None  # Se inicializará después de new_game()

        # Upgrade usage counters (max 10 uses each)
        self.speed_uses_left = 10
        self.eff_uses_left = 10
        self.speed_uses_used = 0
        self.eff_uses_used = 0
        # New Mine purchase counters (max 10 uses)
        self.mine_uses_left = 10
        self.mine_uses_used = 0
        # Hardcoded costs for creating a mine per use (10 entries)
        # These mirror the style of `speed_costs` and `eff_costs` and can be tuned
        self.mine_costs = (10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
        # Cost (in points) to redeem each upgrade
        # These can be tuned or moved to settings.py if desired
        # incremental cost schedule for each of the 10 possible uses
        # define as tuples/lists of length 10 (one cost per use index)
        # Example default costs; adjust as desired
        self.speed_costs = (10, 12, 14, 16, 18, 20, 24, 28, 32, 40)
        self.eff_costs = (16, 18, 20, 22, 24, 28, 32, 36, 40, 50)
        # action buffer to store pending upgrade actions (processed in update())
        # each entry: { 'type': 'speed'|'eff', 'tries': int, 'max_tries': int }
        self.action_buffer = deque()

        # default well positions as individual variables posWell1..posWell10
        # Edit these tuples to reposition each well. They are (grid_x, grid_y).
        self.posWell1 = (8, 2)
        self.posWell2 = (3, 6)    # Retrocede un poco en X, sube en Y
        self.posWell3 = (11, 4)   # Salto a la derecha
        self.posWell4 = (6, 12)   # Vuelve a la izquierda pero sube
        self.posWell5 = (15, 10)  # Salto al centro
        self.posWell6 = (12, 18)  # Sube bastante
        self.posWell7 = (22, 13)  # Se dispara a la derecha
        self.posWell8 = (18, 21)  # Ajuste hacia arriba
        self.posWell9 = (24, 17)  # Casi al borde derecho
        self.posWell10 = (22, 25)
        # convenience tuple to iterate over if needed
        self.well_positions = (self.posWell1, self.posWell2, self.posWell3, self.posWell4, self.posWell5,
                self.posWell6, self.posWell7, self.posWell8, self.posWell9, self.posWell10)

        self.running = True

        # start
        self.new_game()
        
        # Inicializar HUD después de que el juego esté configurado
        self.hud = HUD(self)

        # mark initialized
        self._initialized = True

    def new_game(self):
        """Inicializa los elementos del juego: carga mapa si existe o crea uno por defecto."""
        self.mouse = MouseControl(self)

        # creator mapping for loading
        creators = {
            "Mine": MineCreator(),
            "Well": WellCreator(),
            "MergerModule": MergerCreator(),
            "SplitterModule": SplitterCreator(),
            "SumModule": SumCreator(),
            "MultiplyModule": MultiplyCreator(),
        }

        # ensure save dir exists (create lazily)
        os.makedirs(self.save_dir, exist_ok=True)

        if self.save_file.exists():
            print(f"Found saved map at {self.save_file}, loading...")
            try:
                self.map = Map.load_from_file(str(self.save_file), creators=creators, gameManager=self)
                # try to read persisted upgrades and apply them
                try:
                    with open(self.save_file, 'r', encoding='utf-8') as fh:
                        saved = json.load(fh)
                        # restore saved score (puntuación) if present
                        try:
                            self.points = int(saved.get('score', getattr(self, 'points', 0)))
                        except Exception:
                            # fallback to 0 if parsing fails
                            self.points = int(getattr(self, 'points', 0) or 0)

                        upgrades = saved.get('upgrades', {})
                    speed_used = int(upgrades.get('speed_uses_used', 0))
                    eff_used = int(upgrades.get('eff_uses_used', 0))
                    mine_used = int(upgrades.get('mine_uses_used', 0))
                    # set counters
                    self.speed_uses_used = speed_used
                    self.eff_uses_used = eff_used
                    # restore mine purchase counters (do not change game state beyond counters)
                    try:
                        self.mine_uses_used = mine_used
                        self.mine_uses_left = max(0, 10 - self.mine_uses_used)
                    except Exception:
                        pass
                    self.speed_uses_left = max(0, 10 - self.speed_uses_used)
                    self.eff_uses_left = max(0, 10 - self.eff_uses_used)
                    # apply effects without consuming uses
                    if speed_used > 0:
                        try:
                            # apply speed multiplier corresponding to total uses
                            multiplier = 0.9 ** self.speed_uses_used
                            for conv in getattr(self, 'conveyors', []):
                                base_conv = conv
                                while hasattr(base_conv, 'target'):
                                    base_conv = base_conv.target
                                if not hasattr(base_conv, '_base_travel_time'):
                                    base_conv._base_travel_time = getattr(base_conv, 'travel_time', 2000)
                                base_conv.travel_time = max(50, int(base_conv._base_travel_time * multiplier))
                            # also reduce mine production interval using same multiplier
                            try:
                                if not hasattr(self, '_base_production_interval'):
                                    self._base_production_interval = 2000
                                self.production_interval = max(100, int(self._base_production_interval * multiplier))
                            except Exception:
                                pass
                        except Exception:
                            pass
                    if eff_used > 0:
                        try:
                            # increment mine base numbers by eff_used
                            for row in self.map.cells:
                                for cell in row:
                                    if cell and not cell.isEmpty():
                                        s = cell.structure
                                        base_s = s
                                        try:
                                            while hasattr(base_s, 'target'):
                                                base_s = base_s.target
                                        except Exception:
                                            pass
                                        # if it's a Mine increase its number, if it's a Well increase consumingNumber
                                        if hasattr(base_s, 'number'):
                                            if not hasattr(base_s, '_base_number'):
                                                try:
                                                    base_s._base_number = int(base_s.number)
                                                except Exception:
                                                    base_s._base_number = getattr(base_s, 'number', 1)
                                            # add cumulative increments
                                            base_s._base_number = int(base_s._base_number) + eff_used
                                            base_s._effective_number = max(1, int(base_s._base_number))
                                        if hasattr(base_s, 'consumingNumber'):
                                            if not hasattr(base_s, '_base_consumingNumber'):
                                                try:
                                                    base_s._base_consumingNumber = int(base_s.consumingNumber)
                                                except Exception:
                                                    base_s._base_consumingNumber = getattr(base_s, 'consumingNumber', 1)
                                            base_s._base_consumingNumber = int(base_s._base_consumingNumber) + eff_used
                                            base_val = max(1, int(base_s._base_consumingNumber))
                                            base_s.consumingNumber = base_val
                                            # also propagate to the outer structure (wrapper) so runtime references update
                                            try:
                                                if s is not base_s and hasattr(s, 'consumingNumber'):
                                                    s.consumingNumber = base_val
                                            except Exception:
                                                pass
                        except Exception:
                            pass
                except Exception:
                    pass
                print("Map loaded successfully.")
            except Exception as e:
                print("Failed to load map, creating a new default map:", e)
                self.map = Map(DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT)
        else:
            print(f"No saved map found at {self.save_file}, creating default map.")
            self.map = Map(DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT)

            # Test: Two Mines (1) -> SumModule -> Well (2)
            mine1 = MineCreator().createStructure((2, 1), 1, self)
            self.map.placeStructure(2, 1, mine1)

            mine2 = MineCreator().createStructure((2, 3), 1, self)
            self.map.placeStructure(2, 3, mine2)

            sum_mod = SumCreator().createStructure((5, 2), self)
            self.map.placeStructure(5, 2, sum_mod)

            # place a row of 10 wells with consuming numbers 1..10 using the configured positions
            self.wells = []
            for idx, num in enumerate(range(1, 11)):
                try:
                    pos = self.well_positions[idx]
                except Exception:
                    # fallback: place to the right of merger if not enough positions
                    pos = (8 + idx, 2)
                w = WellCreator().createStructure(pos, num, self)
                self.map.placeStructure(int(pos[0]), int(pos[1]), w)
                self.wells.append(w)

            # Create conveyors
            conv1 = Conveyor(mine1.position, sum_mod.position, self)
            conv2 = Conveyor(mine2.position, sum_mod.position, self)
            conv3 = Conveyor(sum_mod.position, well.position, self)
            
            self.conveyors = [conv1, conv2, conv3]
            
            # Use new setter syntax for connections
            mine1.output = conv1
            mine2.output = conv2
            sum_mod.input1 = conv1
            sum_mod.input2 = conv2
            sum_mod.output = conv3
            conv3.output = well
            
            # connect merger to the first well (consumingNumber=1) for the sample conveyor path
            target_well = self.wells[0] if getattr(self, 'wells', None) and len(self.wells) > 0 else None
            if target_well:
                conv4 = Conveyor(merger.position, target_well.position, self)
            else:
                conv4 = Conveyor(merger.position, pg.Vector2(0, 0), self)

            # Explicitly connect conveyors/structures for deterministic flow
            try:
                # connect intermediate conveyor segments
                conv2.connectOutput(conv2_merge)
                conv3.connectOutput(conv3_merge)
                # connect logical structure ports
                splitter.connectInput(conv1)
                splitter.connectOutput1(conv2)
                splitter.connectOutput2(conv3)
                merger.connectInput1(conv2_merge)
                merger.connectInput2(conv3_merge)
                merger.connectOutput(conv4)
            except Exception:
                pass

            self.conveyors = [conv1, conv2, conv2_merge, conv3, conv3_merge, conv4]
            
            self.mine = mine
            # convenience reference to the first well (consumingNumber==1)
            self.well = target_well if target_well else None
            self.final_conveyor = conv4
            self.production_timer = 0
            self.consumption_timer = 0

        # ensure conveyors list exists
        if not hasattr(self, 'conveyors'):
            self.conveyors = []
        
        if not hasattr(self, 'points'):
            self.points = 0

        # ALWAYS establish/re-establish connections between structures and conveyors
        # This handles both new games and loaded games automatically
        print(f"Establishing connections for {len(self.conveyors)} conveyors...")
        self._reconnect_structures()

        # ALWAYS rebuild structures list to include conveyors
        self.structures = []
        # add conveyors first
        for conv in self.conveyors:
            self.structures.append(conv)
        # then map structures
        for row in self.map.cells:
            for cell in row:
                if not cell.isEmpty():
                    self.structures.append(cell.structure)

        if not hasattr(self, 'production_timer'):
            self.production_timer = 0
        if not hasattr(self, 'consumption_timer'):
            self.consumption_timer = 0

    def _reconnect_structures(self):
        """Re-establish connections between structures and conveyors after loading from save."""
        # Find structures by their grid position
        def find_structure_at(grid_x, grid_y):
            if 0 <= grid_y < len(self.map.cells) and 0 <= grid_x < len(self.map.cells[grid_y]):
                cell = self.map.cells[grid_y][grid_x]
                if not cell.isEmpty():
                    return cell.structure
            return None

        # Connect conveyors to structures based on their start/end positions
        for conv in self.conveyors:
            start_grid_x = int(conv.start_pos.x) // CELL_SIZE_PX
            start_grid_y = int(conv.start_pos.y) // CELL_SIZE_PX
            end_grid_x = int(conv.end_pos.x) // CELL_SIZE_PX
            end_grid_y = int(conv.end_pos.y) // CELL_SIZE_PX

            start_struct = find_structure_at(start_grid_x, start_grid_y)
            end_struct = find_structure_at(end_grid_x, end_grid_y)

            # Connect source structure to conveyor
            if start_struct:
                if hasattr(start_struct, 'connectOutput'):
                    start_struct.connectOutput(conv)
                elif hasattr(start_struct, 'connectOutput1'):
                    # For splitters, use Y position to determine which output
                    # If conveyor goes upward (end_y < start_y), use output1
                    # If conveyor goes downward (end_y > start_y), use output2
                    if conv.end_pos.y < start_struct.position.y:
                        start_struct.connectOutput1(conv)
                        print(f"[Reconnect] Connected splitter output1 (upper path)")
                    else:
                        start_struct.connectOutput2(conv)
                        print(f"[Reconnect] Connected splitter output2 (lower path)")

            # Connect conveyor to destination structure
            if end_struct:
                if hasattr(end_struct, 'connectInput'):
                    end_struct.connectInput(conv)
                elif hasattr(end_struct, 'connectInput1'):
                    # For mergers, use Y position to determine which input
                    # If conveyor comes from above (start_y < end_y), use input1
                    # If conveyor comes from below (start_y > end_y), use input2
                    if conv.start_pos.y < end_struct.position.y:
                        end_struct.connectInput1(conv)
                        print(f"[Reconnect] Connected merger input1 (from above)")
                    else:
                        end_struct.connectInput2(conv)
                        print(f"[Reconnect] Connected merger input2 (from below)")

        # Connect conveyors to each other (chain)
        for i, conv in enumerate(self.conveyors):
            # Check if this conveyor's end connects to another conveyor's start
            for other_conv in self.conveyors:
                if conv != other_conv:
                    if (int(conv.end_pos.x) == int(other_conv.start_pos.x) and
                        int(conv.end_pos.y) == int(other_conv.start_pos.y)):
                        
                        # Only connect if there is NO structure at this junction
                        # If there is a structure, the structure handles the transfer
                        grid_x = int(conv.end_pos.x) // CELL_SIZE_PX
                        grid_y = int(conv.end_pos.y) // CELL_SIZE_PX
                        struct = find_structure_at(grid_x, grid_y)
                        
                        if struct is None:
                            conv.connectOutput(other_conv)
                            print(f"[Reconnect] Connected conveyor {i} to conveyor")
                        else:
                            print(f"[Reconnect] Skipping direct conveyor connection at {grid_x},{grid_y} due to structure {struct.__class__.__name__}")

        # Re-establish reference to first and last conveyors
        if len(self.conveyors) > 0:
            # Find mine (first encountered) for reference
            for row in self.map.cells:
                for cell in row:
                    if not cell.isEmpty() and cell.structure.__class__.__name__ == 'Mine':
                        self.mine = cell.structure
                        break
                if hasattr(self, 'mine') and self.mine:
                    break

            # Determine which conveyor connects directly into a Well and treat that as final_conveyor
            self.final_conveyor = None
            self.well = None
            for conv in self.conveyors:
                end_grid_x = int(conv.end_pos.x) // CELL_SIZE_PX
                end_grid_y = int(conv.end_pos.y) // CELL_SIZE_PX
                # find structure at conveyor end
                if 0 <= end_grid_y < len(self.map.cells) and 0 <= end_grid_x < len(self.map.cells[end_grid_y]):
                    cell = self.map.cells[end_grid_y][end_grid_x]
                    if not cell.isEmpty() and cell.structure.__class__.__name__ == 'Well':
                        self.final_conveyor = conv
                        self.well = cell.structure
                        print(f"[Reconnect] Final conveyor set to one that ends at Well at {end_grid_x},{end_grid_y}")
                        break

    def save_map(self):
        """Save map to App/saves/map.json"""
        try:
            base = self.map.to_dict()
            # Ensure we persist base/original numeric values for structures when available.
            # If upgrades have modified in-memory attributes (e.g. consumingNumber or number),
            # prefer to save the original base values so re-loading + applying saved
            # upgrades does not double-apply them.
            try:
                grid = base.get('grid', [])
                eff_used = int(getattr(self, 'eff_uses_used', 0))
                for y, row in enumerate(grid):
                    for x, entry in enumerate(row):
                        if not entry:
                            continue
                        try:
                            cell = self.map.getCell(x, y)
                            if cell and not cell.isEmpty():
                                s = cell.structure
                                # For mines: if _base_number exists it currently includes applied
                                # efficiency upgrades; recover original by subtracting eff_used.
                                if 'number' in entry:
                                    if hasattr(s, '_base_number'):
                                        try:
                                            original = int(getattr(s, '_base_number')) - eff_used
                                            entry['number'] = max(1, original)
                                        except Exception:
                                            entry['number'] = int(entry.get('number', 1))
                                # For wells: same logic for consumingNumber
                                if 'consumingNumber' in entry:
                                    if hasattr(s, '_base_consumingNumber'):
                                        try:
                                            original = int(getattr(s, '_base_consumingNumber')) - eff_used
                                            entry['consumingNumber'] = max(1, original)
                                        except Exception:
                                            entry['consumingNumber'] = int(entry.get('consumingNumber', 1))
                        except Exception:
                            pass
            except Exception:
                pass
            # include conveyors as grid-based connections
            convs = []
            for conv in getattr(self, 'conveyors', []):
                # try to infer grid coords for start and end
                sx = sy = ex = ey = None
                # try to match to cell structures first
                found = False
                for y, row in enumerate(self.map.cells):
                    for x, cell in enumerate(row):
                        if not cell.isEmpty() and hasattr(cell.structure, 'position'):
                            pos = cell.structure.position
                            # compare pixel positions (Vector2 or tuple)
                            try:
                                px, py = float(pos.x), float(pos.y)
                            except Exception:
                                px, py = float(pos[0]), float(pos[1])
                            if int(px) == int(conv.start_pos.x) and int(py) == int(conv.start_pos.y):
                                sx, sy = x, y
                                found = True
                                break
                    if found:
                        break
                if sx is None:
                    sx = int(conv.start_pos.x) // CELL_SIZE_PX
                    sy = int(conv.start_pos.y) // CELL_SIZE_PX

                found = False
                for y, row in enumerate(self.map.cells):
                    for x, cell in enumerate(row):
                        if not cell.isEmpty() and hasattr(cell.structure, 'position'):
                            pos = cell.structure.position
                            try:
                                px, py = float(pos.x), float(pos.y)
                            except Exception:
                                px, py = float(pos[0]), float(pos[1])
                            if int(px) == int(conv.end_pos.x) and int(py) == int(conv.end_pos.y):
                                ex, ey = x, y
                                found = True
                                break
                    if found:
                        break
                if ex is None:
                    ex = int(conv.end_pos.x) // CELL_SIZE_PX
                    ey = int(conv.end_pos.y) // CELL_SIZE_PX

                # Prefer to persist the base travel time if available so reload
                # doesn't re-apply speed multipliers.
                travel = getattr(conv, 'travel_time', None)
                if hasattr(conv, '_base_travel_time'):
                    try:
                        travel = int(getattr(conv, '_base_travel_time'))
                    except Exception:
                        travel = getattr(conv, 'travel_time', None)
                entry = {"start": [sx, sy], "end": [ex, ey], "travel_time": travel}
                convs.append(entry)

            base['conveyors'] = convs
            # include applied upgrades so they persist
            base['upgrades'] = {
                'speed_uses_used': getattr(self, 'speed_uses_used', 0),
                'eff_uses_used': getattr(self, 'eff_uses_used', 0),
                'mine_uses_used': getattr(self, 'mine_uses_used', 0)
            }
            # persist current score with the map
            try:
                base['score'] = int(getattr(self, 'points', 0))
            except Exception:
                base['score'] = getattr(self, 'points', 0)
            # write combined file
            os.makedirs(self.save_dir, exist_ok=True)
            with open(self.save_file, 'w', encoding='utf-8') as fh:
                json.dump(base, fh, indent=2)
            print(f"Map (with conveyors) saved to {self.save_file}")
        except Exception as e:
            print("Failed to save map:", e)

    def save_and_exit(self):
        self.save_map()
        print("Exiting game after save.")
        pg.quit()
        sys.exit()

    def update(self):
        # update inputs
        self.mouse.update()
        
        # Actualizar HUD (popups, temporizadores, etc)
        if self.hud:
            self.hud.update(self.delta_time)
        
        # process any pending upgrade actions from the action_buffer
        try:
            self.process_action_buffer()
        except Exception:
            pass

        # camera movement (smooth) using keyboard
        try:
            keys = pg.key.get_pressed()
            if keys[pg.K_w] or keys[pg.K_UP]:
                self.camera.y = max(0, self.camera.y - self.camera_speed * (self.delta_time / 1000.0))
            if keys[pg.K_s] or keys[pg.K_DOWN]:
                # limit to map pixel height - screen height
                max_y = max(0, self.map.height * CELL_SIZE_PX - HEIGHT)
                self.camera.y = min(max_y, self.camera.y + self.camera_speed * (self.delta_time / 1000.0))
            if keys[pg.K_a] or keys[pg.K_LEFT]:
                self.camera.x = max(0, self.camera.x - self.camera_speed * (self.delta_time / 1000.0))
            if keys[pg.K_d] or keys[pg.K_RIGHT]:
                max_x = max(0, self.map.width * CELL_SIZE_PX - WIDTH)
                self.camera.x = min(max_x, self.camera.x + self.camera_speed * (self.delta_time / 1000.0))
        except Exception:
            pass

        # update map structures
        self.map.update()

        # update conveyors (they are not map-placed structures)
        for conv in getattr(self, 'conveyors', []):
            try:
                conv.update()
            except Exception:
                pass

        # production driven by a configurable interval so speed upgrades can affect it
        # ensure we have a base production interval that can be modified by upgrades
        if not hasattr(self, '_base_production_interval'):
            self._base_production_interval = 2000
        if not hasattr(self, 'production_interval'):
            self.production_interval = int(self._base_production_interval)

        self.production_timer += self.delta_time
        prod_int = int(getattr(self, 'production_interval', getattr(self, '_base_production_interval', 2000)))
        if self.production_timer > prod_int:
            if hasattr(self, 'mine') and self.mine and self.conveyors:
                self.mine.produce(self.conveyors[0])
            self.production_timer = 0

        # Consume immediately when an item has arrived at the end of the final conveyor.
        # Previously this was driven by a 2000ms timer which introduced an extra delay
        # between arrival and scoring. Check the front item's position so wells act
        # as soon as the conveyor reports readiness.
        try:
            if hasattr(self, 'well') and self.well and hasattr(self, 'final_conveyor') and self.final_conveyor is not None:
                q = getattr(self.final_conveyor, 'queue', None)
                if q and len(q) > 0 and q[0].get('position', 0) >= 1.0:
                    # consume will pop the ready item and award points immediately
                    try:
                        self.well.consume(self.final_conveyor)
                    except Exception:
                        pass
        except Exception:
            pass

        # tick (advance clock and compute delta_time)
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def draw(self):
        # Fondo con color pastel suave
        self.screen.fill(Colors.BG_DARK)
        
        # camera (viewport) and mouse grid coords in world space
        cam = getattr(self, 'camera', pg.Vector2(0, 0))
        # convert mouse screen position to world coordinates by adding camera offset
        world_mx = int(self.mouse.position.x + cam.x)
        world_my = int(self.mouse.position.y + cam.y)
        gx = world_mx // CELL_SIZE_PX
        gy = world_my // CELL_SIZE_PX

        # draw grid and structures
        grid_color = Colors.GRID_LINE
        hover_fill = Colors.GRID_HOVER
    # draw world grid and map-placed structures applying camera offset
        for y in range(self.map.height):
            for x in range(self.map.width):
                rect_x = x * CELL_SIZE_PX - cam.x
                rect_y = y * CELL_SIZE_PX - cam.y
                rect = pg.Rect(rect_x, rect_y, CELL_SIZE_PX, CELL_SIZE_PX)
                # highlight hovered cell (we compute gx,gy in screen coords earlier)
                if x == gx and y == gy and 0 <= x < self.map.width and 0 <= y < self.map.height:
                    pg.draw.rect(self.screen, hover_fill, rect)
                pg.draw.rect(self.screen, grid_color, rect, 1)

        # Dibujar conveyors PRIMERO (capa inferior)
        for structure in self.structures:
            if hasattr(structure, 'grid_position'):
                continue
            try:
                structure.draw()
            except Exception:
                pass

        # Dibujar estructuras del mapa DESPUÉS (capa superior)
        for y in range(self.map.height):
            for x in range(self.map.width):
                cell = self.map.getCell(x, y)
                if cell and not cell.isEmpty():
                    try:
                        # map-placed structure draw methods were updated to account for camera
                        cell.structure.draw()
                    except Exception:
                        pass

        # Dibujar HUD (botones, puntos, popup)
        mouse_pt = (int(self.mouse.position.x), int(self.mouse.position.y))
        if self.hud:
            self.hud.draw(self.screen, mouse_pt)

        # draw mouse
        self.mouse.draw()
        # present the rendered frame
        pg.display.flip()
#region checkevents
    def checkEvents(self):
        for event in pg.event.get():
            # pass to mouse control only for clicks not over UI buttons (prevents UI clicks selecting map cells)
            # MouseControl uses MOUSEBUTTONDOWN events to inspect map cells; we call it only for events
            # that are not over the UI button rects so clicking a button won't also select a cell underneath.
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                over_ui = False
                try:
                    if self.hud and self.hud.is_over_button(pos):
                        over_ui = True
                except Exception:
                    over_ui = False

                if not over_ui:
                    self.mouse.checkClickEvent(event)

            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.running = False
                self.save_and_exit()

            # Use MOUSEBUTTONUP for reliable button clicks (handle release)
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                # check if Save & Exit clicked
                if self.hud and self.hud.save_button.collidepoint(event.pos):
                    self.save_and_exit()

                if self.hud and self.hud.shop_button.collidepoint(event.pos):
                    if self.hud.shop_mode == "SHOP":
                        self.hud.shop_mode = None
                    else:
                        self.hud.shop_mode = "SHOP"
                    self.hud._setup_buttons()
                if self.hud and self.hud.build_button.collidepoint(event.pos):
                    if self.hud.shop_mode == "BUILD":
                        self.hud.shop_mode = None
                    else:
                        self.hud.shop_mode = "BUILD"
                    self.hud._setup_buttons()
                #si la tienda esta abierta
                elif self.hud and self.hud.shop_mode == "BUILD":
                    if self.hud and self.hud.sum_module_button.collidepoint(event.pos):
                        pass
                    elif self.hud and self.hud.mul_module_button.collidepoint(event.pos):
                        pass
                    elif self.hud and self.hud.div_module_button.collidepoint(event.pos):
                        pass


                elif self.hud and self.hud.shop_mode == "SHOP":
                    
                    # enqueue upgrade actions (global)
                    if self.hud and self.hud.speed_button.collidepoint(event.pos):
                        # avoid enqueueing more than remaining capacity (max 10 uses total)
                        queued = sum(1 for a in self.action_buffer if a.get('type') == 'speed')
                        if queued + self.speed_uses_used >= 10:
                            print("No speed upgrades available to queue")
                        elif queued >= 1:
                            # already have a pending speed action; ignore extra clicks
                            print("Ya hay una Mejora Velocidad pendiente")
                        elif getattr(self, 'points', 0) < (self.speed_costs[self.speed_uses_used] if 0 <= self.speed_uses_used < len(self.speed_costs) else float('inf')):
                            print("No tienes puntos suficientes para Mejora Velocidad")
                        else:
                            # append action (will be processed in update())
                            self.action_buffer.append({'type': 'speed', 'tries': 0, 'max_tries': 30})
                            print(f"Queued Speed upgrade action (queue size={len(self.action_buffer)})")

                    elif self.hud and self.hud.efficiency_button.collidepoint(event.pos):
                        queued = sum(1 for a in self.action_buffer if a.get('type') == 'eff')
                        if queued + self.eff_uses_used >= 10:
                            print("No efficiency upgrades available to queue")
                        elif queued >= 1:
                            print("Ya hay una Mejora Eficiencia pendiente")
                        elif getattr(self, 'points', 0) < (self.eff_costs[self.eff_uses_used] if 0 <= self.eff_uses_used < len(self.eff_costs) else float('inf')):
                            print("No tienes puntos suficientes para Mejora Eficiencia")
                        
                        else:
                            self.action_buffer.append({'type': 'eff', 'tries': 0, 'max_tries': 30})
                            print(f"Queued Efficiency upgrade action (queue size={len(self.action_buffer)})")

                    elif self.hud and self.hud.new_mine_button.collidepoint(event.pos):
                        # enqueue a 'mine' purchase action (similar to speed/eff)
                        queued = sum(1 for a in self.action_buffer if a.get('type') == 'mine')
                        if queued + self.mine_uses_used >= 10:
                            print("No hay compras de Mina disponibles para poner en cola")
                        elif queued >= 1:
                            print("Ya hay una compra de Mina pendiente")
                        else:
                            # determine next cost
                            next_cost = None
                            try:
                                if 0 <= self.mine_uses_used < len(self.mine_costs):
                                    next_cost = int(self.mine_costs[self.mine_uses_used])
                            except Exception:
                                next_cost = None

                            if next_cost is None or getattr(self, 'points', 0) < (next_cost or 0):
                                print("No tienes puntos suficientes para comprar una Mina")
                            else:
                                self.action_buffer.append({'type': 'mine', 'tries': 0, 'max_tries': 30})
                                print(f"Queued Mine purchase action (queue size={len(self.action_buffer)})")
                    elif self.hud and self.hud.shop_button.collidepoint(event.pos):
                        print("Has pulsado el botón nuevo")
                        self.hud.show_popup("¡Botón activado!") 

    def run(self):
        while self.running:
            self.checkEvents()
            self.update()
            self.draw()

    def create_new_mine(self) -> bool:
        """Locate a random empty cell and create/place a Mine that produces 1.

        Returns True when a mine was successfully placed, False otherwise.
        """
        # simple guard
        if not hasattr(self, 'map') or self.map is None:
            print("Mapa no inicializado")
            return False

        width = int(getattr(self.map, 'width', 0))
        height = int(getattr(self.map, 'height', 0))
        if width <= 0 or height <= 0:
            print("Mapa con dimensiones inválidas")
            return False

        max_tries = width * height * 2
        tries = 0
        while tries < max_tries:
            x = random.randrange(0, width)
            y = random.randrange(0, height)
            cell = self.map.getCell(x, y)
            if cell and cell.isEmpty():
                try:
                    mine = MineCreator().createStructure((x, y), 1, self)
                    ok = self.map.placeStructure(x, y, mine)
                    if ok:
                        # add to structures list so it gets drawn/updated
                        try:
                            if not hasattr(self, 'structures'):
                                self.structures = []
                            self.structures.append(mine)
                        except Exception:
                            pass
                        # if no primary mine exists, set reference
                        if not hasattr(self, 'mine') or self.mine is None:
                            self.mine = mine
                        # set a transient popup message for the UI (2 seconds)
                        try:
                            self._popup_message = f"Mina creada en ({x},{y})"
                            self._popup_timer = 2000
                        except Exception:
                            pass
                        print(f"Nueva mina creada en {x},{y}")
                        return True
                except Exception as e:
                    print("Fallo al crear mina:", e)
            tries += 1

        return False

    def _apply_mine_action(self) -> bool:
        """Attempt to purchase and create a new mine in a random empty cell.

        Returns True on success, False to retry later (e.g., no empty cells or insufficient points).
        """
        # determine next cost
        try:
            next_cost = int(self.mine_costs[self.mine_uses_used]) if 0 <= self.mine_uses_used < len(self.mine_costs) else None
        except Exception:
            next_cost = None

        if next_cost is None or getattr(self, 'points', 0) < (next_cost or 0):
            print("[Action] Not enough points to purchase Mine; will retry")
            return False

        # attempt to create a new mine; create_new_mine will set a popup message on success
        created = False
        try:
            created = self.create_new_mine()
        except Exception:
            created = False

        if not created:
            # no empty cell or creation failed; retry a few times
            print("[Action] Failed to place Mine; will retry")
            return False

        # commit the purchase: deduct points and decrement available uses
        try:
            self.mine_uses_used += 1
            self.mine_uses_left = max(0, 10 - self.mine_uses_used)
            if next_cost is not None:
                try:
                    self.points = max(0, int(self.points) - int(next_cost))
                except Exception:
                    try:
                        self.points -= next_cost
                    except Exception:
                        pass
            # ensure there's a popup if create_new_mine didn't set one
            if self.hud:
                self.hud.show_popup(f"Mina creada ({self.mine_uses_left} restantes)")
            print(f"[Action] Mine purchase applied (uses left={self.mine_uses_left}) | -{next_cost} pts (total={self.points})")
            return True
        except Exception:
            return True

    # ---- Action buffer processing ----
    def process_action_buffer(self, max_per_frame: int = 5):
        """Process up to `max_per_frame` queued upgrade actions.

        Actions are retried up to `max_tries`. If an action is successfully
        applied we decrement the remaining uses and remove it from the queue.
        If an action repeatedly fails it will be dropped after max_tries.
        """
        to_process = min(max_per_frame, len(self.action_buffer))
        applied_this_frame = set()  # types applied successfully this frame
        for _ in range(to_process):
            action = self.action_buffer.popleft()
            ok = False
            if action.get('type') == 'speed':
                try:
                    ok = self._apply_speed_action()
                except Exception:
                    ok = False
            elif action.get('type') == 'eff':
                try:
                    ok = self._apply_eff_action()
                except Exception:
                    ok = False
            elif action.get('type') == 'mine':
                try:
                    ok = self._apply_mine_action()
                except Exception:
                    ok = False

            if ok:
                # applied successfully; log handled in apply function
                applied_this_frame.add(action.get('type'))
                # avoid applying more than one successful upgrade of any type per frame
                # (prevents many queued retries from consuming all uses at once)
                break

            # failed to apply: retry later unless too many tries
            action['tries'] = action.get('tries', 0) + 1
            if action['tries'] < action.get('max_tries', 30):
                self.action_buffer.append(action)
            else:
                print(f"Dropping action {action.get('type')} after {action['tries']} failed tries")

    def _apply_speed_action(self) -> bool:
        """Attempt to apply a single global speed upgrade.

        Returns True on success, False if conditions not met (will retry).
        """
        convs = list(getattr(self, 'conveyors', []))
        if not convs:
            return False

        # determine current cost for this next use
        try:
            next_cost = int(self.speed_costs[self.speed_uses_used]) if 0 <= self.speed_uses_used < len(self.speed_costs) else None
        except Exception:
            next_cost = None

        # ensure enough points at application time
        if next_cost is None or getattr(self, 'points', 0) < (next_cost or 0):
            # not enough points now; retry later
            print("[Action] Not enough points to apply Speed upgrade; will retry")
            return False

        # compute multiplier as if this use is applied
        prospective_uses = self.speed_uses_used + 1
        multiplier = 0.9 ** prospective_uses

        applied = 0
        for conv in convs:
            try:
                base_conv = conv
                while hasattr(base_conv, 'target'):
                    base_conv = base_conv.target
                if not hasattr(base_conv, '_base_travel_time'):
                    base_conv._base_travel_time = getattr(base_conv, 'travel_time', 2000)
                base_conv.travel_time = max(50, int(base_conv._base_travel_time * multiplier))
                applied += 1
            except Exception:
                pass

        if applied > 0:
            # also update global production interval for mines so speed upgrades
            # affect production frequency (use same multiplier as conveyors)
            try:
                if not hasattr(self, '_base_production_interval'):
                    self._base_production_interval = 2000
                # compute new production interval using the same multiplier
                self.production_interval = max(100, int(self._base_production_interval * multiplier))
            except Exception:
                pass
            # commit the use and subtract points
            self.speed_uses_used += 1
            self.speed_uses_left = max(0, 10 - self.speed_uses_used)
            if next_cost is not None:
                try:
                    self.points = max(0, int(self.points) - int(next_cost))
                except Exception:
                    try:
                        self.points -= next_cost
                    except Exception:
                        pass
            # show popup for user feedback
            try:
                self._popup_message = f"Mejora Velocidad aplicada ({self.speed_uses_left})"
                self._popup_timer = 2000
            except Exception:
                pass
            print(f"[Action] Speed upgrade applied (uses left={self.speed_uses_left}) -> updated {applied} conveyors | -{next_cost} pts (total={self.points})")
            return True

        return False

    def _apply_eff_action(self) -> bool:
        """Attempt to apply a single global efficiency upgrade.

        Returns True on success, False if no applicable mines found (will retry).
        """
        mines_found = False
        # scan map for mines (structures with attribute 'number')
        for y, row in enumerate(self.map.cells):
            for x, cell in enumerate(row):
                if cell and not cell.isEmpty():
                    s = cell.structure
                    base_s = s
                    try:
                        while hasattr(base_s, 'target'):
                            base_s = base_s.target
                    except Exception:
                        pass
                    if hasattr(base_s, 'number'):
                        mines_found = True
                        break
            if mines_found:
                break

        if not mines_found:
            return False

        # determine next cost for efficiency
        try:
            next_cost = int(self.eff_costs[self.eff_uses_used]) if 0 <= self.eff_uses_used < len(self.eff_costs) else None
        except Exception:
            next_cost = None

        # ensure enough points at application time
        if next_cost is None or getattr(self, 'points', 0) < (next_cost or 0):
            print("[Action] Not enough points to apply Efficiency upgrade; will retry")
            return False

        applied = 0
        for y, row in enumerate(self.map.cells):
            for x, cell in enumerate(row):
                if cell and not cell.isEmpty():
                    s = cell.structure
                    base_s = s
                    try:
                        while hasattr(base_s, 'target'):
                            base_s = base_s.target
                    except Exception:
                        pass
                    # If it's a Mine, adjust its base/effective production number
                    if hasattr(base_s, 'number'):
                        if not hasattr(base_s, '_base_number'):
                            try:
                                base_s._base_number = int(base_s.number)
                            except Exception:
                                base_s._base_number = getattr(base_s, 'number', 1)
                        try:
                            base_s._base_number = int(base_s._base_number) + 1
                            base_s._effective_number = max(1, int(base_s._base_number))
                            applied += 1
                        except Exception:
                            pass
                    # If it's a Well, adjust its consumingNumber so it consumes more per tick
                    if hasattr(base_s, 'consumingNumber'):
                        if not hasattr(base_s, '_base_consumingNumber'):
                            try:
                                base_s._base_consumingNumber = int(base_s.consumingNumber)
                            except Exception:
                                base_s._base_consumingNumber = getattr(base_s, 'consumingNumber', 1)
                        try:
                            base_s._base_consumingNumber = int(base_s._base_consumingNumber) + 1
                            # update the runtime consumingNumber so consume() uses the new value
                            base_val = max(1, int(base_s._base_consumingNumber))
                            base_s.consumingNumber = base_val
                            # propagate to outer wrapper/object so draw/consume calls using the
                            # top-level reference see the updated value immediately
                            try:
                                if s is not base_s and hasattr(s, 'consumingNumber'):
                                    s.consumingNumber = base_val
                            except Exception:
                                pass
                            applied += 1
                        except Exception:
                            pass

        if applied > 0:
            # update in-flight items on conveyors so they reflect the new efficiency
            # The efficiency upgrade increments mine output by +1 per use in this implementation,
            # so add the same delta to all queued numeric items so wells see the increased values
            try:
                delta = 1
                for conv in getattr(self, 'conveyors', []):
                    try:
                        for item in conv.queue:
                            try:
                                item['value'] = int(item.get('value', 0)) + delta
                            except Exception:
                                pass
                    except Exception:
                        pass
            except Exception:
                pass
            # commit the use and subtract points
            self.eff_uses_used += 1
            self.eff_uses_left = max(0, 10 - self.eff_uses_used)
            if next_cost is not None:
                try:
                    self.points = max(0, int(self.points) - int(next_cost))
                except Exception:
                    try:
                        self.points -= next_cost
                    except Exception:
                        pass
            # popup for efficiency
            try:
                self._popup_message = f"Mejora Eficiencia aplicada ({self.eff_uses_left})"
                self._popup_timer = 2000
            except Exception:
                pass
            print(f"[Action] Efficiency upgrade applied (uses left={self.eff_uses_left}) -> updated {applied} mines | -{next_cost} pts (total={self.points})")
            return True

        return False