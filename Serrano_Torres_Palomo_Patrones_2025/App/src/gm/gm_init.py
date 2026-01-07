import pygame as pg
import pathlib
import os
from collections import deque
from settings import *
from utils.app_paths import APP_DIR


def init_pygame(gm):
    """Initialize pygame surfaces, clock and camera on the given GameManager.

    The function configures the display surface, clock and basic camera
    attributes required by the game loop.
    """
    pg.init()
    gm.screen = pg.display.set_mode(RESOLUTION)
    try:
        pg.display.set_caption("Number Tycoon")
    except Exception:
        pass
    gm.clock = pg.time.Clock()
    gm.delta_time = 1
    gm.camera = pg.Vector2(0, 0)
    gm.camera_speed = 400

def init_paths(gm):
    """Set save directory and save file attributes on the GameManager instance.

    The save directory is ``<project_root>/saves`` and the save file is
    ``map.json`` inside that folder.
    """
    # Place saves next to the executable (APP_DIR) so when running a bundled
    # executable the saves live beside the binary. When running from source
    # APP_DIR resolves to the project root (App/).
    gm.save_dir = pathlib.Path(APP_DIR) / "saves"
    gm.save_file = gm.save_dir / "map.json"

def init_ui(gm):
    """Create button rects and layout-related UI constants on the GameManager.

    The positions are set relative to the global ``WIDTH`` constant from
    settings.
    """
    btn_width = 200
    right_margin = 20
    top_margin = 14
    v_spacing = 56
    gm.save_button_rect = pg.Rect(WIDTH - btn_width - right_margin, top_margin, btn_width, 40)
    gm.speed_button_rect = pg.Rect(WIDTH - btn_width - right_margin, top_margin + v_spacing, btn_width, 40)
    gm.eff_button_rect = pg.Rect(WIDTH - btn_width - right_margin, top_margin + v_spacing * 2, btn_width, 40)
    gm.new_mine_button_rect = pg.Rect(WIDTH - btn_width - right_margin, top_margin + v_spacing * 3, btn_width, 40)

def init_counters(gm):
    """Initialize counters, cost tables and the action buffer on the GameManager.

    This sets default values for upgrade counters, cost tables and the
    optional GIF ordering used by the HUD.
    """
    gm.speed_uses_left = 10
    gm.eff_uses_left = 10
    gm.speed_uses_used = 0
    gm.eff_uses_used = 0
    gm.mine_uses_left = None
    gm.mine_uses_used = 0

    gm.mine_costs = (10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
    gm.speed_costs = (10, 12, 24, 48, 96, 192, 384, 768, 1500, 3000)
    gm.eff_costs = (70, 100, 500, 800, 1000, 1600, 3200, 6400, 12000, 15000)

    gm.well_objectives = (30, 50, 100, 200, 500, 800, 1200, 1600, 2000, 5000)

    gm.build_costs = {
        'sum': 15,
        'mul': 45,
        'div': 35,  # Not implemented
        'splitter': 10,
        'merger': 10,
        'conveyor': 2,
    }

    gm.action_buffer = deque()
    # Optional explicit ordering of GIFs to show on a new game. Each entry is
    # (filename, title). If empty, HUD enumerates Assets/gifs alphabetically.
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
    """Define default well grid coordinates and set ``gm.well_positions``.

    The positions are stored individually (posWell1..posWell10) and as a
    tuple ``gm.well_positions`` for convenient iteration elsewhere in the
    codebase.
    """
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