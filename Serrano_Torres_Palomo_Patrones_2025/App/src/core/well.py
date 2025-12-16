import pygame as pg
import pathlib
from .structure import *
from utils import is_prime
from settings import CELL_SIZE_PX


class Well(Structure):
    def __init__(self, position, consumingNumber, gameManager):
        '''
        Inicializa el pozo usando coordenadas de grilla (x,y). La posición
        pixel se calcula a partir de CELL_SIZE_PX y el centro de la celda.
        '''
        gx, gy = int(position[0]), int(position[1])
        px = gx * CELL_SIZE_PX + CELL_SIZE_PX // 2
        py = gy * CELL_SIZE_PX + CELL_SIZE_PX // 2
        self.grid_position = (gx, gy)
        self.position = pg.Vector2((px, py))
        self.consumingNumber = consumingNumber
        self.gameManager = gameManager
        self.radius = 15
        self.color = (0, 150, 0)
        
        BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
        COIN_PATH = BASE_DIR / "Assets" / "Sprites" / "coin.svg"
        try:
            self.coin_img = pg.image.load(str(COIN_PATH)).convert_alpha()
            self.coin_img = pg.transform.scale(self.coin_img, (20, 20))
        except:
            self.coin_img = None

    def update(self):
        '''
        '''
        pass
    
    def consume(self, conveyor):
        number = conveyor.pop()
        if number is not None and number == self.consumingNumber:
            points = number
            if is_prime(number):
                points *= 2
            self.gameManager.points += points
            bonus_text = " (PRIME x2!)" if is_prime(number) else ""
            print(f"Well consumed {number}! +{points} points{bonus_text} | Total: {self.gameManager.points}")
            bonus_text = " (PRIME x2!)" if is_prime(number) else ""
            print(f"Well consumed {number}! +{points} points{bonus_text} | Total: {self.gameManager.points}")

    def draw(self):
        pg.draw.circle(self.gameManager.screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
        
        font = pg.font.Font(None, 24)
        text = font.render(str(self.consumingNumber), True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.position.x, self.position.y))
        self.gameManager.screen.blit(text, text_rect)
        
        points_value = self.consumingNumber
        if is_prime(self.consumingNumber):
            points_value *= 2
        
        if self.coin_img:
            coin_x = self.position.x - 25
            coin_y = self.position.y - 35
            self.gameManager.screen.blit(self.coin_img, (coin_x, coin_y))
        
        points_font = pg.font.Font(None, 20)
        points_text = points_font.render(f"+{points_value}", True, (255, 215, 0))
        points_rect = points_text.get_rect(center=(self.position.x + 5, self.position.y - 35))
        self.gameManager.screen.blit(points_text, points_rect)