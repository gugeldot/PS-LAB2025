"""Update loop helpers for GameManager.

This module implements the detailed steps executed each frame by the
GameManager update loop. The public entrypoint is :func:`update` which
orchestrates input, camera, world updates, production and HUD updates.
"""

import pygame as pg
from settings import *
from .gm_upgrades import process_action_buffer


def _handle_input_and_state(gm):
    """Process input and forward to the current game state.

    This updates the mouse helper and invokes the active state's update
    callback.
    """
    gm.mouse.update()
    gm.state.update()


def _process_action_buffer(gm):
    """Safely process queued upgrade actions using gm_upgrades helpers.

    Exceptions from the processing are ignored to keep the main loop
    robust.
    """
    try:
        process_action_buffer(gm)
    except Exception:
        pass


def _handle_camera(gm):
    """Update camera position according to keyboard input.

    The function handles WASD and arrow keys and clamps the camera within a
    margin around the map bounds.
    """
    try:
        keys = pg.key.get_pressed()
        if keys[pg.K_w] or keys[pg.K_UP]:
            gm.camera.y = max(0, gm.camera.y - gm.camera_speed * (gm.delta_time / 1000.0))
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            CAMERA_MARGIN = 350
            base_max_y = max(0, gm.map.height * CELL_SIZE_PX - HEIGHT)
            max_y = base_max_y + CAMERA_MARGIN
            min_y = -CAMERA_MARGIN
            gm.camera.y = min(max_y, gm.camera.y + gm.camera_speed * (gm.delta_time / 1000.0))
            gm.camera.y = max(min_y, gm.camera.y)
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            CAMERA_MARGIN = 350
            min_x = -CAMERA_MARGIN
            gm.camera.x = max(min_x, gm.camera.x - gm.camera_speed * (gm.delta_time / 1000.0))
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            CAMERA_MARGIN = 350
            base_max_x = max(0, gm.map.width * CELL_SIZE_PX - WIDTH)
            max_x = base_max_x + CAMERA_MARGIN
            gm.camera.x = min(max_x, gm.camera.x + gm.camera_speed * (gm.delta_time / 1000.0))
            try:
                gm.camera.x = max(-CAMERA_MARGIN, gm.camera.x)
            except Exception:
                pass
    except Exception:
        pass


def _update_world(gm):
    """Update map and conveyors when the tutorial is not paused."""
    if not getattr(gm, '_tutorial_paused', False):
        try:
            gm.map.update()
        except Exception:
            pass

        for conv in getattr(gm, 'conveyors', []):
            try:
                conv.update()
            except Exception:
                pass


def _handle_production(gm):
    """Advance production timers and trigger Mine production when due."""
    if not hasattr(gm, '_base_production_interval'):
        gm._base_production_interval = 2000
    if not hasattr(gm, 'production_interval'):
        gm.production_interval = int(gm._base_production_interval)

    gm.production_timer += gm.delta_time
    prod_int = int(getattr(gm, 'production_interval', getattr(gm, '_base_production_interval', 2000)))
    if gm.production_timer > prod_int:
        structures = getattr(gm, 'structures', [])
        for struct in structures:
            if struct.__class__.__name__ == 'Mine':
                if hasattr(struct, 'outputConveyor') and struct.outputConveyor:
                    try:
                        struct.produce(struct.outputConveyor)
                    except Exception:
                        pass
        gm.production_timer = 0


def _process_operation_modules(gm):
    """Process operation modules (Sum/Mul) when their inputs are ready.

    When both input conveyors are ready and an output conveyor exists the
    module's ``calcular()`` method is invoked.
    """
    structures = getattr(gm, 'structures', [])
    for struct in structures:
        struct_type = struct.__class__.__name__
        if struct_type in ['SumModule', 'MulModule']:
            if hasattr(struct, 'inConveyor1') and hasattr(struct, 'inConveyor2'):
                conv1 = struct.inConveyor1
                conv2 = struct.inConveyor2
                if (conv1 and conv2 and 
                    hasattr(conv1, 'isReady') and hasattr(conv2, 'isReady') and
                    conv1.isReady() and conv2.isReady() and
                    hasattr(struct, 'outConveyor') and struct.outConveyor):
                    try:
                        struct.calcular()
                    except Exception as e:
                        print(f"Error in {struct_type}.calcular(): {e}")


def _tick_and_caption(gm):
    """Advance clock and update window caption."""
    gm.delta_time = gm.clock.tick(FPS)
    try:
        pg.display.set_caption("Number Tycoon")
    except Exception:
        pass


def _update_hud(gm):
    """Update the HUD if present, swallowing errors to keep the loop robust."""
    try:
        if hasattr(gm, 'hud') and gm.hud:
            try:
                gm.hud.update(gm.delta_time)
            except Exception:
                pass
    except Exception:
        pass


def update(gm):
    _handle_input_and_state(gm)
    _process_action_buffer(gm)
    _handle_camera(gm)
    _update_world(gm)
    _handle_production(gm)
    _process_operation_modules(gm)
    _tick_and_caption(gm)
    _update_hud(gm)
