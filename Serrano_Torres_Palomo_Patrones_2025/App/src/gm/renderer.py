import pygame as pg
from settings import CELL_SIZE_PX, HEIGHT, WIDTH
from ui.hud import Colors


class GMRenderer:
    """Encapsula la lógica de dibujo del GameManager en capas claras.

    Mantiene la API pública original: se puede llamar a GMRenderer(gm).draw()
    desde `gm_draw.draw(gm)` sin cambiar comportamiento observable.
    """
    def __init__(self, gm):
        self.gm = gm
        self.screen = gm.screen
        self.cam = getattr(gm, 'camera', pg.Vector2(0, 0))

    def world_mouse_grid(self):
        screen_mouse = pg.mouse.get_pos()
        world_mx = int(self.gm.mouse.position.x + self.cam.x)
        world_my = int(self.gm.mouse.position.y + self.cam.y)
        gx = world_mx // CELL_SIZE_PX
        gy = world_my // CELL_SIZE_PX
        return screen_mouse, gx, gy

    def draw_grid_background(self):
        grid_color = Colors.GRID_LINE
        for y in range(self.gm.map.height):
            for x in range(self.gm.map.width):
                rect_x = x * CELL_SIZE_PX - self.cam.x
                rect_y = y * CELL_SIZE_PX - self.cam.y
                rect = pg.Rect(rect_x, rect_y, CELL_SIZE_PX, CELL_SIZE_PX)
                pg.draw.rect(self.screen, grid_color, rect, 1)

    def draw_conveyors_first_pass(self):
        # Dibujar conveyors por detrás de estructuras
        try:
            for conveyor in getattr(self.gm, 'conveyors', []):
                conveyor.draw()
        except Exception:
            pass

        # También dibujar estructuras que no están en el grid pero que sean conveyors
        for structure in getattr(self.gm, 'structures', []):
            if hasattr(structure, 'grid_position'):
                continue
            if structure.__class__.__name__ == 'Conveyor':
                try:
                    structure.draw()
                except Exception:
                    pass

    def draw_structures_in_grid_with_hover(self):
        screen_mouse, gx, gy = self.world_mouse_grid()
        hover_fill = Colors.GRID_HOVER

        for y in range(self.gm.map.height):
            for x in range(self.gm.map.width):
                rect_x = x * CELL_SIZE_PX - self.cam.x
                rect_y = y * CELL_SIZE_PX - self.cam.y
                rect = pg.Rect(rect_x, rect_y, CELL_SIZE_PX, CELL_SIZE_PX)

                # Hover effect: no dibujar el hover si el ratón está sobre la UI
                over_ui = False
                try:
                    if hasattr(self.gm, 'hud') and self.gm.hud:
                        over_ui = self.gm.hud.is_over_button(screen_mouse)
                except Exception:
                    over_ui = False

                if not over_ui and x == gx and y == gy and 0 <= x < self.gm.map.width and 0 <= y < self.gm.map.height:
                    pg.draw.rect(self.screen, hover_fill, rect)

                # Structures (minas, pozos, splitters, mergers, etc.)
                cell = self.gm.map.getCell(x, y)
                if cell and not cell.isEmpty():
                    try:
                        cell.structure.draw()
                    except Exception:
                        pass

    def draw_structures_off_grid_third_pass(self):
        for structure in getattr(self.gm, 'structures', []):
            if hasattr(structure, 'grid_position'):
                continue
            if structure.__class__.__name__ != 'Conveyor':
                try:
                    structure.draw()
                except Exception:
                    pass

    def draw_hud_and_cursor(self):
        # Dibujar HUD
        try:
            if hasattr(self.gm, 'hud') and self.gm.hud:
                mouse_pos = pg.mouse.get_pos()
                self.gm.hud.draw(self.screen, mouse_pos)
        except Exception as e:
            print(f"Error drawing HUD: {e}")
            try:
                font = pg.font.Font(None, 36)
                points_text = font.render(f"Puntuación: {getattr(self.gm, 'points', 0)}", True, Colors.TEXT_ACCENT)
                self.screen.blit(points_text, (10, HEIGHT - 40))
            except Exception:
                pass

        # Dibujar cursor y preview de estructura si estamos en modo build
        try:
            if hasattr(self.gm.state, "draw"):
                self.gm.state.draw()
            self.gm.mouse.draw()
        except Exception:
            pass

    def draw(self):
        # Fondo
        self.screen.fill(Colors.BG_DARK)
        self.cam = getattr(self.gm, 'camera', pg.Vector2(0, 0))

        # Capas
        self.draw_grid_background()
        self.draw_conveyors_first_pass()
        self.draw_structures_in_grid_with_hover()
        self.draw_structures_off_grid_third_pass()
        self.draw_hud_and_cursor()

        pg.display.flip()
