import pygame as pg
from settings import *
from ui.hud import Colors


def draw(gm):
    # Fondo con color de la paleta pastel
    gm.screen.fill(Colors.BG_DARK)
    
    cam = getattr(gm, 'camera', pg.Vector2(0, 0))
    # obtener la posicion del raton en pantalla y en mundo
    screen_mouse = pg.mouse.get_pos()
    world_mx = int(gm.mouse.position.x + cam.x)
    world_my = int(gm.mouse.position.y + cam.y)
    gx = world_mx // CELL_SIZE_PX
    gy = world_my // CELL_SIZE_PX

    # Grid con colores pastel
    grid_color = Colors.GRID_LINE
    hover_fill = Colors.GRID_HOVER

    # PRIMERA CAPA: Grid de fondo y conveyors
    for y in range(gm.map.height):
        for x in range(gm.map.width):
            rect_x = x * CELL_SIZE_PX - cam.x
            rect_y = y * CELL_SIZE_PX - cam.y
            rect = pg.Rect(rect_x, rect_y, CELL_SIZE_PX, CELL_SIZE_PX)
            
            # Grid lines (fondo)
            pg.draw.rect(gm.screen, grid_color, rect, 1)

    # Dibujar conveyors (deben ir por detrás de estructuras)
    try:
        for conveyor in gm.conveyors:
            conveyor.draw()
    except Exception:
        pass

    # También dibujar estructuras que no están en el grid pero que sean conveyors
    for structure in gm.structures:
        if hasattr(structure, 'grid_position'):
            continue
        # Solo dibujar si es un conveyor en esta primera pasada
        if structure.__class__.__name__ == 'Conveyor':
            try:
                structure.draw()
            except Exception:
                pass

    # SEGUNDA CAPA: Hover effect y estructuras del mapa (por encima de conveyors y grid)
    for y in range(gm.map.height):
        for x in range(gm.map.width):
            rect_x = x * CELL_SIZE_PX - cam.x
            rect_y = y * CELL_SIZE_PX - cam.y
            rect = pg.Rect(rect_x, rect_y, CELL_SIZE_PX, CELL_SIZE_PX)
            
            # Hover effect: no dibujar el hover si el ratón está sobre la UI
            over_ui = False
            try:
                if hasattr(gm, 'hud') and gm.hud:
                    over_ui = gm.hud.is_over_button(screen_mouse)
            except Exception:
                over_ui = False

            if not over_ui and x == gx and y == gy and 0 <= x < gm.map.width and 0 <= y < gm.map.height:
                pg.draw.rect(gm.screen, hover_fill, rect)

            # Structures (minas, pozos, splitters, mergers, etc.)
            cell = gm.map.getCell(x, y)
            if cell and not cell.isEmpty():
                try:
                    cell.structure.draw()
                except Exception:
                    pass

    # TERCERA CAPA: Dibujar estructuras que no están en el grid (EXCEPTO conveyors)
    for structure in gm.structures:
        if hasattr(structure, 'grid_position'):
            continue
        # No dibujar conveyors aquí, ya se dibujaron en la primera capa
        if structure.__class__.__name__ != 'Conveyor':
            try:
                structure.draw()
            except Exception:
                pass

    # Dibujar HUD (reemplaza toda la UI antigua)
    try:
        if hasattr(gm, 'hud') and gm.hud:
            mouse_pos = pg.mouse.get_pos()
            gm.hud.draw(gm.screen, mouse_pos)
    except Exception as e:
        print(f"Error drawing HUD: {e}")
        # Fallback: dibujar puntos básico si HUD falla
        try:
            font = pg.font.Font(None, 36)
            points_text = font.render(f"Puntuación: {getattr(gm, 'points', 0)}", True, Colors.TEXT_ACCENT)
            gm.screen.blit(points_text, (10, HEIGHT - 40))
        except:
            pass

    # Dibujar cursor y preview de estructura si estamos en modo build
    try:
        # esto dibuja la preview del build en caso de que estemos en modo build
        if hasattr(gm.state, "draw"):
            gm.state.draw()
        gm.mouse.draw()
    except:
        pass

    # Flip display
    pg.display.flip()
