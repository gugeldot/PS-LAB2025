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

            # Test: Mine -> Conveyor1 -> Splitter -> [Conveyor2, Conveyor3] -> Merger -> Conveyor4 -> Well
            mine = MineCreator().createStructure((2, 2), 1, self)
            self.map.placeStructure(2, 2, mine)

            splitter = SplitterCreator().createStructure((4, 2), self)
            self.map.placeStructure(4, 2, splitter)

            merger = MergerCreator().createStructure((6, 2), self)
            self.map.placeStructure(6, 2, merger)

            well = WellCreator().createStructure((8, 2), 1, self)
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
            
            # Connect conveyors to each other
            conv2.connectOutput(conv2_merge)
            conv3.connectOutput(conv3_merge)
            
            # Connect splitter
            splitter.connectInput(conv1)
            splitter.connectOutput1(conv2)
            splitter.connectOutput2(conv3)
            
            # Connect merger
            merger.connectInput1(conv2_merge)
            merger.connectInput2(conv3_merge)
            merger.connectOutput(conv4)

            self.conveyors = [conv1, conv2, conv2_merge, conv3, conv3_merge, conv4]
            self.structures = [conv1, conv2, conv2_merge, conv3, conv3_merge, conv4]
            
            self.mine = mine
            self.well = well
            self.final_conveyor = conv4
            self.production_timer = 0
            self.consumption_timer = 0
            self.points = 0

        # ensure conveyors list exists; if loaded from save, might need to initialize
        if not hasattr(self, 'conveyors'):
            self.conveyors = []
        
        if not hasattr(self, 'points'):
            self.points = 0

        # collect structures only if not already set (when loading from save)
        if not hasattr(self, 'structures'):
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
            if hasattr(self, 'mine') and self.mine and self.conveyors:
                self.mine.produce(self.conveyors[0])
            self.production_timer = 0

        self.consumption_timer += self.delta_time
        if self.consumption_timer > 2000:
            if hasattr(self, 'well') and self.well and hasattr(self, 'final_conveyor'):
                self.well.consume(self.final_conveyor)
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
        
        # display points below button
        font = pg.font.Font(None, 36)
        points_text = font.render(f"Points: {self.points}", True, (255, 215, 0))
        self.screen.blit(points_text, (self.save_button_rect.left, self.save_button_rect.bottom + 10))

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