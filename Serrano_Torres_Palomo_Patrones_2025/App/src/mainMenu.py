import os
import pathlib
import pygame as pg
from settings import *
from gameManager import GameManager

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pg.time.Clock()
        self.running = True
        self.selected_option = 0  # para manejar opciones si hay varias
        self.options = ["Nueva partida", "Continuar", "Salir"]
        self.font = pg.font.Font(None, 50)
        self.optionRects = []
       
        

        # el cursos del lol
        pg.mouse.set_visible(False)

        BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
        CURSOR_IMG_PATH = BASE_DIR / "Assets" / "Sprites" / "cursor.png"

        self.cursor_img = pg.image.load(CURSOR_IMG_PATH).convert_alpha()
        self.cursor_img = pg.transform.scale(
            self.cursor_img, (MOUSE_WIDTH, MOUSE_HEIGHT)
        )
        self.cursor_offset = pg.Vector2(-25, -20) 

    def draw(self):
        self.screen.fill((30, 30, 30))
        self.option_rects = []

        mouse_pos = pg.mouse.get_pos()

        for i, option in enumerate(self.options):
            text = self.font.render(option, True, (200, 200, 200))
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 60))

            # Hover con el mouse
            if rect.collidepoint(mouse_pos):
                self.selected_option = i
                text = self.font.render(option, True, (255, 215, 0))

            self.option_rects.append(rect)
            self.screen.blit(text, rect)
        # Dibuja el cursor personalizado
        mouse_pos = pg.mouse.get_pos() + self.cursor_offset
        self.screen.blit(self.cursor_img, mouse_pos)
        pg.display.flip()

    def update(self):
        self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

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
                    self.execute_option()

            # ---------- RATÓN ----------
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_option = i
                        self.executeOption()
                        break
                        
    def executeOption(self):
        if self.selected_option == 0:  # nueva partida
            self.delete_save()
            self.running = False
            print("opcion 0")
            self.start_game()
        elif self.selected_option == 1:  # COntinuar
            if self.load_save():
                self.running = False
        elif self.selected_option == 2:  # salir
            self.running = False
    def start_game(self):
        # Aquí toma el control el GameManager y el main menu muere
        game = GameManager()
        game.run()
    def delete_save(self):
        base_dir = pathlib.Path(__file__).resolve().parent.parent  # sube de src/ a app/
        save_file = base_dir / "saves" / "map.json"
        if save_file.exists():
            try:
                os.remove(save_file)
                print(f"Archivo {save_file} eliminado. Se inicia un nuevo juego.")
            except Exception as e:
                print(f"No se pudo eliminar {save_file}: {e}")

    def load_save(self):
        """Intenta cargar el guardado 'map.json' si existe."""
        base_dir = pathlib.Path(__file__).resolve().parent.parent  # sube de src/ a app/
        save_file = base_dir / "saves" / "map.json"

        if save_file.exists():
            print(f"Guardado encontrado: {save_file}. Continuando juego...")
            game = GameManager()
            game.run()
            return True
        else:
            print("No hay guardado. Debes iniciar un nuevo juego.")
            return False
        

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            
