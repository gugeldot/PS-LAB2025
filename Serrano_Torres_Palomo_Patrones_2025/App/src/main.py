import pygame as pg
import sys
from mainMenu import MainMenu
from settings import *
from gameManager import GameManager

if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode(RESOLUTION)
    pg.display.set_caption("Le jogo")
    
    mainMenu = MainMenu(screen)
    mainMenu.run()
    pg.quit()