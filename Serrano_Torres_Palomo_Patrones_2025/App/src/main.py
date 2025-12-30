import pygame as pg
import sys
from mainMenu import MainMenu
from settings import *
from gameManager import GameManager

if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode(RESOLUTION)
    pg.display.set_caption("Number Tycoon")
    
    # Loop principal: mostrar el menú, y si se inicia un juego y vuelve, mostrar el menú de nuevo
    while True:
        mainMenu = MainMenu(screen)
        mainMenu.run()
        # Si el usuario eligió Salir (opción índice 2), salir del bucle
        try:
            if mainMenu.selected_option == 2:
                break
        except Exception:
            break

    pg.quit()