"""Application entry point for Number Tycoon.

This module initializes pygame, attempts to redirect stdout to the game's
log file, initializes background music (when available) and runs the main
menu loop. Selecting "Nueva partida" creates a :class:`gameManager.GameManager`
instance and starts the game loop.

The module is intended to be executed as a script::

    python src/main.py

No behavioral changes are made here; only documentation is added for Sphinx.
"""

import pygame as pg
import sys
from mainMenu import MainMenu
from settings import *
from gameManager import GameManager

# Redirect all stdout to App/game.log early so any prints go to the log file.
try:
    # local import from same folder
    from utils.logger import redirect_stdout_to_game_log
    redirect_stdout_to_game_log()
except Exception:
    # If anything goes wrong with redirection, continue running using normal stdout
    pass

if __name__ == '__main__':
    pg.init()

    # Inicializar mixer y reproducir música de fondo desde el menú principal.
    try:
        import pathlib
        base_dir = pathlib.Path(__file__).resolve().parent
        app_dir = base_dir.parent  # subir de src/ a la raíz App/
        music_path = app_dir / "Assets" / "Music" / "kirbySoundTrack.mp3"

        # Intentar inicializar el mezclador y reportar estados para depuración
        mixer_inited = False
        try:
            pg.mixer.init()
            mixer_inited = True
        except Exception as e:
            print(f"[AUDIO DEBUG] pg.mixer.init() falló: {e}")
            try:
                # comprobar si ya estaba inicializado
                mixer_inited = pg.mixer.get_init()
            except Exception:
                mixer_inited = False


        if music_path.exists() and mixer_inited:
            pg.mixer.music.load(str(music_path))
            print(f"[AUDIO DEBUG] music loaded OK")
            pg.mixer.music.set_volume(0.6)
            pg.mixer.music.play(-1)
        else:
            if not music_path.exists():
                print("[AUDIO DEBUG] music file not found; will not play background music.")
            elif not mixer_inited:
                print("[AUDIO DEBUG] mixer not initialized; cannot play music.")
    except Exception as e:
        print(f"[AUDIO DEBUG] unexpected error initializing music: {e}")

    screen = pg.display.set_mode(RESOLUTION)
    # Establecer el icono de la ventana si existe
    try:
        import pathlib
        base_dir = pathlib.Path(__file__).resolve().parent
        app_dir = base_dir.parent
        icon_path = app_dir / "Assets" / "icon.png"
        if icon_path.exists():
            try:
                icon_surf = pg.image.load(str(icon_path)).convert_alpha()
                pg.display.set_icon(icon_surf)
            except Exception as e:
                print(f"[ICON DEBUG] failed to load/set icon: {e}")
    except Exception:
        pass

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