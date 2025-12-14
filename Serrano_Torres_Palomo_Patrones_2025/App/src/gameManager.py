import pygame as pg
import sys
import pathlib
import os
import json

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

        # save paths (App/saves/map.json)
        base_dir = pathlib.Path(__file__).resolve().parent
        app_dir = base_dir.parent
        self.save_dir = app_dir / "saves"
        self.save_file = self.save_dir / "map.json"

        # UI: Save & Exit button
        self.save_button_rect = pg.Rect(WIDTH - 170, 10, 160, 40)

        self.running = True

        # start
        self.new_game()

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
        }

        # ensure save dir exists (create lazily)
        os.makedirs(self.save_dir, exist_ok=True)

        if self.save_file.exists():
            print(f"Found saved map at {self.save_file}, loading...")
            try:
                self.map = Map.load_from_file(str(self.save_file), creators=creators, gameManager=self)
                print("Map loaded successfully.")
            except Exception as e:
                print("Failed to load map, creating a new default map:", e)
                self.map = Map(DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT)
        else:
            print(f"No saved map found at {self.save_file}, creating default map.")
            self.map = Map(DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT)

            # place some sample structures (grid coords)
            mine = MineCreator().createStructure((1, 1), 1, self)
            self.map.placeStructure(1, 1, mine)

            well = WellCreator().createStructure((3, 1), 1, self)
            self.map.placeStructure(3, 1, well)

            # create conveyor between mine and well
            c = Conveyor(mine.position, well.position, self)
            # store conveyors as a list
            self.conveyors = [c]
            self.structures = [c]

            m1 = MergerCreator().createStructure((2, 3), self)
            self.map.placeStructure(2, 3, m1)
            s1 = SplitterCreator().createStructure((5, 4), self)
            self.map.placeStructure(5, 4, s1)

        # ensure conveyors list exists; if not created above (map load), try to
        # create conveyors from saved data in the save file (if any)
        if not hasattr(self, 'conveyors'):
            self.conveyors = []

            # attempt to read conveyors section from saved json
            try:
                with open(self.save_file, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                conveyors_data = data.get('conveyors', [])
                for cdata in conveyors_data:
                    sx, sy = cdata.get('start', (0, 0))
                    ex, ey = cdata.get('end', (0, 0))
                    # derive pixel positions: prefer cell structure positions
                    start_cell = self.map.getCell(sx, sy)
                    end_cell = self.map.getCell(ex, ey)
                    if start_cell and not start_cell.isEmpty():
                        start_pos = start_cell.structure.position
                    else:
                        start_pos = (sx * CELL_SIZE_PX + CELL_SIZE_PX // 2, sy * CELL_SIZE_PX + CELL_SIZE_PX // 2)
                    if end_cell and not end_cell.isEmpty():
                        end_pos = end_cell.structure.position
                    else:
                        end_pos = (ex * CELL_SIZE_PX + CELL_SIZE_PX // 2, ey * CELL_SIZE_PX + CELL_SIZE_PX // 2)

                    conv = Conveyor(start_pos, end_pos, self)
                    # restore travel_time if present
                    if 'travel_time' in cdata:
                        conv.travel_time = cdata['travel_time']
                    self.conveyors.append(conv)
            except Exception:
                # no conveyors info or failed to parse; leave empty
                self.conveyors = []

        # collect structures: conveyors (non-map) + map structures
        self.structures = []
        # add conveyors first
        for conv in self.conveyors:
            self.structures.append(conv)
        # then map structures
        for row in self.map.cells:
            for cell in row:
                if not cell.isEmpty():
                    self.structures.append(cell.structure)

        self.production_timer = 0
        self.consumption_timer = 0

    def save_map(self):
        """Save map to App/saves/map.json"""
        try:
            base = self.map.to_dict()
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

                entry = {"start": [sx, sy], "end": [ex, ey], "travel_time": getattr(conv, 'travel_time', None)}
                convs.append(entry)

            base['conveyors'] = convs
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
            # try find a mine in map and push into first conveyor if available
            try:
                mine_cell = self.map.getCell(1, 1)
                if mine_cell and not mine_cell.isEmpty() and self.conveyors:
                    mine_cell.structure.produce(self.conveyors[0])
            except Exception:
                pass
            self.production_timer = 0

        self.consumption_timer += self.delta_time
        if self.consumption_timer > 2000:
            try:
                well_cell = self.map.getCell(3, 1)
                if well_cell and not well_cell.isEmpty() and self.conveyors:
                    well_cell.structure.consume(self.conveyors[0])
            except Exception:
                pass
            self.consumption_timer = 0

        # flip and tick
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

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

        # draw mouse
        self.mouse.draw()

    def checkEvents(self):
        for event in pg.event.get():
            # pass to mouse control (keeps existing debug prints)
            self.mouse.checkClickEvent(event)

            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.running = False
                self.save_and_exit()

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # check if Save & Exit clicked
                if self.save_button_rect.collidepoint(event.pos):
                    self.save_and_exit()

    def run(self):
        while self.running:
            self.checkEvents()
            self.update()
            self.draw()