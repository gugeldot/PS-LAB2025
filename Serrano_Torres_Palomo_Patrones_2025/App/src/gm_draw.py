import pygame as pg
from settings import *


def draw(gm):
    gm.screen.fill('black')
    cam = getattr(gm, 'camera', pg.Vector2(0, 0))
    world_mx = int(gm.mouse.position.x + cam.x)
    world_my = int(gm.mouse.position.y + cam.y)
    gx = world_mx // CELL_SIZE_PX
    gy = world_my // CELL_SIZE_PX

    grid_color = (80, 80, 80)
    hover_fill = (200, 200, 200)

    for y in range(gm.map.height):
        for x in range(gm.map.width):
            rect_x = x * CELL_SIZE_PX - cam.x
            rect_y = y * CELL_SIZE_PX - cam.y
            rect = pg.Rect(rect_x, rect_y, CELL_SIZE_PX, CELL_SIZE_PX)
            if x == gx and y == gy and 0 <= x < gm.map.width and 0 <= y < gm.map.height:
                pg.draw.rect(gm.screen, hover_fill, rect)
            pg.draw.rect(gm.screen, grid_color, rect, 1)

            cell = gm.map.getCell(x, y)
            if cell and not cell.isEmpty():
                try:
                    cell.structure.draw()
                except Exception:
                    pass

    for structure in gm.structures:
        if hasattr(structure, 'grid_position'):
            continue
        try:
            structure.draw()
        except Exception:
            pass

    mouse_pt = (int(gm.mouse.position.x), int(gm.mouse.position.y))
    hover = gm.save_button_rect.collidepoint(mouse_pt)
    btn_color = (100, 100, 100) if not hover else (150, 150, 150)
    pg.draw.rect(gm.screen, btn_color, gm.save_button_rect)
    font = pg.font.Font(None, 24)
    text = font.render("Save & Exit", True, (255, 255, 255))
    text_rect = text.get_rect(center=gm.save_button_rect.center)
    gm.screen.blit(text, text_rect)

    # points label
    try:
        font = pg.font.Font(None, 36)
        points_text = font.render(f"Puntuación: {gm.points}", True, (255, 215, 0))
        padding = 8
        text_rect = points_text.get_rect()
        label_x = 10
        label_y = HEIGHT - text_rect.height - 10
        bg_rect = pg.Rect(label_x - padding, label_y - padding,
                          text_rect.width + padding * 2, text_rect.height + padding * 2)
        pg.draw.rect(gm.screen, (30, 30, 30), bg_rect)
        pg.draw.rect(gm.screen, (180, 180, 180), bg_rect, 1)
        gm.screen.blit(points_text, (label_x, label_y))
    except Exception:
        try:
            font = pg.font.Font(None, 20)
            points_text = font.render(str(getattr(gm, 'points', 0)), True, (255, 215, 0))
            gm.screen.blit(points_text, (10, HEIGHT - 30))
        except Exception:
            pass

    font_small = pg.font.Font(None, 20)

    hover_speed = gm.speed_button_rect.collidepoint(mouse_pt)
    next_speed_cost = None
    try:
        if 0 <= gm.speed_uses_used < len(gm.speed_costs):
            next_speed_cost = int(gm.speed_costs[gm.speed_uses_used])
    except Exception:
        next_speed_cost = None

    can_buy_speed = (getattr(gm, 'points', 0) >= (next_speed_cost or 0)) and (gm.speed_uses_left > 0)
    if not can_buy_speed:
        speed_color = (60, 60, 60)
    else:
        speed_color = (150, 150, 150) if hover_speed else (100, 100, 100)
    pg.draw.rect(gm.screen, speed_color, gm.speed_button_rect)
    speed_label_cost = f"{next_speed_cost}pts" if next_speed_cost is not None else "N/A"
    text_speed = font_small.render(f"Mejora Velocidad ({speed_label_cost}) [{gm.speed_uses_left}]", True, (255, 255, 255))
    gm.screen.blit(text_speed, text_speed.get_rect(center=gm.speed_button_rect.center))

    hover_eff = gm.eff_button_rect.collidepoint(mouse_pt)
    next_eff_cost = None
    try:
        if 0 <= gm.eff_uses_used < len(gm.eff_costs):
            next_eff_cost = int(gm.eff_costs[gm.eff_uses_used])
    except Exception:
        next_eff_cost = None

    can_buy_eff = (getattr(gm, 'points', 0) >= (next_eff_cost or 0)) and (gm.eff_uses_left > 0)
    if not can_buy_eff:
        eff_color = (60, 60, 60)
    else:
        eff_color = (150, 150, 150) if hover_eff else (100, 100, 100)
    pg.draw.rect(gm.screen, eff_color, gm.eff_button_rect)
    eff_label_cost = f"{next_eff_cost}pts" if next_eff_cost is not None else "N/A"
    text_eff = font_small.render(f"Mejora Eficiencia ({eff_label_cost}) [{gm.eff_uses_left}]", True, (255, 255, 255))
    gm.screen.blit(text_eff, text_eff.get_rect(center=gm.eff_button_rect.center))

    hover_new_mine = gm.new_mine_button_rect.collidepoint(mouse_pt)
    next_mine_cost = None
    try:
        if 0 <= gm.mine_uses_used < len(gm.mine_costs):
            next_mine_cost = int(gm.mine_costs[gm.mine_uses_used])
    except Exception:
        next_mine_cost = None

    can_buy_mine = (getattr(gm, 'points', 0) >= (next_mine_cost or 0)) and (gm.mine_uses_left > 0)
    if not can_buy_mine:
        new_mine_color = (60, 60, 60)
    else:
        new_mine_color = (150, 150, 150) if hover_new_mine else (100, 100, 100)
    pg.draw.rect(gm.screen, new_mine_color, gm.new_mine_button_rect)
    mine_label_cost = f"{next_mine_cost}pts" if next_mine_cost is not None else "N/A"
    text_new = font_small.render(f"Nueva Mina ({mine_label_cost}) [{gm.mine_uses_left}]", True, (255, 255, 255))
    gm.screen.blit(text_new, text_new.get_rect(center=gm.new_mine_button_rect.center))

    try:
        msg = getattr(gm, '_popup_message', None)
        t = getattr(gm, '_popup_timer', None)
        if msg and t and t > 0:
            popup_font = pg.font.Font(None, 26)
            text_surf = popup_font.render(msg, True, (0, 0, 0))
            padding_x = 16
            padding_y = 10
            w = text_surf.get_width() + padding_x * 2
            h = text_surf.get_height() + padding_y * 2
            px = WIDTH // 2 - w // 2
            py = 10
            popup_rect = pg.Rect(px, py, w, h)
            pg.draw.rect(gm.screen, (250, 240, 120), popup_rect)
            pg.draw.rect(gm.screen, (120, 120, 120), popup_rect, 2)
            tx = px + (w - text_surf.get_width()) // 2
            ty = py + (h - text_surf.get_height()) // 2
            gm.screen.blit(text_surf, (tx, ty))
    except Exception:
        pass

    gm.mouse.draw()
    pg.display.flip()
