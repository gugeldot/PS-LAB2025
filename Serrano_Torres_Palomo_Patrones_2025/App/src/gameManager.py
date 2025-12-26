import pygame as pg
import sys
import pathlib
import os
import json
from collections import deque

from buildState import BuildState
from core.sumModuleCreator import SumModuleCreator
from normalState import NormalState
from placementController import PlacementController
from settings import *
from mouseControl import MouseControl
from patterns.singleton import Singleton
from core.mine import Mine
from core.well import Well
from core.mineCreator import MineCreator
from core.wellCreator import WellCreator
from core.mergerCreator import MergerCreator
from core.splitterCreator import SplitterCreator
from core.conveyor import Conveyor
from map.map import Map
from patterns.decorator import SpeedUpgrade, EfficiencyUpgrade


class GameManager(Singleton):
    _initialized = False
    # region __init__
    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        pg.init()
        self.screen = pg.display.set_mode(RESOLUTION)
        pg.display.set_caption("Jueguito")

        # timing
        self.clock = pg.time.Clock()
        self.delta_time = 1

        # save paths (App/saves/map.json)
        base_dir = pathlib.Path(__file__).resolve().parent
        app_dir = base_dir.parent
        self.save_dir = app_dir / "saves"
        self.save_file = self.save_dir / "map.json"

        # UI: Save & Exit button
        self.save_button_rect = pg.Rect(WIDTH - 170, 10, 160, 40)
        # UI: Upgrade buttons (stacked under Save)
        self.speed_button_rect = pg.Rect(WIDTH - 170, 60, 160, 40)
        self.eff_button_rect = pg.Rect(WIDTH - 170, 110, 160, 40)

        # Upgrade usage counters (max 10 uses each)
        self.speed_uses_left = 10
        self.eff_uses_left = 10
        self.speed_uses_used = 0
        self.eff_uses_used = 0
        # Cost (in points) to redeem each upgrade
        # These can be tuned or moved to settings.py if desired
        # incremental cost schedule for each of the 10 possible uses
        # define as tuples/lists of length 10 (one cost per use index)
        # Example default costs; adjust as desired
        self.speed_costs = (5, 6, 7, 8, 9, 10, 12, 14, 16, 20)
        self.eff_costs = (8, 9, 10, 11, 12, 14, 16, 18, 20, 25)
        # action buffer to store pending upgrade actions (processed in update())
        # each entry: { 'type': 'speed'|'eff', 'tries': int, 'max_tries': int }

        
        self.action_buffer = deque()

        self.running = True

        # start
        self.new_game()

        # mark initialized
        self._initialized = True
    # region new_game
    def new_game(self):
        """Inicializa los elementos del juego: carga mapa si existe o crea uno por defecto."""
        self.mouse = MouseControl(self)

        #modo normal o construccion
        self.buildMode= False
        
        self.normalState= NormalState(self.mouse)
        self.buildState= BuildState(PlacementController(self,None))
        self.state= self.normalState
        # creator mapping for loading
        creators = {
            "Mine": MineCreator(),
            "Well": WellCreator(),
            "MergerModule": MergerCreator(),
            "SplitterModule": SplitterCreator(),
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
                    # set counters
                    self.speed_uses_used = speed_used
                    self.eff_uses_used = eff_used
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

            # Test: Mine -> Conveyor1 -> Splitter -> [Conveyor2, Conveyor3] -> Merger -> Conveyor4 -> Well
            mine = MineCreator().createStructure((2, 2),  self,1)
            self.map.placeStructure(2, 2, mine)

            splitter = SplitterCreator().createStructure((4, 2), self)
            self.map.placeStructure(4, 2, splitter)

            merger = MergerCreator().createStructure((6, 2), self)
            self.map.placeStructure(6, 2, merger)

            well = WellCreator().createStructure((8, 2),  self,1)
            self.map.placeStructure(8, 2, well)

            # Create conveyors with visual deviation
            conv1 = Conveyor(mine.position, splitter.position, self)
            
            # Upper path: splitter -> waypoint up -> merger
            waypoint_up = pg.Vector2(merger.position.x - 40, merger.position.y - 40)
            conv2 = Conveyor(splitter.position, waypoint_up, self)
            conv2_merge = Conveyor(waypoint_up, merger.position, self)
            
            # Lower path: splitter -> waypoint down -> merger
            waypoint_down = pg.Vector2(merger.position.x - 40, merger.position.y + 40)
            conv3 = Conveyor(splitter.position, waypoint_down, self)
            conv3_merge = Conveyor(waypoint_down, merger.position, self)
            
            conv4 = Conveyor(merger.position, well.position, self)
            
            self.conveyors = [conv1, conv2, conv2_merge, conv3, conv3_merge, conv4]
            
            self.mine = mine
            self.well = well
            self.final_conveyor = conv4
            self.production_timer = 0
            self.consumption_timer = 0
            self.points = 0

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
# region update
    def update(self):
        # update inputs
        self.mouse.update()
        self.state.update()
        # process any pending upgrade actions from the action buffer
        try:
            self.process_action_buffer()
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

        self.production_timer += self.delta_time
        if self.production_timer > 2000:
            if hasattr(self, 'mine') and self.mine and self.conveyors:
                self.mine.produce(self.conveyors[0])
            self.production_timer = 0

        self.consumption_timer += self.delta_time
        if self.consumption_timer > 2000:
            if hasattr(self, 'well') and self.well and hasattr(self, 'final_conveyor'):
                self.well.consume(self.final_conveyor)
            self.consumption_timer = 0

        # tick (advance clock and compute delta_time)
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')
# region draw
    def draw(self):
        self.screen.fill('black')
        
        # mouse grid coords
        mx, my = int(self.mouse.position.x), int(self.mouse.position.y)
        gx = mx // CELL_SIZE_PX
        gy = my // CELL_SIZE_PX

        # draw grid and structures
        grid_color = (80, 80, 80)
        hover_fill = (200, 200, 200)
        for y in range(self.map.height):
            for x in range(self.map.width):
                rect = pg.Rect(x * CELL_SIZE_PX, y * CELL_SIZE_PX, CELL_SIZE_PX, CELL_SIZE_PX)
                # highlight hovered cell
                if x == gx and y == gy and 0 <= x < self.map.width and 0 <= y < self.map.height:
                    pg.draw.rect(self.screen, hover_fill, rect)
                pg.draw.rect(self.screen, grid_color, rect, 1)

                cell = self.map.getCell(x, y)
                if cell and not cell.isEmpty():
                    try:
                        cell.structure.draw()
                    except Exception:
                        pass

        # draw non-map structures (e.g., conveyors)
        for structure in self.structures:
            if hasattr(structure, 'grid_position'):
                continue
            try:
                structure.draw()
            except Exception:
                pass

        # draw Save & Exit button
        mouse_pt = (int(self.mouse.position.x), int(self.mouse.position.y))
        hover = self.save_button_rect.collidepoint(mouse_pt)
        btn_color = (100, 100, 100) if not hover else (150, 150, 150)
        pg.draw.rect(self.screen, btn_color, self.save_button_rect)
        # button text
        font = pg.font.Font(None, 24)
        text = font.render("Save & Exit", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.save_button_rect.center)
        self.screen.blit(text, text_rect)
        
        # display total points as a label in the bottom-left corner
        # draw a dark background box so the text is always legible
        try:
            font = pg.font.Font(None, 36)
            points_text = font.render(f"Puntuación: {self.points}", True, (255, 215, 0))
            padding = 8
            text_rect = points_text.get_rect()
            label_x = 10
            label_y = HEIGHT - text_rect.height - 10
            bg_rect = pg.Rect(label_x - padding, label_y - padding,
                              text_rect.width + padding * 2, text_rect.height + padding * 2)
            # slightly translucent-ish look (solid color; SDL surfaces do not always support alpha here)
            pg.draw.rect(self.screen, (30, 30, 30), bg_rect)
            # thin border
            pg.draw.rect(self.screen, (180, 180, 180), bg_rect, 1)
            self.screen.blit(points_text, (label_x, label_y))
        except Exception:
            # fallback: try a very small font and a plain blit so draw() never crashes
            try:
                font = pg.font.Font(None, 20)
                points_text = font.render(str(getattr(self, 'points', 0)), True, (255, 215, 0))
                self.screen.blit(points_text, (10, HEIGHT - 30))
            except Exception:
                pass

        # draw Upgrade buttons (Mejora Velocidad / Mejora Eficiencia)
        font_small = pg.font.Font(None, 20)

        # Speed button shows price and remaining uses, and is shaded if unaffordable or no uses
        hover_speed = self.speed_button_rect.collidepoint(mouse_pt)
        # determine next cost for speed (based on how many uses already consumed)
        next_speed_cost = None
        try:
            if 0 <= self.speed_uses_used < len(self.speed_costs):
                next_speed_cost = int(self.speed_costs[self.speed_uses_used])
        except Exception:
            next_speed_cost = None

        can_buy_speed = (getattr(self, 'points', 0) >= (next_speed_cost or 0)) and (self.speed_uses_left > 0)
        if not can_buy_speed:
            speed_color = (60, 60, 60)
        else:
            speed_color = (150, 150, 150) if hover_speed else (100, 100, 100)
        pg.draw.rect(self.screen, speed_color, self.speed_button_rect)
        speed_label_cost = f"{next_speed_cost}pts" if next_speed_cost is not None else "N/A"
        text_speed = font_small.render(f"Mejora Velocidad ({speed_label_cost}) [{self.speed_uses_left}]", True, (255, 255, 255))
        self.screen.blit(text_speed, text_speed.get_rect(center=self.speed_button_rect.center))

        # Efficiency button shows price and remaining uses, and is shaded if unaffordable or no uses
        hover_eff = self.eff_button_rect.collidepoint(mouse_pt)
        # determine next cost for efficiency
        next_eff_cost = None
        try:
            if 0 <= self.eff_uses_used < len(self.eff_costs):
                next_eff_cost = int(self.eff_costs[self.eff_uses_used])
        except Exception:
            next_eff_cost = None

        can_buy_eff = (getattr(self, 'points', 0) >= (next_eff_cost or 0)) and (self.eff_uses_left > 0)
        if not can_buy_eff:
            eff_color = (60, 60, 60)
        else:
            eff_color = (150, 150, 150) if hover_eff else (100, 100, 100)
        pg.draw.rect(self.screen, eff_color, self.eff_button_rect)
        eff_label_cost = f"{next_eff_cost}pts" if next_eff_cost is not None else "N/A"
        text_eff = font_small.render(f"Mejora Eficiencia ({eff_label_cost}) [{self.eff_uses_left}]", True, (255, 255, 255))
        self.screen.blit(text_eff, text_eff.get_rect(center=self.eff_button_rect.center))

        # esto dibuja la preview del build en caso de que estemos en modo build
        if hasattr(self.state, "draw"):
            self.state.draw()
        self.mouse.draw()
        # present the rendered frame
        pg.display.flip()
# region checkEvents
    def checkEvents(self):
        for event in pg.event.get():
            # pass to mouse control (keeps existing debug prints)

            #el estado aqui sustituye al mouse para manejar los clicks, dependeidneo de si modo construccion o no
            
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.running = False
                self.save_and_exit()

            #gestion de teclas
            if event.type == pg.KEYDOWN:
                    #se activa modo construccion
                    if event.key == pg.K_b:
                            self.toggleBuildMode(True)
                            self.state.setFactory(MineCreator())  
                    if event.key == pg.K_n:
                            self.toggleBuildMode(True)
                            self.state.setFactory(WellCreator())
                    if event.key == pg.K_BACKSPACE:
                            self.toggleBuildMode(False)
                    if event.key == pg.K_v:
                            self.toggleBuildMode(True)
                            self.state.setFactory(SumModuleCreator())        

            # Use MOUSEBUTTONUP for reliable button clicks (handle release)
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                # check if Save & Exit clicked
                if self.save_button_rect.collidepoint(event.pos):
                    self.save_and_exit()
                # enqueue upgrade actions (global)
                elif self.speed_button_rect.collidepoint(event.pos):
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

                elif self.eff_button_rect.collidepoint(event.pos):
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
            self.state.handleClickEvent(event)
# region run
    def run(self):
        while self.running:
            self.checkEvents()
            self.update()
            self.draw()




#region toggleBuildMode

    def toggleBuildMode(self,boolean):
        self.buildMode= boolean
        if boolean:
            self.state= self.buildState
        else:
            self.state= self.normalState

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
                'eff_uses_used': getattr(self, 'eff_uses_used', 0)
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
            print(f"[Action] Efficiency upgrade applied (uses left={self.eff_uses_left}) -> updated {applied} mines | -{next_cost} pts (total={self.points})")
            return True

        return False
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
            # Find mine and well to set first/last conveyor references
            for row in self.map.cells:
                for cell in row:
                    if not cell.isEmpty():
                        if cell.structure.__class__.__name__ == 'Mine':
                            self.mine = cell.structure
                        elif cell.structure.__class__.__name__ == 'Well':
                            self.well = cell.structure

            # Set final conveyor (last one that connects to well)
            if hasattr(self, 'well') and self.well:
                for conv in self.conveyors:
                    end_grid_x = int(conv.end_pos.x) // CELL_SIZE_PX
                    end_grid_y = int(conv.end_pos.y) // CELL_SIZE_PX
                    well_grid_x = int(self.well.position.x) // CELL_SIZE_PX
                    well_grid_y = int(self.well.position.y) // CELL_SIZE_PX
                    if end_grid_x == well_grid_x and end_grid_y == well_grid_y:
                        self.final_conveyor = conv
                        break