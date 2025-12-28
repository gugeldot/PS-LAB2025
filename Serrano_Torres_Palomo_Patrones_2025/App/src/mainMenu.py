import pygame as pg
from settings import *
from gameManager import GameManager

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pg.time.Clock()
        self.running = True
        self.selected_option = 0  # para manejar opciones si hay varias
        self.options = ["Jugar", "Salir"]
        self.font = pg.font.Font(None, 50)
        
    def draw(self):
        self.screen.fill((30, 30, 30))
        for i, option in enumerate(self.options):
            color = (255, 215, 0) if i == self.selected_option else (200, 200, 200)
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 60))
            self.screen.blit(text, rect)
        pg.display.flip()
    def update(self):
        self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')
    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pg.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pg.K_RETURN:
                    if self.selected_option == 0:  # Jugar
                        self.running = False
                        self.start_game()
                    elif self.selected_option == 1:  # Salir
                        self.running = False

    def start_game(self):
        # Aquí toma el control el GameManager y el main menu muere
        game = GameManager()
        game.run()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            
