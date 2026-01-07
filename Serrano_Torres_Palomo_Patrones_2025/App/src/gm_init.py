import pygame as pg
import pathlib
import os
from collections import deque
from settings import * # Ahora está al nivel del módulo, donde debe estar

def init_pygame(gm):
    """Initialize pygame-related surfaces, clock and camera on the given GameManager instance."""
    pg.init()
    # Nota: la inicialización y reproducción de la música se realiza en `main.py`
    # para que la pista suene desde el menú principal y permanezca hasta el
    # cierre completo de la aplicación.
    gm.screen = pg.display.set_mode(RESOLUTION)
    # Asegurar que el título de la ventana sea el esperado
    try:
        pg.display.set_caption("Number Tycoon")
    except Exception:
        pass
    gm.clock = pg.time.Clock()
    gm.delta_time = 1
    gm.camera = pg.Vector2(0, 0)
    gm.camera_speed = 400

def init_paths(gm):
    """Set save directory and save file attributes on gm."""
    base_dir = pathlib.Path(__file__).resolve().parent
    app_dir = base_dir.parent
    gm.save_dir = app_dir / "saves"
    gm.save_file = gm.save_dir / "map.json"

def init_ui(gm):
    """Create button rects and layout-related UI constants."""
    btn_width = 200
    right_margin = 20
    top_margin = 14
    v_spacing = 56
    gm.save_button_rect = pg.Rect(WIDTH - btn_width - right_margin, top_margin, btn_width, 40)
    gm.speed_button_rect = pg.Rect(WIDTH - btn_width - right_margin, top_margin + v_spacing, btn_width, 40)
    gm.eff_button_rect = pg.Rect(WIDTH - btn_width - right_margin, top_margin + v_spacing * 2, btn_width, 40)
    gm.new_mine_button_rect = pg.Rect(WIDTH - btn_width - right_margin, top_margin + v_spacing * 3, btn_width, 40)

def init_counters(gm):
    """Initialize counters, cost tables and the action buffer."""
    gm.speed_uses_left = 10
    gm.eff_uses_left = 10
    gm.speed_uses_used = 0
    gm.eff_uses_used = 0
    # No limit on buying new mines: set uses_left to None to indicate unlimited
    gm.mine_uses_left = None
    gm.mine_uses_used = 0

    #gm.mine_costs = (10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
    gm.mine_costs = (1,2,3,4,5,6,7,8,9,10)
    gm.speed_costs = (10, 12, 24, 48, 96, 192, 384, 768, 1500, 3000)
    gm.eff_costs = (70, 100, 500, 800, 1000, 1600, 3200, 6400, 12000, 15000)

    gm.well_objectives = (30, 50, 100, 200, 500, 800, 1200, 1600, 2000, 5000)

    gm.build_costs = {
        'sum': 15,
        'mul': 45,
        'div': 35, #Not implemented
        'splitter': 10,
        'merger': 10,
        'conveyor': 2,
    }

    
    gm.action_buffer = deque()
    # Optional explicit ordering of GIFs to show on new game. Provide file
    # names (strings) relative to Assets/gifs in the desired order. If left
    # empty, HUD will alphabetically enumerate files found in the folder.
    # Example:
    # gm.gifs_order = ("intro.gif", "tip1.gif", "tip2.gif")
    # If empty, HUD will enumerate files in Assets/gifs alphabetically.
    # I populate a sensible default order based on Assets/gifs contents.
    # Each entry is (filename, title) to display in the GIF modal header.
    gm.gifs_order = (
        ("tutorial1.gif", "Básico"),
        ("tutorial2.gif", "Básico 2"),
        ("tutorialSuma.gif", "Módulo de Suma"),
        ("tutorialMulti.gif", "Módulo de Multiplicación"),
        ("tutorialDivider.gif", "Splitter"),
        ("tutorialMerger.gif", "Merger"),
        ("tutorialVelocidad.gif", "Mejora de Velocidad"),
        ("tutorialEficiencia.gif", "Mejora de Eficiencia"),
        ("tutorialControlesObjetivos.gif", "Controles y Objetivos"),
    )

def init_well_positions(gm):
    """Define default well grid coordinates and the iterable tuple."""
    gm.posWell1 = (8, 2)
    gm.posWell2 = (3, 6)
    gm.posWell3 = (11, 4)
    gm.posWell4 = (6, 12)
    gm.posWell5 = (15, 10)
    gm.posWell6 = (12, 18)
    gm.posWell7 = (22, 13)
    gm.posWell8 = (18, 21)
    gm.posWell9 = (24, 17)
    gm.posWell10 = (22, 25)
    gm.well_positions = (
        gm.posWell1, gm.posWell2, gm.posWell3, gm.posWell4, gm.posWell5,
        gm.posWell6, gm.posWell7, gm.posWell8, gm.posWell9, gm.posWell10,
    )