"""Main menu implementation for Number Tycoon.

This module provides the :class:`MainMenu` class which renders the game's
main menu, handles input and launches or resumes games by creating a
:class:`gameManager.GameManager` instance. The implementation uses pygame
surfaces and draws a custom cursor to match the in-game UI.

Only documentation strings are added to support Sphinx; behavior is
unchanged.
"""

import os
import pathlib
import pygame as pg
from settings import *
from gameManager import GameManager
from utils.app_paths import APP_ROOT as BASE_DIR


class MainMenu:
    """Main menu controller.

    Public methods:
    - draw(): render the menu to the screen
    - update(): tick the menu clock
    - handle_events(): process pygame events
    - start_game(new=False): start a GameManager instance
    """
    def __init__(self, screen):
        self.screen = screen
        self.clock = pg.time.Clock()
        self.running = True
        self.selected_option = 0  # para manejar opciones si hay varias
        self.options = ["Nueva partida", "Continuar", "Salir"]
        self.font = pg.font.Font(None, 50)
        self.optionRects = []
        # estado de existencia de guardado
        self.save_exists = self.has_save()
       
        

        # el cursos del lol
        pg.mouse.set_visible(False)

        # Resolve base dir (works inside PyInstaller bundles)
        CURSOR_IMG_PATH = BASE_DIR / "Assets" / "Sprites" / "cursor.png"

        self.cursor_img = pg.image.load(str(CURSOR_IMG_PATH)).convert_alpha()
        self.cursor_img = pg.transform.scale(
            self.cursor_img, (MOUSE_WIDTH, MOUSE_HEIGHT)
        )
        self.cursor_offset = pg.Vector2(-25, -20)

        # Intentar cargar icono de warning desde Assets/Sprites (prefiere PNG, luego SVG)
        self.warning_icon = None
        try:
            warn_png = BASE_DIR / "Assets" / "Sprites" / "warning.png"
            warn_svg = BASE_DIR / "Assets" / "Sprites" / "warning.svg"
            if warn_png.exists():
                self.warning_icon = pg.image.load(str(warn_png)).convert_alpha()
            elif warn_svg.exists():
                # intentar cargar el SVG (depende de SDL_image); puede fallar, por eso el try
                try:
                    self.warning_icon = pg.image.load(str(warn_svg)).convert_alpha()
                except Exception:
                    self.warning_icon = None
        except Exception:
            self.warning_icon = None

        # Si no se pudo cargar, dibujar un icono simple en runtime
        if self.warning_icon is None:
            s = pg.Surface((28, 28), pg.SRCALPHA)
            # triángulo amarillo
            pg.draw.polygon(s, (255, 204, 77), [(14,2),(26,24),(2,24)])
            # exclamación
            pg.draw.rect(s, (35,31,32), pg.Rect(13,7,4,10))
            pg.draw.circle(s, (35,31,32), (15,22), 2)
            self.warning_icon = s
        else:
            # escalar a tamaño adecuado
            try:
                self.warning_icon = pg.transform.smoothscale(self.warning_icon, (28, 28))
            except Exception:
                pass

        # Cargar imagen de fondo del menú si existe
        self.background = None
        try:
            fondo_path = BASE_DIR / "Assets" / "Sprites" / "fondoIA.png"
            if fondo_path.exists():
                img = pg.image.load(str(fondo_path)).convert()
                # escalar a la resolución de ventana
                try:
                    img = pg.transform.smoothscale(img, RESOLUTION)
                except Exception:
                    img = pg.transform.scale(img, RESOLUTION)
                self.background = img
        except Exception:
            self.background = None

    def draw(self):
        # dibujar fondo (imagen si está disponible, sino color)
        if self.background is not None:
            try:
                self.screen.blit(self.background, (0, 0))
            except Exception:
                self.screen.fill((30, 30, 30))
        else:
            self.screen.fill((30, 30, 30))
        self.option_rects = []

        mouse_pos = pg.mouse.get_pos()

        # Separación vertical entre botones (ajustable)
        spacing = 90  # píxeles entre centros de botones
        total_h = spacing * (len(self.options) - 1)
        start_y = HEIGHT // 2 - total_h // 2

        for i, option in enumerate(self.options):
            # Si es la opción "Continuar" y no hay guardado, pintarla deshabilitada
            disabled = (i == 1 and not self.save_exists)
            # color base del texto
            base_color = (120, 120, 120) if disabled else (200, 200, 200)
            text = self.font.render(option, True, base_color)
            y = start_y + i * spacing
            rect = text.get_rect(center=(WIDTH // 2, y))

            # Botón: expandir rect para crear fondo/borde (padding)
            # aumentar ancho ~60px y alto ~28px para tener espacio alrededor del texto
            btn_rect = rect.inflate(60, 28)

            # Hover con el mouse (usamos btn_rect para el hover/hitbox)
            hover = btn_rect.collidepoint(mouse_pos)
            if hover and not disabled:
                self.selected_option = i
                # texto resaltado
                text = self.font.render(option, True, (255, 215, 0))

            # Colores de fondo y borde según estado
            if disabled:
                bg_color = (45, 45, 45)
                border_color = (90, 90, 90)
            elif hover or i == self.selected_option:
                bg_color = (70, 60, 20)
                border_color = (255, 215, 0)
            else:
                bg_color = (30, 30, 30)
                border_color = (85, 85, 85)

            # dibujar fondo redondeado y borde
            try:
                pg.draw.rect(self.screen, bg_color, btn_rect, border_radius=8)
                pg.draw.rect(self.screen, border_color, btn_rect, 2, border_radius=8)
            except Exception:
                # fallback sin border_radius si no soportado
                pg.draw.rect(self.screen, bg_color, btn_rect)
                pg.draw.rect(self.screen, border_color, btn_rect, 2)

            # registrar hitbox para clicks (usamos btn_rect para facilidad)
            self.option_rects.append(btn_rect)
            # Si la opción "Nueva partida" y hay guardado, dibujar icono de warning a la izquierda
            if i == 0 and self.save_exists:
                # colocar icono a la izquierda del botón (con pequeño margen)
                icon_rect = pg.Rect(btn_rect.left - 44, btn_rect.centery - 14, 28, 28)
                try:
                    self.screen.blit(self.warning_icon, icon_rect.topleft)
                except Exception:
                    # fallback: dibujar un círculo
                    pg.draw.circle(self.screen, (253, 203, 110), icon_rect.center, 12)
                    ex_surf = self.font.render("!", True, (44, 62, 80))
                    ex_surf = pg.transform.smoothscale(ex_surf, (14, 18))
                    self.screen.blit(ex_surf, ex_surf.get_rect(center=icon_rect.center))

            # blitear texto centrado en el botón
            self.screen.blit(text, text.get_rect(center=btn_rect.center))
        # Dibuja el cursor personalizado
        mouse_pos = pg.mouse.get_pos() + self.cursor_offset
        self.screen.blit(self.cursor_img, mouse_pos)
        pg.display.flip()

    def update(self):
        self.clock.tick(FPS)
        # Mantener el título fijo en lugar de mostrar los FPS
        try:
            pg.display.set_caption("Number Tycoon")
        except Exception:
            pass

    def handle_events(self):
        for event in pg.event.get():

            # Cerrar ventana
            if event.type == pg.QUIT:
                self.running = False

            # ---------- TECLADO ----------
            elif event.type == pg.KEYDOWN:

                if event.key == pg.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)

                elif event.key == pg.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)

                elif event.key == pg.K_RETURN:
                    self.executeOption()

            # ---------- RATÓN ----------
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_option = i
                        # Si es "Continuar" pero no hay guardado, ignorar
                        if i == 1 and not self.save_exists:
                            break
                        self.executeOption()
                        break
                        
    def executeOption(self):
        if self.selected_option == 0:  # nueva partida
            # Si existe un guardado, pedir confirmación antes de borrarlo
            if self.has_save():
                ok = self.confirm_delete_save()
                if not ok:
                    return
            # borrar (si existe) y lanzar nueva partida
            self.delete_save()
            self.running = False
            print("opcion 0 - nueva partida")
            self.start_game(new=True)
        elif self.selected_option == 1:  # COntinuar
            if self.load_save():
                self.running = False
        elif self.selected_option == 2:  # salir
            self.running = False
    def start_game(self, new=False):
        # Forzar recreación de la instancia singleton del GameManager cuando se
        # solicita una nueva partida, para asegurarnos de limpiar todo el estado
        # en memoria (estructuras, conveyors, timers, HUD, etc.). Si no pedimos
        # nueva partida, usar la instancia existente (continuar).
        if new:
            try:
                # Limpiar referencias al singleton para forzar re-creación
                GameManager._instance = None
                GameManager._initialized = False
                # También resetear singleton del Map para evitar reutilizar el
                # mapa en memoria (Map es un singleton separado que mantiene
                # las celdas/estructuras entre instancias del GameManager).
                try:
                    from map.map import Map
                    Map._instance = None
                    Map._initialized = False
                except Exception:
                    pass
            except Exception:
                pass

        # Crear (o recrear) el GameManager y arrancar el loop del juego
        game = GameManager()
        try:
            game.running = True
        except Exception:
            pass
        game.run()
    def delete_save(self):
        from utils.app_paths import APP_DIR
        save_file = pathlib.Path(APP_DIR) / "saves" / "map.json"
        if save_file.exists():
            try:
                os.remove(save_file)
                print(f"Archivo {save_file} eliminado. Se inicia un nuevo juego.")
            except Exception as e:
                print(f"No se pudo eliminar {save_file}: {e}")

    def load_save(self):
        """Intenta cargar el guardado 'map.json' si existe."""
        from utils.app_paths import APP_DIR
        save_file = pathlib.Path(APP_DIR) / "saves" / "map.json"

        if save_file.exists():
            print(f"Guardado encontrado: {save_file}. Continuando juego...")
            game = GameManager()
            try:
                # si la instancia ya existía, puede venir con running=False; reactivar
                game.running = True
            except Exception:
                pass
            game.run()
            return True
        else:
            print("No hay guardado. Debes iniciar un nuevo juego.")
            return False
    def has_save(self):
        from utils.app_paths import APP_DIR
        save_file = pathlib.Path(APP_DIR) / "saves" / "map.json"
        return save_file.exists()

    def confirm_delete_save(self):
        """Muestra un diálogo modal simple preguntando si borrar la partida anterior.
        Devuelve True si confirma, False si cancela.
        """
        clock = pg.time.Clock()
        confirmed = False
        showing = True

        # guardar visibilidad previa del cursor y mostrar cursor del sistema durante modal
        prev_cursor_vis = pg.mouse.get_visible()
        pg.mouse.set_visible(True)

        # Dibujar el menú una vez y tomar snapshot para evitar redibujar todo cada frame (evita flicker)
        try:
            # usamos draw() para generar fondo con custom cursor y tomamos copia
            self.draw()
            bg = self.screen.copy()
        except Exception:
            bg = None

        # helper para ajustar texto (wrapping)
        def wrap_text(text, font, max_width):
            words = text.split(' ')
            lines = []
            cur = ''
            for w in words:
                test = (cur + ' ' + w).strip()
                if font.size(test)[0] <= max_width:
                    cur = test
                else:
                    if cur:
                        lines.append(cur)
                    cur = w
            if cur:
                lines.append(cur)
            return lines

        # Mensaje y fuentes
        msg = "¿Estás seguro de borrar partida anterior?"
        font_msg = pg.font.Font(None, 26)
        # calcular tamaño de caja basado en texto
        max_w = WIDTH - 120
        lines = wrap_text(msg, font_msg, 420)
        text_width = max((font_msg.size(l)[0] for l in lines), default=0)
        padding = 28
        w = max(360, text_width + padding * 2)
        h = 120 + (len(lines)-1) * 22
        x = (WIDTH - w) // 2
        y = (HEIGHT - h) // 2

        yes_rect = pg.Rect(x + 40, y + h - 48, 140, 36)
        no_rect = pg.Rect(x + w - 180, y + h - 48, 140, 36)

        # Modal loop
        while showing:
            mouse_pos = pg.mouse.get_pos()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    showing = False
                    confirmed = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_y or event.key == pg.K_RETURN:
                        confirmed = True
                        showing = False
                    elif event.key == pg.K_n or event.key == pg.K_ESCAPE:
                        confirmed = False
                        showing = False
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if yes_rect.collidepoint((mx, my)):
                        confirmed = True
                        showing = False
                    elif no_rect.collidepoint((mx, my)):
                        confirmed = False
                        showing = False

            # dibujar snapshot del fondo si está disponible para evitar flicker
            if bg is not None:
                try:
                    self.screen.blit(bg, (0, 0))
                except Exception:
                    self.screen.fill((20, 20, 20))
            else:
                self.screen.fill((20, 20, 20))

            # overlay semitransparente
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            # cuadro del diálogo
            box = pg.Rect(x, y, w, h)
            pg.draw.rect(self.screen, (240, 240, 240), box, border_radius=10)
            pg.draw.rect(self.screen, (100, 100, 100), box, 2, border_radius=10)

            # renderizar líneas de texto
            ty = y + 18
            for line in lines:
                surf = font_msg.render(line, True, (20, 20, 20))
                self.screen.blit(surf, (x + padding, ty))
                ty += surf.get_height() + 4

            # botones con hover
            hover_yes = yes_rect.collidepoint(mouse_pos)
            hover_no = no_rect.collidepoint(mouse_pos)
            yes_color = (220, 70, 70) if hover_yes else (200, 80, 80)
            no_color = (200, 200, 200) if hover_no else (160, 160, 160)
            pg.draw.rect(self.screen, yes_color, yes_rect, border_radius=8)
            pg.draw.rect(self.screen, no_color, no_rect, border_radius=8)

            yes_s = pg.font.Font(None, 24).render("Sí - Borrar", True, (255, 255, 255) if hover_yes else (255, 255, 255))
            no_s = pg.font.Font(None, 24).render("No - Cancelar", True, (0, 0, 0) if not hover_no else (0,0,0))
            self.screen.blit(yes_s, yes_s.get_rect(center=yes_rect.center))
            self.screen.blit(no_s, no_s.get_rect(center=no_rect.center))

            # dibujar custom cursor (para que no desaparezca) encima del modal
            try:
                cursor_pos = pg.mouse.get_pos() + self.cursor_offset
                self.screen.blit(self.cursor_img, cursor_pos)
            except Exception:
                pass

            pg.display.flip()
            clock.tick(FPS)

        # restaurar visibilidad del cursor al valor previo
        try:
            pg.mouse.set_visible(prev_cursor_vis)
        except Exception:
            pass

        # actualizar flag de existencia de guardado
        self.save_exists = self.has_save()
        return confirmed
        

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            
