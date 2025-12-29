import pygame as pg
import sys
import os
import json
import random
from collections import deque

from settings import *
# Módulos delegados (modularización)
from gm_init import init_pygame, init_paths, init_ui, init_counters, init_well_positions
from gm_update import update as gm_update
from gm_draw import draw as gm_draw
# No necesitamos importar las funciones de upgrades aquí, ya que gm_update las gestiona,
# pero sí necesitamos que gm_update funcione correctamente.

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


class GameManager(Singleton):
    _initialized = False

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        # Inicialización agrupada delegada a helpers en gm_init
        init_pygame(self)
        init_paths(self)
        init_ui(self)
        init_counters(self)
        init_well_positions(self)

        self.running = True

        # Construir mapa y estructuras
        self.new_game()
        
        # Inicializar HUD después de que el juego esté configurado
        self.hud = HUD(self)

        # Marcar como inicializado
        self._initialized = True
#region new_game
    def new_game(self):
        """Inicializa los elementos del juego: carga mapa si existe o crea uno por defecto."""
        self.mouse = MouseControl(self)

        # Mapeo de creadores para la carga
        creators = {
            "Mine": MineCreator(),
            "Well": WellCreator(),
            "MergerModule": MergerCreator(),
            "SplitterModule": SplitterCreator(),
            "SumModule": SumCreator(),
            "MultiplyModule": MultiplyCreator(),
        }

        # Asegurar que existe el directorio de guardado
        os.makedirs(self.save_dir, exist_ok=True)

        if self.save_file.exists():
            print(f"Found saved map at {self.save_file}, loading...")
            try:
                self.map = Map.load_from_file(str(self.save_file), creators=creators, gameManager=self)
                # Intentar leer mejoras persistidas y aplicarlas
                try:
                    with open(self.save_file, 'r', encoding='utf-8') as fh:
                        saved = json.load(fh)
                        # Restaurar puntuación
                        try:
                            self.points = int(saved.get('score', getattr(self, 'points', 0)))
                        except Exception:
                            self.points = int(getattr(self, 'points', 0) or 0)

                        upgrades = saved.get('upgrades', {})
                    speed_used = int(upgrades.get('speed_uses_used', 0))
                    eff_used = int(upgrades.get('eff_uses_used', 0))
                    mine_used = int(upgrades.get('mine_uses_used', 0))
                    
                    # Set counters
                    self.speed_uses_used = speed_used
                    self.eff_uses_used = eff_used
                    # Restaurar contadores de compra de minas
                    try:
                        self.mine_uses_used = mine_used
                        self.mine_uses_left = max(0, 10 - self.mine_uses_used)
                    except Exception:
                        pass
                    self.speed_uses_left = max(0, 10 - self.speed_uses_used)
                    self.eff_uses_left = max(0, 10 - self.eff_uses_used)
                    
                    # Aplicar efectos visuales/lógicos de carga (restauración de estado)
                    if speed_used > 0:
                        try:
                            multiplier = 0.9 ** self.speed_uses_used
                            for conv in getattr(self, 'conveyors', []):
                                base_conv = conv
                                while hasattr(base_conv, 'target'):
                                    base_conv = base_conv.target
                                if not hasattr(base_conv, '_base_travel_time'):
                                    base_conv._base_travel_time = getattr(base_conv, 'travel_time', 2000)
                                base_conv.travel_time = max(50, int(base_conv._base_travel_time * multiplier))
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
                                        if hasattr(base_s, 'number'):
                                            if not hasattr(base_s, '_base_number'):
                                                try:
                                                    base_s._base_number = int(base_s.number)
                                                except Exception:
                                                    base_s._base_number = getattr(base_s, 'number', 1)
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

            # Estructuras por defecto
            mine = MineCreator().createStructure((2, 2), 1, self)
            self.map.placeStructure(2, 2, mine)

            splitter = SplitterCreator().createStructure((4, 2), self)
            self.map.placeStructure(4, 2, splitter)

            merger = MergerCreator().createStructure((6, 2), self)
            self.map.placeStructure(6, 2, merger)

            self.wells = []
            for idx, num in enumerate(range(1, 11)):
                try:
                    pos = self.well_positions[idx]
                except Exception:
                    pos = (8 + idx, 2)
                w = WellCreator().createStructure(pos, num, self)
                self.map.placeStructure(int(pos[0]), int(pos[1]), w)
                self.wells.append(w)

            conv1 = Conveyor(mine.position, splitter.position, self)

            waypoint_up = pg.Vector2(merger.position.x - 40, merger.position.y - 40)
            conv2 = Conveyor(splitter.position, waypoint_up, self)
            conv2_merge = Conveyor(waypoint_up, merger.position, self)

            waypoint_down = pg.Vector2(merger.position.x - 40, merger.position.y + 40)
            conv3 = Conveyor(splitter.position, waypoint_down, self)
            conv3_merge = Conveyor(waypoint_down, merger.position, self)

            target_well = self.wells[0] if getattr(self, 'wells', None) and len(self.wells) > 0 else None
            if target_well:
                conv4 = Conveyor(merger.position, target_well.position, self)
            else:
                conv4 = Conveyor(merger.position, pg.Vector2(0, 0), self)

            try:
                conv2.connectOutput(conv2_merge)
                conv3.connectOutput(conv3_merge)
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
            self.well = target_well if target_well else None
            self.final_conveyor = conv4
            self.production_timer = 0
            self.consumption_timer = 0
            self.points = 0

        if not hasattr(self, 'conveyors'):
            self.conveyors = []
        if not hasattr(self, 'points'):
            self.points = 0

        print(f"Establishing connections for {len(self.conveyors)} conveyors...")
        self._reconnect_structures()

        self.structures = []
        for conv in self.conveyors:
            self.structures.append(conv)
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
        def find_structure_at(grid_x, grid_y):
            if 0 <= grid_y < len(self.map.cells) and 0 <= grid_x < len(self.map.cells[grid_y]):
                cell = self.map.cells[grid_y][grid_x]
                if not cell.isEmpty():
                    return cell.structure
            return None

        for conv in self.conveyors:
            start_grid_x = int(conv.start_pos.x) // CELL_SIZE_PX
            start_grid_y = int(conv.start_pos.y) // CELL_SIZE_PX
            end_grid_x = int(conv.end_pos.x) // CELL_SIZE_PX
            end_grid_y = int(conv.end_pos.y) // CELL_SIZE_PX

            start_struct = find_structure_at(start_grid_x, start_grid_y)
            end_struct = find_structure_at(end_grid_x, end_grid_y)

            if start_struct:
                if hasattr(start_struct, 'connectOutput'):
                    start_struct.connectOutput(conv)
                elif hasattr(start_struct, 'connectOutput1'):
                    if conv.end_pos.y < start_struct.position.y:
                        start_struct.connectOutput1(conv)
                    else:
                        start_struct.connectOutput2(conv)

            if end_struct:
                if hasattr(end_struct, 'connectInput'):
                    end_struct.connectInput(conv)
                elif hasattr(end_struct, 'connectInput1'):
                    if conv.start_pos.y < end_struct.position.y:
                        end_struct.connectInput1(conv)
                    else:
                        end_struct.connectInput2(conv)

        for i, conv in enumerate(self.conveyors):
            for other_conv in self.conveyors:
                if conv != other_conv:
                    if (int(conv.end_pos.x) == int(other_conv.start_pos.x) and
                        int(conv.end_pos.y) == int(other_conv.start_pos.y)):
                        grid_x = int(conv.end_pos.x) // CELL_SIZE_PX
                        grid_y = int(conv.end_pos.y) // CELL_SIZE_PX
                        struct = find_structure_at(grid_x, grid_y)
                        if struct is None:
                            conv.connectOutput(other_conv)

        if len(self.conveyors) > 0:
            for row in self.map.cells:
                for cell in row:
                    if not cell.isEmpty() and cell.structure.__class__.__name__ == 'Mine':
                        self.mine = cell.structure
                        break
                if hasattr(self, 'mine') and self.mine:
                    break

            self.final_conveyor = None
            self.well = None
            for conv in self.conveyors:
                end_grid_x = int(conv.end_pos.x) // CELL_SIZE_PX
                end_grid_y = int(conv.end_pos.y) // CELL_SIZE_PX
                if 0 <= end_grid_y < len(self.map.cells) and 0 <= end_grid_x < len(self.map.cells[end_grid_y]):
                    cell = self.map.cells[end_grid_y][end_grid_x]
                    if not cell.isEmpty() and cell.structure.__class__.__name__ == 'Well':
                        self.final_conveyor = conv
                        self.well = cell.structure
                        break

    def save_map(self):
        """Save map to App/saves/map.json"""
        try:
            base = self.map.to_dict()
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
                                if 'number' in entry:
                                    if hasattr(s, '_base_number'):
                                        try:
                                            original = int(getattr(s, '_base_number')) - eff_used
                                            entry['number'] = max(1, original)
                                        except Exception:
                                            entry['number'] = int(entry.get('number', 1))
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
            
            convs = []
            for conv in getattr(self, 'conveyors', []):
                sx = sy = ex = ey = None
                found = False
                for y, row in enumerate(self.map.cells):
                    for x, cell in enumerate(row):
                        if not cell.isEmpty() and hasattr(cell.structure, 'position'):
                            pos = cell.structure.position
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

                travel = getattr(conv, 'travel_time', None)
                if hasattr(conv, '_base_travel_time'):
                    try:
                        travel = int(getattr(conv, '_base_travel_time'))
                    except Exception:
                        travel = getattr(conv, 'travel_time', None)
                entry = {"start": [sx, sy], "end": [ex, ey], "travel_time": travel}
                convs.append(entry)

            base['conveyors'] = convs
            base['upgrades'] = {
                'speed_uses_used': getattr(self, 'speed_uses_used', 0),
                'eff_uses_used': getattr(self, 'eff_uses_used', 0),
                'mine_uses_used': getattr(self, 'mine_uses_used', 0)
            }
            try:
                base['score'] = int(getattr(self, 'points', 0))
            except Exception:
                base['score'] = getattr(self, 'points', 0)
            
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
#region update
    def update(self):
        """Delegamos el loop de update a gm_update.py"""
        try:
            gm_update(self)
        except Exception:
            pass
#region draw
    def draw(self):
        """Delegamos el loop de draw a gm_draw.py"""
        try:
            gm_draw(self)
        except Exception:
            pass
#region checkEvents
    def checkEvents(self):
        for event in pg.event.get():
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

            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if self.save_button_rect.collidepoint(event.pos):
                    self.save_and_exit()
                elif self.speed_button_rect.collidepoint(event.pos):
                    queued = sum(1 for a in self.action_buffer if a.get('type') == 'speed')
                    if queued + self.speed_uses_used >= 10:
                        print("No speed upgrades available to queue")
                    elif queued >= 1:
                        print("Ya hay una Mejora Velocidad pendiente")
                    elif getattr(self, 'points', 0) < (self.speed_costs[self.speed_uses_used] if 0 <= self.speed_uses_used < len(self.speed_costs) else float('inf')):
                        print("No tienes puntos suficientes para Mejora Velocidad")
                    else:
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

                elif self.new_mine_button_rect.collidepoint(event.pos):
                    queued = sum(1 for a in self.action_buffer if a.get('type') == 'mine')
                    if queued + self.mine_uses_used >= 10:
                        print("No hay compras de Mina disponibles para poner en cola")
                    elif queued >= 1:
                        print("Ya hay una compra de Mina pendiente")
                    else:
                        next_cost = None
                        try:
                            if 0 <= self.mine_uses_used < len(self.mine_costs):
                                next_cost = int(self.mine_costs[self.mine_uses_used])
                        except Exception:
                            next_cost = None

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
        Used by external gm_upgrades logic.
        """
        if not hasattr(self, 'map') or self.map is None:
            return False

        width = int(getattr(self.map, 'width', 0))
        height = int(getattr(self.map, 'height', 0))
        if width <= 0 or height <= 0:
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
                        try:
                            if not hasattr(self, 'structures'):
                                self.structures = []
                            self.structures.append(mine)
                        except Exception:
                            pass
                        if not hasattr(self, 'mine') or self.mine is None:
                            self.mine = mine
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