"""Helper functions for conveyor-building state.

This module contains the extracted logic used by `ConveyorBuildState` so
the heavy click/update/draw code is isolated for clarity and testing.
The helpers operate on a `state` object that matches the fields used in
the original state class.
"""

import pygame as pg
from settings import CELL_SIZE_PX, WIDTH, HEIGHT


def handle_click_event(state, event):
    """Handle click logic extracted from ConveyorBuildState.handleClickEvent.

    Operates on the provided `state` object (the ConveyorBuildState
    instance) to avoid duplicating state and to keep the public class
    interface unchanged.
    """
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
        cam = getattr(state.gameManager, 'camera', pg.Vector2(0, 0))
        world_x = int(state.mouse.position.x + cam.x)
        world_y = int(state.mouse.position.y + cam.y)

        grid_x = world_x // CELL_SIZE_PX
        grid_y = world_y // CELL_SIZE_PX
        pixel_x = grid_x * CELL_SIZE_PX + CELL_SIZE_PX // 2
        pixel_y = grid_y * CELL_SIZE_PX + CELL_SIZE_PX // 2
        click_pos = pg.Vector2(pixel_x, pixel_y)

        map_obj = getattr(state.gameManager, 'map', None)
        if map_obj is None or not (0 <= grid_x < getattr(map_obj, 'width', 0) and 0 <= grid_y < getattr(map_obj, 'height', 0)):
            # Cancel mid-placement if out of bounds
            if getattr(state, 'start_pos', None) is not None:
                state.start_pos = None
            print(f"Click at ({grid_x},{grid_y}) is outside map bounds - ignoring placement click")
            return

        if getattr(state, 'start_pos', None) is None:
            structure_at_start = get_structure_at_grid(state, grid_x, grid_y)
            if structure_at_start:
                structure_type = structure_at_start.__class__.__name__.lower()
                if 'well' in structure_type:
                    print("Cannot start conveyor from a Well")
                    return

            state.start_pos = click_pos
            state.start_grid = (grid_x, grid_y)
            print(f"Conveyor start point set at grid ({grid_x}, {grid_y})")
        else:
            structure_at_end = get_structure_at_grid(state, grid_x, grid_y)
            if structure_at_end:
                structure_type = structure_at_end.__class__.__name__.lower()
                if 'mine' in structure_type:
                    print("Cannot end conveyor at a Mine")
                    state.start_pos = None
                    return

            end_pos = click_pos
            if state.start_pos.x == end_pos.x and state.start_pos.y == end_pos.y:
                print("Cannot create conveyor: start and end points are the same")
                state.start_pos = None
                return

            try:
                costs_map = getattr(state.gameManager, 'build_costs', {}) or {}
                cost = int(costs_map.get('conveyor', state.conveyorCreator.getCost()))
            except Exception:
                cost = state.conveyorCreator.getCost()

            if getattr(state.gameManager, 'points', 0) >= cost:
                conveyor = state.conveyorCreator.createStructure(state.start_pos, state.gameManager, end_pos)
                if not hasattr(state.gameManager, 'conveyors'):
                    state.gameManager.conveyors = []
                state.gameManager.conveyors.append(conveyor)

                if not hasattr(state.gameManager, 'structures'):
                    state.gameManager.structures = []
                state.gameManager.structures.append(conveyor)

                try:
                    state.gameManager.points -= cost
                except Exception:
                    pass

                if hasattr(state.gameManager, '_reconnect_structures'):
                    state.gameManager._reconnect_structures()

                print(f"Conveyor built from grid ({grid_x}, {grid_y}) to previous point | Cost: {cost} pts")

                state.start_pos = None
                try:
                    if hasattr(state.gameManager, 'hud') and getattr(state.gameManager, 'hud'):
                        try:
                            state.gameManager.hud.shop_mode = None
                            state.gameManager.hud._setup_buttons()
                        except Exception:
                            pass
                except Exception:
                    pass
                if hasattr(state.gameManager, 'normalState'):
                    state.gameManager.setState(state.gameManager.normalState)
            else:
                print(f"Not enough points to build conveyor (need {cost}, have {getattr(state.gameManager, 'points', 0)})")
                state.start_pos = None

    elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
        # Cancel placement
        state.start_pos = None
        try:
            if hasattr(state.gameManager, 'hud') and getattr(state.gameManager, 'hud'):
                try:
                    state.gameManager.hud.shop_mode = None
                    state.gameManager.hud._setup_buttons()
                except Exception:
                    pass
        except Exception:
            pass
        if hasattr(state.gameManager, 'normalState'):
            state.gameManager.setState(state.gameManager.normalState)


def update(state):
    cam = getattr(state.gameManager, 'camera', pg.Vector2(0, 0))
    world_x = int(state.mouse.position.x + cam.x)
    world_y = int(state.mouse.position.y + cam.y)

    grid_x = world_x // CELL_SIZE_PX
    grid_y = world_y // CELL_SIZE_PX
    pixel_x = grid_x * CELL_SIZE_PX + CELL_SIZE_PX // 2
    pixel_y = grid_y * CELL_SIZE_PX + CELL_SIZE_PX // 2
    state.current_mouse_pos = pg.Vector2(pixel_x, pixel_y)


def draw(state):
    try:
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((60, 140, 220, 70))
        state.gameManager.screen.blit(overlay, (0, 0))
    except Exception:
        pass

    if getattr(state, 'start_pos', None) and getattr(state, 'current_mouse_pos', None):
        cam = getattr(state.gameManager, 'camera', pg.Vector2(0, 0))

        start_screen = (
            int(state.start_pos.x - cam.x),
            int(state.start_pos.y - cam.y)
        )
        end_screen = (
            int(state.current_mouse_pos.x - cam.x),
            int(state.current_mouse_pos.y - cam.y)
        )

        color = state.conveyorCreator.getSpritePreview()
        pg.draw.line(state.gameManager.screen, color, start_screen, end_screen, 4)
        pg.draw.circle(state.gameManager.screen, (100, 200, 100), start_screen, 8)
        pg.draw.circle(state.gameManager.screen, color, end_screen, 6)


def get_structure_at_grid(state, grid_x, grid_y):
    try:
        map_obj = getattr(state.gameManager, 'map', None)
        if map_obj:
            cell = map_obj.getCell(grid_x, grid_y)
            if cell:
                return cell.getStructure()
    except Exception:
        pass
    return None
